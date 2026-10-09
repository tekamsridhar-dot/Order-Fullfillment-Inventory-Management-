from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.auth import (require_admin)
from app.dependencies import get_db
from app.schemas.product import (ProductCreate,ProductResponse,ProductUpdate)
from app.services.product_service import (create_new_product,get_product,list_products,
                                          update_product,activate_product,deactivate_product)

router = APIRouter(prefix="/api/products",
                   tags=["Products"])

@router.post("",response_model=ProductResponse)
def create_product_endpoint(data: ProductCreate,
                            db: Session = Depends(get_db),
                            current_user=Depends(require_admin)):
    return create_new_product(db,data)

@router.get("",response_model=list[ProductResponse])
def list_products_endpoint(page: int = Query(default=1,ge=1),
    page_size: int = Query(default=20,ge=1,le=100),
    db: Session = Depends(get_db)):
    skip = (page - 1) * page_size
    return list_products(db,skip=skip,limit=page_size)

@router.get("/{product_id}",response_model=ProductResponse)
def get_product_endpoint(product_id: int,
                         db: Session = Depends(get_db)):
    return get_product(db,product_id)

@router.put("/{product_id}",response_model=ProductResponse)
def update_product_endpoint(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)):

    return update_product(db,product_id,data)

@router.patch("/{product_id}/activate",
              response_model=ProductResponse)
def activate_product_endpoint(product_id: int,
                              db: Session = Depends(get_db),
                              current_user=Depends(require_admin)):
    return activate_product(db,product_id)

@router.patch("/{product_id}/deactivate",
              response_model=ProductResponse)
def deactivate_product_endpoint(product_id: int,
                                db: Session = Depends(get_db),
                                current_user=Depends(require_admin)):
    return deactivate_product(db,product_id)