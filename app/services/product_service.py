from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.category import Category
from app.models.product import Product
from app.repositories.product_repository import (create_product,get_product_by_id,
                                                 get_product_by_sku,get_products,)
from app.schemas.product import (ProductCreate,ProductUpdate)

def create_new_product(db: Session,data: ProductCreate):
    # Check SKU
    existing_product = get_product_by_sku(db,data.sku)
    if existing_product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"code": "DUPLICATE_SKU",
                                    "message": f"SKU '{data.sku}' already exists"})
    # Check category
    category = db.scalar(select(Category).where(Category.id == data.category_id))
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CATEGORY_NOT_FOUND",
                    "message": "Category not found",})
    if not category.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CATEGORY_INACTIVE",
                    "message": "Cannot create product under inactive category"})
    product = Product(
        sku=data.sku,
        name=data.name,
        description=data.description,
        category_id=data.category_id,
        price=data.price,
        cost_price=data.cost_price,
        is_active=True)
    return create_product(db,product)

def get_product(db: Session,product_id: int):
    product = get_product_by_id(db,product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": "PRODUCT_NOT_FOUND",
                                    "message": "Product not found"})
    return product

def list_products(
    db: Session,
    skip: int = 0,
    limit: int = 20):
    return get_products(
        db,
        skip=skip,
        limit=limit)

def update_product(db: Session,
                   product_id: int,
                   data: ProductUpdate):
    product = get_product(db,product_id)
    update_data = data.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        category =db.scalar(select(Category).where(Category.id==update_data["category_id"]))
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail={"code": "CATEGORY_NOT_FOUND",
                                        "message": "Category not found"})
        if not category.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": "CATEGORY_INACTIVE",
                                        "message": "Cannot use inactive category"})
    for field, value in update_data.items():
        setattr(product,field,value)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"code": "PRODUCT_UPDATE_FAILED",
                                    "message": "Product update violates a database constraint"})
    return product

def activate_product(db: Session,product_id: int):
    product = get_product(db,product_id)
    product.is_active = True
    db.commit()
    db.refresh(product)
    return product

def deactivate_product(db: Session,product_id: int):
    product = get_product(db,product_id)
    product.is_active = False
    db.commit()
    db.refresh(product)
    return product