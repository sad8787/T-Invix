from typing import Annotated\nimport secrets
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db import get_session
from app.models.product import Product
from app.schemas.product import ProductList, ProductRead
from app.storage import storage

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.get("/products", response_model=ProductList)
async def list_products(session: SessionDep, limit: int = 100, offset: int = 0):
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    total = await session.scalar(select(func.count()).select_from(Product)) or 0
    result = await session.scalars(
        select(Product).order_by(Product.created_at.desc(), Product.id.desc()).limit(limit).offset(offset)
    )
    return ProductList(items=list(result.all()), total=total, limit=limit, offset=offset)

@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    session: SessionDep,
    name: Annotated[str, Form(min_length=1, max_length=200)],
    image: Annotated[UploadFile, File()],
    admin_id: Annotated[int, Form()],
):
    # Bot is the only intended writer. Restrict this endpoint to configured Telegram admins.
    if not settings.admin_ids or admin_id not in settings.admin_ids:
        raise HTTPException(status_code=403, detail="Administrator is not authorized")
    clean_name = " ".join(name.split())
    if not clean_name:
        raise HTTPException(status_code=422, detail="Product name is required")
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG and WebP images are allowed")
    content = await image.read(settings.max_upload_bytes + 1)
    if not content:
        raise HTTPException(status_code=422, detail="Image is empty")
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image is too large")
    # Upload first. If DB insert fails, remove the object to avoid orphaned files.
    key = await storage.upload(content, image.content_type)
    product = Product(name=clean_name, image_key=key)
    try:
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product
    except Exception:
        await session.rollback()
        await storage.delete(key)
        raise