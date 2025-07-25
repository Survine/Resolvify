from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
import models
from auth.auth import get_current_active_employee
from databases.database import get_db

class PermissionChecker:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action
    
    def __call__(
        self, 
        current_employee: models.Employee = Depends(get_current_active_employee),
        db: Session = Depends(get_db)
    ):
        if not self.has_permission(current_employee, self.resource, self.action, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions to {self.action} {self.resource}"
            )
        return current_employee
    
    @staticmethod
    def has_permission(employee: models.Employee, resource: str, action: str, db: Session) -> bool:
        # Get employee's role permissions
        role_permissions = db.query(models.Permission).join(
            models.role_permissions
        ).filter(
            models.role_permissions.c.role_id == employee.role_id,
            models.Permission.resource == resource,
            models.Permission.action == action
        ).first()
        
        return role_permissions is not None

# Common permission decorators
def require_permission(resource: str, action: str):
    return PermissionChecker(resource, action)

# Specific permission checkers for common operations
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

def create_default_permissions(db: Session):
    """Create default permissions for the system"""
    resources = ["shop", "employee", "team", "role", "chat", "permission", "customer"]
    actions = ["create", "read", "update", "delete"]
    
    for resource in resources:
        for action in actions:
            permission_name = f"{action}_{resource}"
            existing_permission = db.query(models.Permission).filter(
                models.Permission.name == permission_name
            ).first()
            
            if not existing_permission:
                permission = models.Permission(
                    name=permission_name,
                    description=f"Permission to {action} {resource}",
                    resource=resource,
                    action=action
                )
                db.add(permission)
    
    db.commit()

def create_default_roles(db: Session):
    """Create default roles with appropriate permissions"""
    # Create Admin role with all permissions
    admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
    if not admin_role:
        admin_role = models.Role(
            name="admin",
            description="Full system administrator with all permissions"
        )
        db.add(admin_role)
        db.commit()
        
        # Assign all permissions to admin
        all_permissions = db.query(models.Permission).all()
        admin_role.permissions = all_permissions
        db.commit()
    
    # Create Manager role
    manager_role = db.query(models.Role).filter(models.Role.name == "manager").first()
    if not manager_role:
        manager_role = models.Role(
            name="manager",
            description="Shop manager with limited administrative permissions"
        )
        db.add(manager_role)
        db.commit()
        
        # Assign specific permissions to manager
        manager_permissions = db.query(models.Permission).filter(
            models.Permission.name.in_([
                "read_shop", "update_shop",
                "create_employee", "read_employee", "update_employee",
                "create_team", "read_team", "update_team", "delete_team",
                "create_chat", "read_chat", "update_chat",
                "read_customer"
            ])
        ).all()
        manager_role.permissions = manager_permissions
        db.commit()
    
    # Create Support Agent role
    support_role = db.query(models.Role).filter(models.Role.name == "support_agent").first()
    if not support_role:
        support_role = models.Role(
            name="support_agent",
            description="Customer support agent with chat permissions"
        )
        db.add(support_role)
        db.commit()
        
        # Assign chat permissions to support agent
        support_permissions = db.query(models.Permission).filter(
            models.Permission.name.in_([
                "read_employee", "read_team", "read_shop",
                "create_chat", "read_chat", "update_chat",
                "read_customer", "create_customer"
            ])
        ).all()
        support_role.permissions = support_permissions
        db.commit()
