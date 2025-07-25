"""
Setup script to initialize the database with sample data
Run this script after installing dependencies to set up the system
"""

import asyncio
from sqlalchemy.orm import Session
from databases.database import SessionLocal, engine
import models
import crud
import schemas
from permissions import create_default_permissions, create_default_roles
from auth.auth import get_password_hash

def init_db():
    """Initialize database with sample data"""
    
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create default permissions and roles
        print("Creating default permissions and roles...")
        create_default_permissions(db)
        create_default_roles(db)
        
        # Create sample shops
        print("Creating sample shops...")
        shop1 = crud.create_shop(db, schemas.ShopCreate(
            name="Downtown Branch",
            location="123 Main St, Downtown"
        ))
        
        shop2 = crud.create_shop(db, schemas.ShopCreate(
            name="Mall Branch",
            location="456 Shopping Mall, Uptown"
        ))
        
        # Get roles
        admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        manager_role = db.query(models.Role).filter(models.Role.name == "manager").first()
        support_role = db.query(models.Role).filter(models.Role.name == "support_agent").first()
        
        # Create sample employees
        print("Creating sample employees...")
        
        # Admin user
        admin = crud.create_employee(db, schemas.EmployeeCreate(
            username="admin",
            email="admin@techcorp.com",
            first_name="John",
            last_name="Admin",
            password="admin123",
            shop_id=shop1.id,
            role_id=admin_role.id
        ))
        
        # Manager
        manager = crud.create_employee(db, schemas.EmployeeCreate(
            username="manager1",
            email="manager@techcorp.com",
            first_name="Jane",
            last_name="Manager",
            password="manager123",
            shop_id=shop1.id,
            role_id=manager_role.id
        ))
        
        # Support agents
        support1 = crud.create_employee(db, schemas.EmployeeCreate(
            username="support1",
            email="support1@techcorp.com",
            first_name="Alice",
            last_name="Support",
            password="support123",
            shop_id=shop1.id,
            role_id=support_role.id
        ))
        
        support2 = crud.create_employee(db, schemas.EmployeeCreate(
            username="support2",
            email="support2@techcorp.com",
            first_name="Bob",
            last_name="Helper",
            password="support123",
            shop_id=shop2.id,
            role_id=support_role.id
        ))
        
        # Create sample teams
        print("Creating sample teams...")
        team1 = crud.create_team(db, schemas.TeamCreate(
            name="Technical Support",
            description="Handles technical issues and troubleshooting",
            shop_id=shop1.id
        ))
        
        team2 = crud.create_team(db, schemas.TeamCreate(
            name="Customer Service",
            description="Handles general customer inquiries",
            shop_id=shop1.id
        ))
        
        team3 = crud.create_team(db, schemas.TeamCreate(
            name="Sales Support",
            description="Assists with sales-related questions",
            shop_id=shop2.id
        ))
        
        # Assign employees to teams
        print("Assigning employees to teams...")
        support1_updated = crud.update_employee(db, support1.id, schemas.EmployeeUpdate(
            team_ids=[team1.id, team2.id]
        ))
        
        support2_updated = crud.update_employee(db, support2.id, schemas.EmployeeUpdate(
            team_ids=[team3.id]
        ))
        
        manager_updated = crud.update_employee(db, manager.id, schemas.EmployeeUpdate(
            team_ids=[team1.id, team2.id, team3.id]
        ))
        
        # Create sample customers
        print("Creating sample customers...")
        customer1 = crud.create_customer(db, schemas.CustomerCreate(
            name="John Customer",
            email="customer1@example.com"
        ))
        
        customer2 = crud.create_customer(db, schemas.CustomerCreate(
            name="Jane Buyer",
            email="customer2@example.com"
        ))
        
        print("✅ Database initialized successfully!")
        print("\n" + "="*50)
        print("SAMPLE LOGIN CREDENTIALS:")
        print("="*50)
        print("Admin User:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nManager:")
        print("  Username: manager1")
        print("  Password: manager123")
        print("\nSupport Agents:")
        print("  Username: support1")
        print("  Password: support123")
        print("\n  Username: support2")
        print("  Password: support123")
        print("="*50)
        print("\n🚀 You can now start the application with: uvicorn main:app --reload")
        print("📱 Access the application at: http://localhost:8000")
        print("👨‍💼 Employee Dashboard: http://localhost:8000/support")
        print("🙋‍♀️ Customer Chat: http://localhost:8000/customer")
        print("📚 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
