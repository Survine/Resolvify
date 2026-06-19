from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.dependencies import shop_read, shop_create, shop_update, shop_delete

router = APIRouter(prefix="/shops", tags=["shops"])


@router.post("/", response_model=schemas.Shop)
def create_shop(
    shop: schemas.ShopCreate,
    db: Session = Depends(get_db),
    _=Depends(shop_create),
):
    return crud.create_shop(db=db, shop=shop)


@router.get("/", response_model=List[schemas.Shop])
def list_shops(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(shop_read),
):
    return crud.get_shops(db, skip=skip, limit=limit)


@router.get("/{shop_id}", response_model=schemas.Shop)
def get_shop(shop_id: int, db: Session = Depends(get_db), _=Depends(shop_read)):
    shop = crud.get_shop(db, shop_id=shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


@router.put("/{shop_id}", response_model=schemas.Shop)
def update_shop(
    shop_id: int,
    shop: schemas.ShopUpdate,
    db: Session = Depends(get_db),
    _=Depends(shop_update),
):
    result = crud.update_shop(db, shop_id=shop_id, shop=shop)
    if not result:
        raise HTTPException(status_code=404, detail="Shop not found")
    return result


@router.delete("/{shop_id}")
def delete_shop(shop_id: int, db: Session = Depends(get_db), _=Depends(shop_delete)):
    if not crud.delete_shop(db, shop_id=shop_id):
        raise HTTPException(status_code=404, detail="Shop not found")
    return {"message": "Shop deleted successfully"}
