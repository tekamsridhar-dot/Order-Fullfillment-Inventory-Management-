from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import require_admin
from app.dependencies import get_db
from app.schemas.category import (CategoryCreate,CategoryResponse,CategoryUpdate)
from app.services.category_service import (create_category,list_categories,
                                           get_category,update_category)

router = APIRouter(prefix="/api/categories",
                   tags=["Categories"])

@router.post("",response_model=CategoryResponse)
def create_category_endpoint(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)):
    return create_category(db,data)

@router.get("",response_model=list[CategoryResponse])
def list_categories_endpoint(db: Session = Depends(get_db)):
    return list_categories(db)

@router.get("/{category_id}",response_model=CategoryResponse)
def get_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db)):
    return get_category(db,category_id)

@router.put("/{category_id}",response_model=CategoryResponse)
def update_category_endpoint(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)):
    return update_category(db,category_id,data)