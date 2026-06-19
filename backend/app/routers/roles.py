from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.dependencies import role_read, role_create, role_update, role_delete

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=schemas.Role)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db), _=Depends(role_create)):
    return crud.create_role(db=db, role=role)


@router.get("/", response_model=List[schemas.Role])
def list_roles(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(role_read)
):
    return crud.get_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=schemas.Role)
def get_role(role_id: int, db: Session = Depends(get_db), _=Depends(role_read)):
    role = crud.get_role(db, role_id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=schemas.Role)
def update_role(
    role_id: int,
    role: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    _=Depends(role_update),
):
    result = crud.update_role(db, role_id=role_id, role=role)
    if not result:
        raise HTTPException(status_code=404, detail="Role not found")
    return result


@router.delete("/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db), _=Depends(role_delete)):
    if not crud.delete_role(db, role_id=role_id):
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}
