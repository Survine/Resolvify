# Customer Support Management System

A FastAPI-based customer support management system with role-based permissions, multi-shop management, and real-time chat functionality.

## Features

- **Shop Management**: Multiple shops with independent management
- **Employee Management**: Employees organized in teams within shops
- **Role-Based Access Control**: Granular permissions for different roles
- **Real-time Chat**: WebSocket-based customer support chat system
- **RESTful API**: Complete CRUD operations for all entities

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create `.env` file):
```
DATABASE_URL=sqlite:///./customer_support.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Initialize the database:
```bash
python -m alembic init alembic
python -m alembic revision --autogenerate -m "Initial migration"
python -m alembic upgrade head
```

4. Run the application:
```bash
# If you have FastAPI CLI installed:
#   python -m fastapi dev main.py
# Otherwise, use Uvicorn:
uvicorn main:app --reload
```

## API Endpoints

- `/docs` - Interactive API documentation
- `/auth/` - Authentication endpoints
- `/shops/` - Shop management
- `/employees/` - Employee management
- `/teams/` - Team management
- `/roles/` - Role and permission management
- `/customers/` - Customer management
- `/permissions/` - Permission management
- `/chat/` - Chat endpoints
- `/support` - Employee support interface
- `/customer` - Customer chat interface

## Project Structure

```
customer_support/
├── main.py                 # FastAPI application entry point
├── database.py             # Database configuration
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas
├── routers/                # API route handlers
├── auth/                   # Authentication utilities
├── permissions/            # Role-based permission system
├── chat/                   # WebSocket chat functionality
├── templates/              # HTML templates
└── static/                 # Static files (CSS, JS)
```
