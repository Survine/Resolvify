from sqlalchemy.orm import Session
from typing import List
import models
import schemas


def create_permission(db: Session, permission: schemas.PermissionCreate) -> models.Permission:
    db_permission = models.Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[models.Permission]:
    return db.query(models.Permission).offset(skip).limit(limit).all()