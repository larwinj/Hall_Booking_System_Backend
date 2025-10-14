from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import require_role
from app.models.enums import UserRole
from app.models.addon import Addon
from app.schemas.addon import AddonCreate, AddonUpdate, AddonOut

router = APIRouter(prefix="/addons", tags=["addons"])

@router.post("/", response_model=AddonOut)
async def create_addon(payload: AddonCreate, _: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    addon = Addon(**payload.model_dump())
    db.add(addon)
    await db.commit()
    await db.refresh(addon)
    return addon

@router.get("/", response_model=list[AddonOut])
async def list_addons(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Addon))
    return res.scalars().all()

@router.patch("/{addon_id}", response_model=AddonOut)
async def update_addon(addon_id: int, payload: AddonUpdate, _: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    addon = (await db.execute(select(Addon).where(Addon.id == addon_id))).scalar_one_or_none()
    if not addon:
        raise HTTPException(status_code=404, detail="Addon not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(addon, k, v)
    await db.commit()
    await db.refresh(addon)
    return addon

@router.delete("/{addon_id}")
async def delete_addon(addon_id: int, _: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    addon = (await db.execute(select(Addon).where(Addon.id == addon_id))).scalar_one_or_none()
    if not addon:
        raise HTTPException(status_code=404, detail="Addon not found")
    await db.delete(addon)
    await db.commit()
    return {"success": True}
