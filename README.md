# Resolvify

A modern, production-grade Customer Support Management System with a clean separation between the **FastAPI backend** (PostgreSQL, SQLAlchemy 2.0, Redis Pub/Sub) and **React frontend** (Vite, React Router, Tailwind CSS, WebSockets).

---

## 🏗️ Project Architecture

```
Resolvify/
├── backend/                   # FastAPI Application
│   ├── app/
│   │   ├── models/            # SQLAlchemy Declarative Models
│   │   ├── schemas/           # Pydantic v2 validation schemas
│   │   ├── crud/              # Database CRUD services
│   │   ├── services/          # Authentication & Redis Pub/Sub Chat Manager
│   │   ├── routers/           # Route handlers
│   │   ├── config.py          # Centralized pydantic-settings configuration
│   │   ├── database.py        # SQLAlchemy PostgreSQL session setup
│   │   ├── dependencies.py    # Injection helpers (RBAC Permission Checkers)
│   │   └── main.py            # Lifespan managed FastAPI entrypoint
│   ├── scripts/
│   │   └── seed.py            # Database seeding utility
│   ├── requirements.txt       # Backend dependencies (psycopg2-binary, redis)
│   └── Dockerfile             # Production docker config
│
├── frontend/                  # React Application
│   ├── src/
│   │   ├── components/        # Reusable UI & chat components
│   │   ├── context/           # Global AuthContext provider
│   │   ├── hooks/             # Custom WebSocket, Auth, and Theme hooks
│   │   ├── pages/             # Login, Dashboard, CustomerChat views
│   │   ├── utils/             # Formatters and classname helpers
│   │   ├── App.jsx            # Main app router
│   │   ├── main.jsx           # Frontend entrypoint
│   │   └── index.css          # Design system & dark mode tokens
│   ├── vite.config.js         # Vite configuration with API Proxy
│   ├── package.json           # Frontend dependencies
│   └── vercel.json            # Deployment routing rules
│
└── docker-compose.yml         # Container orchestration (FastAPI + PostgreSQL + Redis)
```

---

## 🚀 Key Features

*   **🏪 Multi-Branch Support:** Independent shop setup and specialized customer support channels.
*   **🔐 Granular RBAC:** Role-Based Access Control enforcing resource-level permissions (e.g. `read_shop`, `create_employee`, `update_chat`).
*   **💬 Coherent Redis Pub/Sub Messaging:** Real-time bi-directional communication powered strictly by Redis Pub/Sub to ensure UI components and WebSocket connections across instances remain 100% synchronized.
*   **🐘 Single Database Stack:** Standardized on PostgreSQL across development, Docker, and production (Render).
*   **🌓 Adaptive Dark Mode:** Custom light and dark themes using CSS variables and HSL color tokens.
*   **🐳 Containerized Deployments:** Multi-container setup with Docker Compose.

---

## 🐳 Running with Docker (Recommended)

Start the entire stack (**FastAPI Backend + PostgreSQL + Redis**) with a single command:

```bash
docker compose up --build
```

This starts:
- **Backend API**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432` (`resolvify_db`)
- **Redis Pub/Sub**: `localhost:6379`
- **Adminer Web Database Viewer**: `http://localhost:8080`

---

## ⚙️ Local Development Setup

### Prerequisites
*   **Python 3.11+**
*   **Node.js v18+**
*   **PostgreSQL** (running locally on port `5432` or via Docker)
*   **Redis** (running locally on port `6379` or via Docker)

---

### 1. Backend Setup

1.  Navigate into the `backend/` directory and create a virtual environment:
    ```bash
    cd backend
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure your environment variables in `.env`:
    ```ini
    DATABASE_URL=postgresql://resolvify_user:resolvify_pass@localhost:5432/resolvify_db
    REDIS_HOST=localhost
    REDIS_PORT=6379
    ```

4.  Seed initial database roles, permissions, shops, and demo accounts into PostgreSQL:
    ```bash
    python -m scripts.seed
    ```

5.  Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```

---

### 2. Frontend Setup

1.  Navigate into the `frontend/` directory and install packages:
    ```bash
    cd ../frontend
    npm install
    ```
2.  Start the Vite dev server:
    ```bash
    npm run dev
    ```
3.  Access the applications:
    *   **Customer Support Chat:** `http://localhost:5173/chat`
    *   **Agent Portal Login:** `http://localhost:5173/login`

---

## 🔐 Demo Credentials

Log in with:
*   **System Admin:** `admin` / `admin123`
*   **Shop Manager:** `manager1` / `manager123`
*   **Support Agent:** `support1` / `support123`
