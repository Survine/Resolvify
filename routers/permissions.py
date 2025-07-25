from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import schemas
import crud
from databases.database import get_db

router = APIRouter(
    prefix="/permissions",
    tags=["permissions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Permission)
def create_new_permission(permission: schemas.PermissionCreate, db: Session = Depends(get_db)):
    db_permission = crud.get_permission_by_name(db, name=permission.name)
    if db_permission:
        raise HTTPException(status_code=400, detail="Permission name already exists")
    return crud.create_permission(db=db, permission=permission)

@router.get("/", response_model=List[schemas.Permission])
def read_permissions(
    skip: int = 0, 
    limit: int = 100,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if resource:
        return crud.get_permissions_by_resource(db, resource=resource)
    if action:
        return crud.get_permissions_by_action(db, action=action)
    return crud.get_permissions(db, skip=skip, limit=limit)

@router.get("/{permission_id}", response_model=schemas.Permission)
def read_permission(permission_id: int, db: Session = Depends(get_db)):
    db_permission = crud.get_permission(db, permission_id=permission_id)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    return db_permission

@router.put("/{permission_id}", response_model=schemas.Permission)
def update_existing_permission(
    permission_id: int, 
    permission: schemas.PermissionCreate, 
    db: Session = Depends(get_db)
):
    db_permission = crud.get_permission(db, permission_id=permission_id)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Check if name is being changed to an existing name
    if permission.name != db_permission.name:
        existing_permission = crud.get_permission_by_name(db, name=permission.name)
        if existing_permission:
            raise HTTPException(status_code=400, detail="Permission name already exists")
    
    return crud.update_permission(db=db, permission_id=permission_id, permission_data=permission)

@router.delete("/{permission_id}", response_model=schemas.Permission)
def delete_existing_permission(permission_id: int, db: Session = Depends(get_db)):
    db_permission = crud.get_permission(db, permission_id=permission_id)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    return crud.delete_permission(db=db, permission_id=permission_id)