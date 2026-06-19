from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.dependencies import permission_read, permission_create, permission_update, permission_delete

router = APIRouter(
    prefix="/permissions",
    tags=["permissions"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Permission)
def create_permission(
    permission: schemas.PermissionCreate,
    db: Session = Depends(get_db),
    _=Depends(permission_create),
):
    if crud.get_permission_by_name(db, name=permission.name):
        raise HTTPException(status_code=400, detail="Permission name already exists")
    return crud.create_permission(db=db, permission=permission)


@router.get("/", response_model=List[schemas.Permission])
def list_permissions(
    skip: int = 0,
    limit: int = 100,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(permission_read),
):
    if resource:
        return crud.get_permissions_by_resource(db, resource=resource)
    if action:
        return crud.get_permissions_by_action(db, action=action)
    return crud.get_permissions(db, skip=skip, limit=limit)


@router.get("/{permission_id}", response_model=schemas.Permission)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _=Depends(permission_read),
):
    perm = crud.get_permission(db, permission_id=permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return perm


@router.put("/{permission_id}", response_model=schemas.Permission)
def update_permission(
    permission_id: int,
    permission: schemas.PermissionCreate,
    db: Session = Depends(get_db),
    _=Depends(permission_update),
):
    existing = crud.get_permission(db, permission_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Permission not found")
    if permission.name != existing.name and crud.get_permission_by_name(db, permission.name):
        raise HTTPException(status_code=400, detail="Permission name already exists")
    return crud.update_permission(db=db, permission_id=permission_id, data=permission)


@router.delete("/{permission_id}", response_model=schemas.Permission)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _=Depends(permission_delete),
):
    perm = crud.get_permission(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return crud.delete_permission(db=db, permission_id=permission_id)
