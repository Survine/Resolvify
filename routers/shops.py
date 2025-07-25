from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas

from permissions import shop_read, shop_create, shop_update, shop_delete
from databases.database import get_db

router = APIRouter(prefix="/shops", tags=["shops"])

@router.post("/", response_model=schemas.Shop)
def create_shop(
    shop: schemas.ShopCreate,
    db: Session = Depends(get_db),
    current_employee = Depends(shop_create)
):
    return crud.create_shop(db=db, shop=shop)

@router.get("/", response_model=List[schemas.Shop])
def read_shops(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_employee = Depends(shop_read)
):
    return crud.get_shops(db, skip=skip, limit=limit, company_id=company_id)

@router.get("/{shop_id}", response_model=schemas.Shop)
def read_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(shop_read)
):
    db_shop = crud.get_shop(db, shop_id=shop_id)
    if db_shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    return db_shop

@router.put("/{shop_id}", response_model=schemas.Shop)
def update_shop(
    shop_id: int,
    shop: schemas.ShopUpdate,
    db: Session = Depends(get_db),
    current_employee = Depends(shop_update)
):
    db_shop = crud.update_shop(db, shop_id=shop_id, shop=shop)
    if db_shop is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    return db_shop

@router.delete("/{shop_id}")
def delete_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(shop_delete)
):
    success = crud.delete_shop(db, shop_id=shop_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shop not found")
    return {"message": "Shop deleted successfully"}
