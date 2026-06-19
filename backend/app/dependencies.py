from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth import get_current_active_employee
from app import models


class PermissionChecker:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action

    def __call__(
        self,
        current_employee: models.Employee = Depends(get_current_active_employee),
        db: Session = Depends(get_db),
    ):
        has = (
            db.query(models.Permission)
            .join(models.role_permissions)
            .filter(
                models.role_permissions.c.role_id == current_employee.role_id,
                models.Permission.resource == self.resource,
                models.Permission.action == self.action,
            )
            .first()
        )
        if not has:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions to {self.action} {self.resource}",
            )
        return current_employee


def require_permission(resource: str, action: str):
    return PermissionChecker(resource, action)


# Pre-built permission checkers
shop_read = PermissionChecker("shop", "read")
shop_create = PermissionChecker("shop", "create")
shop_update = PermissionChecker("shop", "update")
shop_delete = PermissionChecker("shop", "delete")

employee_read = PermissionChecker("employee", "read")
employee_create = PermissionChecker("employee", "create")
employee_update = PermissionChecker("employee", "update")
employee_delete = PermissionChecker("employee", "delete")

team_read = PermissionChecker("team", "read")
team_create = PermissionChecker("team", "create")
team_update = PermissionChecker("team", "update")
team_delete = PermissionChecker("team", "delete")

role_read = PermissionChecker("role", "read")
role_create = PermissionChecker("role", "create")
role_update = PermissionChecker("role", "update")
role_delete = PermissionChecker("role", "delete")

chat_read = PermissionChecker("chat", "read")
chat_create = PermissionChecker("chat", "create")
chat_update = PermissionChecker("chat", "update")
chat_delete = PermissionChecker("chat", "delete")

customer_read = PermissionChecker("customer", "read")
customer_create = PermissionChecker("customer", "create")
customer_update = PermissionChecker("customer", "update")
customer_delete = PermissionChecker("customer", "delete")

permission_read = PermissionChecker("permission", "read")
permission_create = PermissionChecker("permission", "create")
permission_update = PermissionChecker("permission", "update")
permission_delete = PermissionChecker("permission", "delete")
