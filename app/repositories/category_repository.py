from sqlalchemy.orm import Session
from app.models.category import Category
from sqlalchemy import select

def get_category_by_id(db: Session,
                       category_id: int):
    return db.scalar(select(Category).where(Category.id == category_id))

def get_category_by_name(db: Session,
                         name: str):
    return db.scalar(select(Category).where(Category.name == name))

def get_categories(db: Session):
    return db.scalars(select(Category).order_by(Category.id.desc())).all()