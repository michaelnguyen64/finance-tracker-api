from pydantic import BaseModel

from app.models.category import CategoryType


class CategoryCreate(BaseModel):
    name: str
    type: CategoryType


class CategoryUpdate(BaseModel):
    name: str | None = None
    type: CategoryType | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: CategoryType
    user_id: int

    model_config = {"from_attributes": True}
