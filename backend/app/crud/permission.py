from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas


def create_permission(db: Session, permission: schemas.PermissionCreate) -> models.Permission:
    db_permission = models.Permission(
        name=permission.name,
        description=permission.description,
        resource=permission.resource,
        action=permission.action,
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def get_permission(db: Session, permission_id: int) -> Optional[models.Permission]:
    return db.query(models.Permission).filter(models.Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str) -> Optional[models.Permission]:
    return db.query(models.Permission).filter(models.Permission.name == name).first()


def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Permission]:
    return db.query(models.Permission).offset(skip).limit(limit).all()


def get_permissions_by_resource(db: Session, resource: str) -> List[models.Permission]:
    return db.query(models.Permission).filter(models.Permission.resource == resource).all()


def get_permissions_by_action(db: Session, action: str) -> List[models.Permission]:
    return db.query(models.Permission).filter(models.Permission.action == action).all()


def update_permission(
    db: Session, permission_id: int, data: schemas.PermissionCreate
) -> Optional[models.Permission]:
    db_perm = get_permission(db, permission_id)
    if not db_perm:
        return None
    db_perm.name = data.name
    db_perm.description = data.description
    db_perm.resource = data.resource
    db_perm.action = data.action
    db.commit()
    db.refresh(db_perm)
    return db_perm


def delete_permission(db: Session, permission_id: int) -> Optional[models.Permission]:
    db_perm = get_permission(db, permission_id)
    if db_perm:
        db.delete(db_perm)
        db.commit()
    return db_perm
