# app/api/routes/rooms.py
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.enums import UserRole
from app.models.room import Room
from app.models.addon import Addon
from app.schemas.room import RoomAddonCreate, RoomOut
from pydantic import ValidationError
import base64, json
from typing import List, Optional

router = APIRouter(prefix="/rooms", tags=["rooms"])

async def extract_form_list(request: Request, field_name: str) -> List[str]:
    """Helper to extract multiple form field values with the same name"""
    try:
        form = await request.form()
        values = form.getlist(field_name)
        return [v.strip() for v in values if isinstance(v, str) and v.strip()]
    except Exception:
        return []

@router.post("/", response_model=RoomOut, description="Access by moderators,admins")
async def create_room(
    request: Request,
    venue_id: int = Form(..., ge=1),
    name: str = Form(..., min_length=3, max_length=100),
    capacity: int = Form(..., ge=1, le=1000),
    rate_per_hour: float = Form(..., gt=0),
    type: Optional[str] = Form(None),
    description: Optional[str] = Form(None, max_length=500),
    addons: Optional[List[str]] = Form(
        None,
        description='List of addon JSON objects. Example item: {"name":"DJ & Dance Floor Setup","description":"...","price":5000}'
    ),
    images: List[UploadFile] = File(default_factory=list),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role not in [UserRole.moderator, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if user.role == UserRole.moderator and user.assigned_venue_id != venue_id:
        raise HTTPException(
            status_code=403, 
            detail=f"Cannot create room outside assigned venue. Assigned: {user.assigned_venue_id}, Target: {venue_id}"
        )

    # Extract amenities from FormData (handles multiple values with same field name)
    amenities_list = await extract_form_list(request, "amenities")
    
    # Validate amenities
    cleaned_amenities = [item.strip() for item in amenities_list if item.strip()]

    # Validate images
    if len(images) > 4:
        raise HTTPException(400, "Maximum 4 images allowed per room")
    room_images = []
    for image_file in images:
        if image_file.size and image_file.size > 10 * 1024 * 1024:
            raise HTTPException(400, f"Image {image_file.filename} exceeds 10MB limit")
        if not image_file.content_type or not image_file.content_type.startswith("image/"):
            raise HTTPException(400, f"File {image_file.filename} must be an image (jpg, jpeg, png, gif)")
        contents = await image_file.read()
        base64_image = base64.b64encode(contents).decode("utf-8")
        room_images.append(f"data:{image_file.content_type};base64,{base64_image}")

    # Create room
    room = Room(
        venue_id=venue_id,
        name=name,
        capacity=capacity,
        rate_per_hour=rate_per_hour,
        type=type if type else "Party Hall",
        amenities=cleaned_amenities,
        description=description if description else "",
        room_images=room_images,
    )
    db.add(room)
    await db.flush()

    if addons:
        parsed_addons: List[RoomAddonCreate] = []
        for idx, item in enumerate(addons):
            try:
                data = json.loads(item) if isinstance(item, str) else item
                parsed = RoomAddonCreate.model_validate(data)
                parsed_addons.append(parsed)
            except (json.JSONDecodeError, ValidationError) as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid addons[{idx}] value. Expect JSON object with fields of RoomAddonCreate. Error: {str(e)}"
                )
        for addon in parsed_addons:
            db.add(Addon(venue_id=venue_id, room_id=room.id, **addon.model_dump()))

    await db.commit()
    await db.refresh(room)
    return room


@router.get("/", response_model=list[RoomOut], description="Access by everyone")
async def list_rooms(venue_id: int | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Room)
    if venue_id:
        stmt = stmt.where(Room.venue_id == venue_id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/getAll", response_model=list[RoomOut], description="Access by everyone")
async def get_all_rooms(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Room))
    rooms = res.scalars().all()
    return rooms

@router.get("/{room_id}", response_model=RoomOut, description="Access by everyone")
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    room = (await db.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.patch("/{room_id}", response_model=RoomOut, description="Access by moderators,admins")
async def update_room(
    room_id: int,
    request: Request,
    name: str | None = Form(None, min_length=3, max_length=100),
    capacity: int | None = Form(None, ge=1, le=1000),
    rate_per_hour: float | None = Form(None, gt=0),
    type: str | None = Form(None),
    description: str | None = Form(None, max_length=500),
    addons: List[dict] | None = Form(None),
    images: List[UploadFile] | None = File(None),
    user=Depends(get_current_user), 
    db: AsyncSession = Depends(get_db),
):
    room = (await db.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if user.role == UserRole.moderator and user.assigned_venue_id != room.venue_id:
        raise HTTPException(
            status_code=403, 
            detail=f"Cannot update room outside assigned venue. Assigned: {user.assigned_venue_id}, Target: {room.venue_id}"
        )
    
    # Update other fields if provided
    if name is not None:
        room.name = name
    if capacity is not None:
        room.capacity = capacity
    if rate_per_hour is not None:
        room.rate_per_hour = rate_per_hour
    if type is not None:
        room.type = type
    
    # Extract amenities from FormData if provided
    amenities_list = await extract_form_list(request, "amenities")
    if amenities_list:  # Only update if amenities were provided
        cleaned_amenities = [item.strip() for item in amenities_list if item.strip()]
        room.amenities = cleaned_amenities
    
    if description is not None:
        room.description = description if description else ""
    
    # Process new images if provided (replace existing)
    if images is not None and len(images) > 0:
        if len(images) > 4:
            raise HTTPException(400, "Maximum 4 images allowed per room")
        room_images = []
        for image_file in images:
            if image_file.size > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(400, f"Image {image_file.filename} exceeds 10MB limit")
            if not image_file.content_type or not image_file.content_type.startswith('image/'):
                raise HTTPException(400, f"File {image_file.filename} must be an image")
            contents = await image_file.read()
            base64_image = base64.b64encode(contents).decode('utf-8')
            room_images.append(f"data:{image_file.content_type};base64,{base64_image}")
        room.room_images = room_images
    
    # Update addons if provided (this would require more logic for update/create/delete)
    if addons is not None:
        # For simplicity, delete old and create new - implement as needed
        pass  # Placeholder - add logic for addon updates
    
    await db.commit()
    await db.refresh(room)
    return room

@router.delete("/{room_id}", description="Access by moderators,admins")
async def delete_room(room_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role not in [UserRole.moderator, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    room = (await db.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if user.role == UserRole.moderator and user.assigned_venue_id != room.venue_id:
        raise HTTPException(
            status_code=403, 
            detail=f"Cannot delete room outside assigned venue. Assigned: {user.assigned_venue_id}, Target: {room.venue_id}"
        )
    
    # Delete the room
    await db.delete(room)
    await db.commit()
    return {"success": True}