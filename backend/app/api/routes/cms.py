from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from app.api.deps import require_role
from app.models.enums import UserRole
from app.schemas.cms import CMSBase, CMSUpdate
from app.utils.cms_sanitize import sanitize_html
from app.core.config import get_settings

router = APIRouter(prefix="/cms", tags=["cms"])

def _col():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGO_URI)
    return client.hall_cms.cms_pages

@router.post("/", response_model=CMSBase)
async def create_page(payload: CMSBase, _: str = Depends(require_role(UserRole.admin))):
    col = _col()
    doc = payload.model_dump()
    doc["html_content"] = sanitize_html(doc["html_content"])
    now = datetime.now(timezone.utc)
    doc["created_at"] = now
    doc["updated_at"] = now
    existing = await col.find_one({"slug": payload.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    await col.insert_one(doc)
    return CMSBase(**doc)

@router.get("/", response_model=list[CMSBase])
async def list_pages():
    col = _col()
    pages = []
    async for d in col.find({}):
        pages.append(CMSBase(**d))
    return pages

@router.get("/slug/{slug}", response_model=CMSBase)
async def get_page(slug: str):
    col = _col()
    d = await col.find_one({"slug": slug})
    if not d:
        raise HTTPException(status_code=404, detail="Page not found")
    return CMSBase(**d)

@router.patch("/slug/{slug}", response_model=CMSBase)
async def update_page(slug: str, payload: CMSUpdate, _: str = Depends(require_role(UserRole.admin))):
    col = _col()
    update = payload.model_dump(exclude_unset=True)
    if "html_content" in update and update["html_content"] is not None:
        update["html_content"] = sanitize_html(update["html_content"])
    update["updated_at"] = datetime.now(timezone.utc)
    res = await col.find_one_and_update({"slug": slug}, {"$set": update}, return_document=True)
    if not res:
        raise HTTPException(status_code=404, detail="Page not found")
    return CMSBase(**res)

@router.delete("/slug/{slug}")
async def delete_page(slug: str, _: str = Depends(require_role(UserRole.admin))):
    col = _col()
    res = await col.delete_one({"slug": slug})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"success": True}
