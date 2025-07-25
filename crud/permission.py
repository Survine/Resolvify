from sqlalchemy.orm import Session
from ..models.permission import Permission as PermissionModel
from ..schemas.permission import PermissionCreate

def get_permission(db: Session, permission_id: int):
    return db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()

def get_permission_by_name(db: Session, name: str):
    return db.query(PermissionModel).filter(PermissionModel.name == name).first()

def get_permissions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PermissionModel).offset(skip).limit(limit).all()

def get_permissions_by_resource(db: Session, resource: str):
    return db.query(PermissionModel).filter(PermissionModel.resource == resource).all()

def get_permissions_by_action(db: Session, action: str):
    return db.query(PermissionModel).filter(PermissionModel.action == action).all()

def create_permission(db: Session, permission: PermissionCreate):
    db_permission = PermissionModel(
        name=permission.name,
        description=permission.description,
        resource=permission.resource,
        action=permission.action
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def update_permission(db: Session, permission_id: int, permission_data: PermissionCreate):
    db_permission = db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()
    if db_permission:
        db_permission.name = permission_data.name
        db_permission.description = permission_data.description
        db_permission.resource = permission_data.resource
        db_permission.action = permission_data.action
        db.commit()
        db.refresh(db_permission)
    return db_permission

def delete_permission(db: Session, permission_id: int):
    db_permission = db.query(PermissionModel).filter(PermissionModel.id == permission_id).first()
    if db_permission:
        db.delete(db_permission)
        db.commit()
    return db_permission