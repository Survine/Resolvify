from sqlalchemy.orm import Session
import models
import schemas

def get_permission(db: Session, permission_id: int):
    return db.query(models.Permission).filter(models.Permission.id == permission_id).first()

def get_permission_by_name(db: Session, name: str):
    return db.query(models.Permission).filter(models.Permission.name == name).first()

def get_permissions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Permission).offset(skip).limit(limit).all()

def get_permissions_by_resource(db: Session, resource: str):
    return db.query(models.Permission).filter(models.Permission.resource == resource).all()

def get_permissions_by_action(db: Session, action: str):
    return db.query(models.Permission).filter(models.Permission.action == action).all()

def create_permission(db: Session, permission: schemas.PermissionCreate):
    db_permission = models.Permission(
        name=permission.name,
        description=permission.description,
        resource=permission.resource,
        action=permission.action
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def update_permission(db: Session, permission_id: int, permission_data: schemas.PermissionCreate):
    db_permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    if db_permission:
        db_permission.name = permission_data.name
        db_permission.description = permission_data.description
        db_permission.resource = permission_data.resource
        db_permission.action = permission_data.action
        db.commit()
        db.refresh(db_permission)
    return db_permission

def delete_permission(db: Session, permission_id: int):
    db_permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    if db_permission:
        db.delete(db_permission)
        db.commit()
    return db_permission