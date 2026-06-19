from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas


def create_shop(db: Session, shop: schemas.ShopCreate) -> models.Shop:
    db_shop = models.Shop(**shop.model_dump())
    db.add(db_shop)
    db.commit()
    db.refresh(db_shop)
    return db_shop


def get_shop(db: Session, shop_id: int) -> Optional[models.Shop]:
    return db.query(models.Shop).filter(models.Shop.id == shop_id).first()


def get_shops(db: Session, skip: int = 0, limit: int = 100) -> List[models.Shop]:
    return db.query(models.Shop).offset(skip).limit(limit).all()


def update_shop(
    db: Session, shop_id: int, shop: schemas.ShopUpdate
) -> Optional[models.Shop]:
    db_shop = get_shop(db, shop_id)
    if not db_shop:
        return None
    for field, value in shop.model_dump(exclude_unset=True).items():
        setattr(db_shop, field, value)
    db.commit()
    db.refresh(db_shop)
    return db_shop


def delete_shop(db: Session, shop_id: int) -> bool:
    db_shop = get_shop(db, shop_id)
    if not db_shop:
        return False
    db.delete(db_shop)
    db.commit()
    return True
