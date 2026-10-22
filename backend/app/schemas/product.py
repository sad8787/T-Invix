from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    image_key: str
    created_at: datetime

class ProductList(BaseModel):
    items: list[ProductRead]
    total: int
    limit: int
    offset: int

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)