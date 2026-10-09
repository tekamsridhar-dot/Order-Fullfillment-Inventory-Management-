from sqlalchemy.orm import Session
from app.models.product import Product
from sqlalchemy import select

def get_product_by_id(db: Session,product_id: int):
    return db.scalar(select(Product).where(Product.id == product_id))


def get_product_by_sku(db: Session,sku: str):
    return db.scalar(select(Product).where(Product.sku == sku))

def get_products(db: Session,
                 skip: int = 0,
                 limit: int = 20):
    return db.scalars(select(Product).order_by(Product.id.desc()).offset(skip).limit(limit)).all()

def create_product(db: Session,product: Product):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session,
                   product: Product):
    db.delete(product)
    db.commit()