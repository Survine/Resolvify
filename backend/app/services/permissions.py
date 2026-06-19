import logging
from sqlalchemy.orm import Session

from app import models

logger = logging.getLogger(__name__)


def create_default_permissions(db: Session):
    resources = ["shop", "employee", "team", "role", "chat", "permission", "customer"]
    actions = ["create", "read", "update", "delete"]

    for resource in resources:
        for action in actions:
            name = f"{action}_{resource}"
            exists = db.query(models.Permission).filter(models.Permission.name == name).first()
            if not exists:
                db.add(
                    models.Permission(
                        name=name,
                        description=f"Permission to {action} {resource}",
                        resource=resource,
                        action=action,
                    )
                )
    db.commit()
    logger.info("Default permissions ensured")


def create_default_roles(db: Session):
    # Admin
    admin = db.query(models.Role).filter(models.Role.name == "admin").first()
    if not admin:
        admin = models.Role(name="admin", description="Full system administrator")
        db.add(admin)
        db.commit()
        admin.permissions = db.query(models.Permission).all()
        db.commit()

    # Manager
    manager = db.query(models.Role).filter(models.Role.name == "manager").first()
    if not manager:
        manager = models.Role(name="manager", description="Shop manager with limited admin access")
        db.add(manager)
        db.commit()
        manager.permissions = (
            db.query(models.Permission)
            .filter(
                models.Permission.name.in_(
                    [
                        "read_shop", "update_shop",
                        "create_employee", "read_employee", "update_employee",
                        "create_team", "read_team", "update_team", "delete_team",
                        "create_chat", "read_chat", "update_chat",
                        "read_customer",
                    ]
                )
            )
            .all()
        )
        db.commit()

    # Support Agent
    support = db.query(models.Role).filter(models.Role.name == "support_agent").first()
    if not support:
        support = models.Role(name="support_agent", description="Customer support agent")
        db.add(support)
        db.commit()
        support.permissions = (
            db.query(models.Permission)
            .filter(
                models.Permission.name.in_(
                    [
                        "read_employee", "read_team", "read_shop",
                        "create_chat", "read_chat", "update_chat",
                        "read_customer", "create_customer",
                    ]
                )
            )
            .all()
        )
        db.commit()

    logger.info("Default roles ensured")
