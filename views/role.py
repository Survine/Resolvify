from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas


def create_role(db: Session, role: schemas.RoleCreate) -> models.Role:
    db_role = models.Role(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    
    if role.permission_ids:
        permissions = db.query(models.Permission).filter(
            models.Permission.id.in_(role.permission_ids)
        ).all()
        db_role.permissions = permissions
        db.commit()
    
    db.refresh(db_role)
    return db_role

def get_role(db: Session, role_id: int) -> Optional[models.Role]:
    return db.query(models.Role).filter(models.Role.id == role_id).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Role]:
    return db.query(models.Role).offset(skip).limit(limit).all()

def update_role(db: Session, role_id: int, role: schemas.RoleUpdate) -> Optional[models.Role]:
    db_role = get_role(db, role_id)
    if db_role:
        if role.name is not None:
            db_role.name = role.name
        if role.description is not None:
            db_role.description = role.description
        
        if role.permission_ids is not None:
            permissions = db.query(models.Permission).filter(
                models.Permission.id.in_(role.permission_ids)
            ).all()
            db_role.permissions = permissions
        
        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int) -> bool:
    db_role = get_role(db, role_id)
    if db_role:
        db.delete(db_role)
        db.commit()
        return True
    return False