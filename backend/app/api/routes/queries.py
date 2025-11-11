from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models.enums import UserRole
from app.models.query import Query as QueryModel
from app.schemas.query import QueryCreate, QueryUpdate, QueryOut

router = APIRouter(prefix="/queries", tags=["queries"])

@router.post("/", response_model=QueryOut,description="Access by customers,moderators")
async def create_query(payload: QueryCreate, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = QueryModel(user_id=user.id, subject=payload.subject, message=payload.message)
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q

@router.get("/", response_model=list[QueryOut],description="Access by customers,moderators,admins")
async def list_queries(_: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(QueryModel))
    return res.scalars().all()

@router.patch("/{query_id}", response_model=QueryOut,description="Access by customers")
async def update_query(query_id: int, payload: QueryUpdate, _: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    q = (await db.execute(select(QueryModel).where(QueryModel.id == query_id))).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Query not found")
    q.status = payload.status
    await db.commit()
    await db.refresh(q)
    return q

@router.delete("/delete",description="Access by moderators,admins")
async def delete_Query(query_id: int, _: str = Depends(require_role(UserRole.admin)), db: AsyncSession = Depends(get_db)):
    cur_query = (await db.execute(select(QueryModel).where(QueryModel.id == query_id))).scalar_one_or_none()
    if not cur_query:
        raise HTTPException(status_code=404, detail="Query not found")
    await db.delete(cur_query)
    await db.commit()
    return {"Message": "Query deleted successfully"}