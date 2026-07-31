"""
Database seeding script — run once to populate initial data.
Usage: python -m scripts.seed (from backend/)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app import models, schemas, crud
from app.services.auth import hash_password
from app.services.permissions import create_default_permissions, create_default_roles


def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        create_default_permissions(db)
        create_default_roles(db)

        # Check if already seeded
        existing_shops = crud.get_shops(db)
        if existing_shops:
            print("Database already seeded. Skipping...")
            print("=" * 40)
            print("Login credentials:")
            print("  admin / admin123")
            print("  manager1 / manager123")
            print("  support1 / support123")
            print("  support2 / support123")
            print("=" * 40)
            return

        # Shops
        print("Seeding shops...")
        shop1 = crud.create_shop(db, schemas.ShopCreate(name="Downtown Branch", location="123 Main St, Downtown"))
        shop2 = crud.create_shop(db, schemas.ShopCreate(name="Mall Branch", location="456 Shopping Mall, Uptown"))

        # Roles
        admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        manager_role = db.query(models.Role).filter(models.Role.name == "manager").first()
        support_role = db.query(models.Role).filter(models.Role.name == "support_agent").first()

        # Employees
        print("Seeding employees...")
        admin = crud.create_employee(db, schemas.EmployeeCreate(
            username="admin", email="admin@resolvify.io",
            first_name="John", last_name="Admin",
            password="admin123", shop_id=shop1.id, role_id=admin_role.id,
        ))
        manager = crud.create_employee(db, schemas.EmployeeCreate(
            username="manager1", email="manager@resolvify.io",
            first_name="Jane", last_name="Manager",
            password="manager123", shop_id=shop1.id, role_id=manager_role.id,
        ))
        support1 = crud.create_employee(db, schemas.EmployeeCreate(
            username="support1", email="support1@resolvify.io",
            first_name="Alice", last_name="Support",
            password="support123", shop_id=shop1.id, role_id=support_role.id,
        ))
        support2 = crud.create_employee(db, schemas.EmployeeCreate(
            username="support2", email="support2@resolvify.io",
            first_name="Bob", last_name="Helper",
            password="support123", shop_id=shop2.id, role_id=support_role.id,
        ))

        # Teams
        print("Seeding teams...")
        team1 = crud.create_team(db, schemas.TeamCreate(name="Technical Support", description="Handles technical issues", shop_id=shop1.id))
        team2 = crud.create_team(db, schemas.TeamCreate(name="Customer Service", description="General customer inquiries", shop_id=shop1.id))
        team3 = crud.create_team(db, schemas.TeamCreate(name="Sales Support", description="Sales-related questions", shop_id=shop2.id))

        crud.update_employee(db, support1.id, schemas.EmployeeUpdate(team_ids=[team1.id, team2.id]))
        crud.update_employee(db, support2.id, schemas.EmployeeUpdate(team_ids=[team3.id]))
        crud.update_employee(db, manager.id, schemas.EmployeeUpdate(team_ids=[team1.id, team2.id, team3.id]))

        # Customers
        print("Seeding customers...")
        crud.create_customer(db, schemas.CustomerCreate(name="John Customer", email="customer1@example.com"))
        crud.create_customer(db, schemas.CustomerCreate(name="Jane Buyer", email="customer2@example.com"))

        print("\nDatabase seeded successfully!")
        print("=" * 40)
        print("Login credentials:")
        print("  admin / admin123")
        print("  manager1 / manager123")
        print("  support1 / support123")
        print("  support2 / support123")
        print("=" * 40)

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
