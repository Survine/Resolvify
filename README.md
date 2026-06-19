# Resolvify

A modern, production-grade Customer Support Management System with a clean separation between the **FastAPI backend** (dependency injection, PostgreSQL, SQLAlchemy 2.0, Redis pub/sub) and **React frontend** (Vite, React Router, Tailwind CSS, WebSockets).

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
│   └── index.html             # HTML template entrypoint
```

---

## 🚀 Key Features

*   **🏪 Multi-Branch Support:** Independent shop setup and specialized customer channels.
*   **🔐 Granular RBAC:** Complete Role-Based Access Control enforcing resource-level permissions (e.g. `read_shop`, `create_employee`, `update_chat`).
*   **💬 Live WebSocket Chat:** Real-time communication with Redis Pub/Sub backend for seamless multi-instance scaling.
*   **🌓 Adaptive Dark Mode:** Hand-crafted, premium light and dark themes using HSL CSS design tokens.
*   **🐳 Containerized Deployments:** Multi-stage Docker config ready for easy deployment to Render, Vercel, or Fly.io.

---

## ⚙️ Local Development Setup

### Prerequisites
*   **Python 3.11+**
*   **Node.js v18+**
*   **PostgreSQL** database
*   **Redis** server

---

### 1. Backend Setup

1.  Navigate into backend folder and create a virtual environment:
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
3.  Set up your environment variables by copying `.env.example`:
    ```bash
    copy .env.example .env
    ```
    *Update database and Redis variables to point to your local instances.*

4.  Seed default roles, permissions, shops, and employees:
    ```bash
    python -m scripts.seed
    ```

5.  Start the FastAPI dev server:
    ```bash
    uvicorn app.main:app --reload
    ```

---

### 2. Frontend Setup

1.  Navigate into frontend folder and install packages:
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
    *   **Agent Portal Login:** `http://localhost:5173/login` (Use credentials: `admin` / `admin123`)

---

## 🔐 Seeder Credentials

After running `python -m scripts.seed`, you can log in with:
*   **System Admin:** `admin` / `admin123`
*   **Shop Manager:** `manager1` / `manager123`
*   **Support Agent:** `support1` / `support123`
