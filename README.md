# Yupcha v4 - Customer Support Management System

A modern, scalable FastAPI-based customer support management system with real-time chat, role-based permissions, multi-shop management, and Redis-powered WebSocket communication.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Redis](https://img.shields.io/badge/Redis-latest-red.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)

## 🚀 Features

### Core Features
- **🏪 Multi-Shop Management**: Independent shop operations with dedicated support teams
- **👥 Employee Management**: Organized teams within shops with role-based access
- **🔐 Role-Based Access Control**: Granular permissions system with customizable roles
- **💬 Real-time Chat**: WebSocket-powered customer support with Redis pub/sub
- **📊 RESTful API**: Complete CRUD operations with OpenAPI documentation
- **🎨 Modern UI**: Clean, responsive interfaces for both customers and support agents

### Advanced Features
- **🔄 Redis Integration**: Multi-worker support with Redis pub/sub messaging
- **⚡ WebSocket Communication**: Real-time bidirectional messaging
- **🏷️ Session Management**: Persistent chat sessions with message history
- **🔔 Real-time Notifications**: Instant notifications for new sessions and messages
- **📱 Responsive Design**: Mobile-friendly customer and support interfaces
- **🛡️ Authentication**: JWT-based secure authentication system

## 🛠️ Prerequisites

- **Python 3.11+**
- **Redis Server** (for real-time messaging)
- **Git** (for cloning the repository)

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Survine/Yupcha-v4.git
cd Yupcha-v4
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Redis Setup

#### Option A: Docker (Recommended)
```bash
docker run --name yupcha-redis -p 6379:6379 -d redis:latest
```

#### Option B: Local Installation
- Windows: Download from [Redis Windows](https://redis.io/download)
- Linux: `sudo apt-get install redis-server`
- Mac: `brew install redis`

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=sqlite:///./customer_support.db

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 6. Database Initialization
```bash
python setup_db.py
```

### 7. Start the Application
```bash
# Development
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 Access Points

Once the server is running, access these URLs:

- **🏠 Home**: http://localhost:8000
- **👤 Customer Chat**: http://localhost:8000/customer
- **🎧 Support Dashboard**: http://localhost:8000/support
- **📚 API Documentation**: http://localhost:8000/docs
- **🔍 Alternative Docs**: http://localhost:8000/redoc

## 🔧 API Endpoints

### Authentication
- `POST /auth/token` - User login
- `POST /auth/refresh` - Refresh access token

### Shop Management
- `GET /shops/` - List all shops
- `POST /shops/` - Create new shop
- `GET /shops/{id}` - Get shop details
- `PUT /shops/{id}` - Update shop
- `DELETE /shops/{id}` - Delete shop

### Employee Management
- `GET /employees/` - List employees
- `POST /employees/` - Create employee
- `GET /employees/me` - Current employee info
- `PUT /employees/{id}` - Update employee
- `DELETE /employees/{id}` - Delete employee

### Chat System
- `GET /chat/shops/` - Available shops for chat
- `POST /chat/sessions/` - Create chat session
- `GET /chat/sessions/waiting` - Waiting sessions
- `GET /chat/sessions/active` - Active sessions
- `PUT /chat/sessions/{id}/assign` - Assign session to employee
- `PUT /chat/sessions/{id}/close` - Close chat session
- `WS /chat/ws/customer/{email}` - Customer WebSocket
- `WS /chat/ws/employee/{id}` - Employee WebSocket

### Customer Management
- `GET /customers/` - List customers
- `POST /customers/` - Create customer
- `GET /customers/{id}` - Customer details

## 🏗️ Project Structure

```
Yupcha-v4/
├── 📄 main.py                    # FastAPI application entry point
├── 🗃️ customer_support.db       # SQLite database
├── ⚙️ setup_db.py               # Database initialization
├── 🔒 permissions.py            # Permission system
├── 📋 requirements.txt          # Python dependencies
├── 🔐 auth/                     # Authentication system
│   ├── auth.py                  # JWT authentication
│   ├── auth_router.py           # Auth endpoints
│   └── auth_schema.py           # Auth data models
├── 🗄️ crud/                     # Database operations
│   ├── customer.py
│   ├── employee.py
│   ├── shop.py
│   ├── chat.py
│   └── ...
├── 🏢 databases/                # Database configuration
│   └── database.py
├── 📊 models/                   # SQLAlchemy models
│   ├── customer.py
│   ├── employee.py
│   ├── chat_session.py
│   ├── chat_message.py
│   └── ...
├── 🌐 routers/                  # API route handlers
│   ├── customers.py
│   ├── employees.py
│   ├── shops.py
│   ├── chat.py
│   └── ...
├── 📝 schemas/                  # Pydantic schemas
│   ├── customer.py
│   ├── employee.py
│   ├── chat_session.py
│   └── ...
└── 🎨 templates/               # HTML templates
    ├── customer.html           # Customer chat interface
    └── support.html            # Support agent dashboard
```

## 💬 Real-time Chat System

### Architecture
The chat system uses **WebSockets** with **Redis pub/sub** for real-time communication:

```
Customer Browser ←→ WebSocket ←→ FastAPI Server ←→ Redis ←→ Support Agent Browser
```

### Key Features
- **Session Management**: Persistent chat sessions with full message history
- **Auto-assignment**: Automatic mapping of customer sessions to WebSocket connections
- **Multi-worker Support**: Redis enables horizontal scaling with multiple server instances
- **Real-time Notifications**: Instant updates for new sessions, messages, and status changes
- **Typing Indicators**: Live typing status between customers and agents

### Chat Flow
1. Customer selects a shop and provides contact information
2. System creates a chat session and notifies available agents
3. Support agent accepts the session and begins conversation
4. All messages are stored in database and delivered via Redis
5. Either party can end the session

## 🐳 Docker Deployment

### Docker Compose (Recommended)
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

```bash
docker-compose up -d
```

## 🔍 Monitoring & Debugging

### Health Check
```bash
curl http://localhost:8000/health
```

### Redis Connection Test
```bash
# Check if Redis is accessible
redis-cli ping
```

### WebSocket Testing
Use browser developer tools or WebSocket testing tools to connect to:
- Customer: `ws://localhost:8000/chat/ws/customer/test@example.com`
- Employee: `ws://localhost:8000/chat/ws/employee/1`

## 🚀 Production Deployment

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname  # Use PostgreSQL for production
SECRET_KEY=your-production-secret-key-here
REDIS_HOST=your-redis-host
REDIS_PORT=6379
```

### Recommended Production Setup
1. **Database**: PostgreSQL instead of SQLite
2. **Redis**: Redis Cluster for high availability
3. **Load Balancer**: Nginx for multiple app instances
4. **HTTPS**: SSL/TLS certificates
5. **Monitoring**: Health checks and logging

### Example Production Command
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📊 Database Schema

### Key Tables
- **shops**: Store locations and information
- **employees**: Support agents and administrators
- **customers**: Customer contact information
- **chat_sessions**: Individual support sessions
- **chat_messages**: All chat messages with timestamps
- **roles & permissions**: RBAC system tables

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Granular permissions system
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Protection**: Configurable CORS policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Issues

- **Issues**: [GitHub Issues](https://github.com/Survine/Yupcha-v4/issues)
- **Documentation**: Check `/docs` endpoint when server is running
- **Community**: Join our discussions for help and feature requests

## 🔄 Version History

- **v4.0**: Redis integration, enhanced WebSocket communication, improved UI
- **v3.x**: Multi-shop support, role-based permissions
- **v2.x**: Basic chat functionality, employee management  
- **v1.x**: Initial customer support system

---

**Built with ❤️ using FastAPI, Redis, and modern web technologies**
