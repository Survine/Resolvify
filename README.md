# Resolvify

A modern, production-grade Customer Support Management System with a clean separation between the **FastAPI backend** (dependency injection, SQLite/PostgreSQL, SQLAlchemy 2.0, Redis pub/sub with in-memory fallback) and **React frontend** (Vite, React Router, Tailwind CSS, WebSockets).

---

## 🏗️ Project Architecture

```
Resolvify/
├── backend/                   # FastAPI Application
│   ├── app/
│   │   ├── models/            # SQLAlchemy Declarative Models
│   │   ├── schemas/           # Pydantic v2 validation schemas
│   │   ├── crud/              # Database CRUD services
│   │   ├── services/          # Authentication & WebSocket connection manager
│   │   ├── routers/           # Route handlers
│   │   ├── config.py          # Centralized pydantic-settings configuration
│   │   ├── database.py        # SQLAlchemy session & base setup
│   │   ├── dependencies.py    # Injection helpers (RBAC Permission Checkers)
│   │   └── main.py            # Lifespan managed FastAPI entrypoint
│   ├── scripts/
│   │   └── seed.py            # Database seeding utility
│   ├── requirements.txt       # Backend dependencies
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
*   **🔐 Granular RBAC:** Complete Role-Based Access Control enforcing resource-level permissions (e.g. `read_shop`, `create_employee`, `update_chat`).
*   **💬 Live WebSocket Chat:** Real-time bi-directional communication with Redis Pub/Sub support and automatic local in-memory fallback.
*   **🌓 Adaptive Dark Mode:** Custom light and dark themes using CSS variables and HSL color tokens.
*   **🐳 Containerized Deployments:** Dockerfile + Docker Compose for running FastAPI, PostgreSQL, and Redis together.

---

## 🐳 Running with Docker (Fastest Setup)

If you have Docker Desktop installed, you can start the entire stack (**FastAPI Backend + PostgreSQL + Redis**) with a single command:

```bash
docker compose up --build
```

This starts:
- **Backend API**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432`
- **Redis Cache/PubSub**: `localhost:6379`

---

## ⚙️ Local Development Setup (Without Docker)

### Prerequisites
*   **Python 3.11+**
*   **Node.js v18+**
*   **SQLite** (default out-of-the-box local database) or **PostgreSQL**
*   **Redis** (optional, automatic in-memory fallback if not running)

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
3.  Set up your environment variables by creating `.env` from `.env.example`:
    ```bash
    # Windows PowerShell
    Copy-Item .env.example .env
    # macOS/Linux
    cp .env.example .env
    ```

4.  Seed initial database roles, permissions, shops, and demo accounts:
    ```bash
    python -m scripts.seed
    ```

5.  Start the FastAPI development server:
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
3.  Access the applications in your browser:
    *   **Customer Support Chat:** `http://localhost:5173/chat`
    *   **Agent Portal Login:** `http://localhost:5173/login`

---

## 🔐 Seeder Credentials

After running `python -m scripts.seed` (or running via Docker), you can log in with:
*   **System Admin:** `admin` / `admin123`
*   **Shop Manager:** `manager1` / `manager123`
*   **Support Agent:** `support1` / `support123`
