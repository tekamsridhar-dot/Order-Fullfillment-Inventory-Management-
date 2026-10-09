from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import (get_category_by_id,
                                                  get_category_by_name,get_categories)
from app.schemas.category import (CategoryCreate,CategoryUpdate)

def create_category(db: Session,data: CategoryCreate):
    existing = get_category_by_name(db,data.name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
            detail={"code": "DUPLICATE_CATEGORY",
                    "message": "Category already exists"})
    category = Category(name=data.name,
                        description=data.description,
                        is_active=True)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def list_categories(db: Session):
    return get_categories(db)

def get_category(db: Session,category_id: int):
    category = get_category_by_id(db,category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": "CATEGORY_NOT_FOUND",
                                    "message": "Category not found",},)
    return category

def update_category(db: Session,
                    category_id: int,
                    data: CategoryUpdate):
    category = get_category(db,category_id)
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = get_category_by_name(db,update_data["name"])
        if existing and existing.id != category.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"code": "DUPLICATE_CATEGORY",
                                        "message": "Category already exists",})
    for field, value in update_data.items():
        setattr(category,field,value)
    db.commit()
    db.refresh(category)
    return category