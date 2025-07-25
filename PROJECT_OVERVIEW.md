# 🏢 Customer Support Management System

## Project Overview

This is a comprehensive FastAPI-based customer support management system with the following features:

### 🌟 Key Features

1. **Multi-Company Architecture**
   - Companies can have multiple shops
   - Each shop can have multiple employees
   - Employees are organized into teams

2. **Role-Based Permission System**
   - Admin: Full system access
   - Manager: Shop-level management
   - Support Agent: Customer support operations
   - Granular permissions for each resource and action

3. **Real-Time Chat System**
   - WebSocket-based communication
   - Employee dashboard for handling multiple chat sessions
   - Customer interface for requesting support
   - Session management and assignment

4. **RESTful API**
   - Complete CRUD operations for all entities
   - Interactive API documentation
   - Authentication with JWT tokens

## 📁 Project Structure

```
d:\Yupcha v4\
├── main.py                 # FastAPI application entry point
├── database.py             # Database configuration and connection
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic data validation schemas
├── crud.py                 # Database CRUD operations
├── auth.py                 # Authentication and authorization
├── permissions.py          # Role-based permission system
├── setup_db.py             # Database initialization script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── README.md               # Project documentation
├── DEPLOYMENT.md           # Deployment guide
├── setup.bat               # Windows setup script
├── setup.ps1               # PowerShell setup script
├── routers/                # API route handlers
│   ├── auth.py             # Authentication endpoints
│   ├── companies.py        # Company management
│   ├── shops.py            # Shop management
│   ├── employees.py        # Employee management
│   ├── teams.py            # Team management
│   ├── roles.py            # Role and permission management
│   └── chat.py             # WebSocket chat functionality
└── templates/              # HTML templates
    ├── support.html        # Employee support dashboard
    └── customer.html       # Customer chat interface
```

## 🗄️ Database Schema

### Core Entities

1. **Company** - Top-level organization
2. **Shop** - Physical locations within a company
3. **Employee** - Users with roles and permissions
4. **Team** - Groups of employees within shops
5. **Role** - Permission templates (Admin, Manager, Support Agent)
6. **Permission** - Granular access rights
7. **Customer** - External users seeking support
8. **ChatSession** - Support conversation instances
9. **ChatMessage** - Individual messages in conversations

### Relationships

- Company → Shops (One-to-Many)
- Shop → Employees (One-to-Many)
- Shop → Teams (One-to-Many)
- Employee → Role (Many-to-One)
- Employee ↔ Teams (Many-to-Many)
- Role ↔ Permissions (Many-to-Many)
- Customer → ChatSessions (One-to-Many)
- ChatSession → Messages (One-to-Many)

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt encryption for password storage
- **Role-Based Access Control**: Granular permissions system
- **Input Validation**: Pydantic schema validation
- **CORS Support**: Configurable cross-origin requests

## 🚀 Getting Started

### Quick Setup

1. **Run Setup Script**:
   ```powershell
   .\setup.ps1
   ```
   Or:
   ```cmd
   setup.bat
   ```

2. **Manual Setup**:
   ```bash
   pip install -r requirements.txt
   python setup_db.py
   uvicorn main:app --reload
   ```

3. **Access the Application**:
   - Main Page: http://localhost:8000
   - Employee Dashboard: http://localhost:8000/support
   - Customer Chat: http://localhost:8000/customer
   - API Docs: http://localhost:8000/docs

### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Manager | manager1 | manager123 |
| Support Agent | support1 | support123 |
| Support Agent | support2 | support123 |

## 💻 Usage Examples

### Employee Workflow

1. **Login**: Access `/support` and login with employee credentials
2. **View Sessions**: See waiting and active chat sessions
3. **Take Session**: Assign waiting sessions to yourself
4. **Chat**: Communicate with customers in real-time
5. **Manage**: Close sessions when resolved

### Customer Workflow

1. **Start Chat**: Visit `/customer` page
2. **Enter Details**: Provide name and email
3. **Connect**: WebSocket connection established
4. **Chat**: Send messages to support team
5. **Get Help**: Receive assistance from assigned agent

### API Usage

```python
import requests

# Login
response = requests.post("http://localhost:8000/auth/token", 
                        data={"username": "admin", "password": "admin123"})
token = response.json()["access_token"]

# Create Company
headers = {"Authorization": f"Bearer {token}"}
company_data = {"name": "New Company", "description": "A new company"}
requests.post("http://localhost:8000/companies/", 
              json=company_data, headers=headers)
```

## 🔧 Customization

### Adding New Permissions

1. Edit `permissions.py`
2. Add new resources and actions
3. Update role assignments
4. Restart application

### Extending Models

1. Modify `models.py`
2. Update `schemas.py`
3. Add CRUD operations in `crud.py`
4. Create new API endpoints

### UI Customization

1. Edit HTML templates in `templates/`
2. Modify CSS styles inline
3. Add JavaScript functionality
4. Update WebSocket message handling

## 📊 Monitoring and Maintenance

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
- Application logs appear in terminal
- WebSocket connections logged
- Error tracking available

### Database Management
- SQLite database: `customer_support.db`
- Backup: Copy database file
- Migration: Use Alembic for schema changes

## 🌐 Production Deployment

See `DEPLOYMENT.md` for detailed production setup including:
- PostgreSQL configuration
- Gunicorn deployment
- Docker containerization
- Nginx reverse proxy
- SSL/HTTPS setup
- Environment variables

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the deployment guide
3. Test with default credentials
4. Verify WebSocket connections

---

**Built with ❤️ using FastAPI, SQLAlchemy, and WebSockets**
