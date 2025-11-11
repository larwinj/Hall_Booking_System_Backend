from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from datetime import datetime, timezone
from app.api.deps import require_role
from app.models.enums import UserRole
from app.schemas.cms import CMSBase, CMSUpdate
from app.utils.cms_sanitize import sanitize_html
from app.utils.mongo_utils import bson_to_json
from app.core.config import get_settings

router = APIRouter(prefix="/cms", tags=["cms"])

def _col(request: Request):
    """Get MongoDB collection with proper client initialization."""
    client = request.app.state.mongo
    if not client:
        raise HTTPException(
            status_code=503,
            detail="Database connection not available"
        )
    return client.get_database('hall_cms').get_collection('cms_pages')

@router.post("/", response_model=CMSBase,description="Access by only admin users.")
async def create_page(payload: CMSBase, request: Request, _: str = Depends(require_role(UserRole.admin))):
    col = _col(request)
    doc = payload.model_dump(exclude={"id"})  # Exclude id if present in payload
    doc["html_content"] = sanitize_html(doc["html_content"])
    now = datetime.now(timezone.utc)
    doc["created_at"] = now
    doc["updated_at"] = now
    existing = await col.find_one({"slug": payload.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    result = await col.insert_one(doc)
    # Get the complete document back
    created_doc = await col.find_one({"_id": result.inserted_id})
    if not created_doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve created document")
    # Convert ensuring ID is handled
    converted = bson_to_json(created_doc)
    if "_id" in created_doc and converted.get("id") is None:
        converted["id"] = str(created_doc["_id"])
    return CMSBase(**converted)

@router.get("/", response_model=list[CMSBase],description="Access by only admin users.")
async def list_pages(request: Request):
    col = _col(request)
    pages = []
    async for doc in col.find({}):
        # Ensure _id is properly handled
        converted = bson_to_json(doc)
        if "_id" in doc and converted.get("id") is None:
            converted["id"] = str(doc["_id"])
        pages.append(CMSBase(**converted))
    return pages

@router.get("/slug/{slug}", response_model=CMSBase,description="Access by only admin users.")
async def get_page(slug: str, request: Request):
    col = _col(request)
    doc = await col.find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Page not found")
    # Ensure _id is properly handled
    converted = bson_to_json(doc)
    if "_id" in doc and converted.get("id") is None:
        converted["id"] = str(doc["_id"])
    return CMSBase(**converted)

@router.patch("/slug/{slug}", response_model=CMSBase,description="Access by only admin users.")
async def update_page(slug: str, payload: CMSUpdate, request: Request, _: str = Depends(require_role(UserRole.admin))):
    col = _col(request)
    update = payload.model_dump(exclude_unset=True)
    if "html_content" in update and update["html_content"] is not None:
        update["html_content"] = sanitize_html(update["html_content"])
    update["updated_at"] = datetime.now(timezone.utc)
    
    res = await col.find_one_and_update(
        {"slug": slug}, 
        {"$set": update}, 
        return_document=ReturnDocument.AFTER
    )
    if not res:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Convert ensuring ID is handled
    converted = bson_to_json(res)
    if "_id" in res and converted.get("id") is None:
        converted["id"] = str(res["_id"])
    return CMSBase(**converted)

@router.delete("/slug/{slug}",description="Access by only admin users.")
async def delete_page(slug: str, request: Request, _: str = Depends(require_role(UserRole.admin))):
    col = _col(request)
    res = await col.delete_one({"slug": slug})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"success": True}
