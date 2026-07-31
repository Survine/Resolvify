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
│   ├── Dockerfile             # Containerized Vite runner
│   ├── vite.config.js         # Vite configuration with API Proxy
│   ├── package.json           # Frontend dependencies
│   └── vercel.json            # Deployment routing rules
│
└── docker-compose.yml         # Container orchestration (Frontend + Backend + Postgres + Redis + Adminer)
```

---

## 🚀 Key Features

* **🏪 Multi-Branch Support:** Independent shop setup and specialized customer support channels.
* **🔐 Granular RBAC:** Role-Based Access Control enforcing resource-level permissions (`read_shop`, `create_employee`, `update_chat`).
* **👥 Admin & Manager Queue Overview:** Admin and Manager roles automatically see waiting support requests across **all** shop branches in real time.
* **💬 Coherent Redis Pub/Sub Messaging:** Real-time bi-directional communication powered by Redis Pub/Sub to ensure UI components and WebSocket connections across instances remain 100% synchronized.
* **🔄 Session & Message Preservation on Refresh:** Active customer chat sessions restore automatically upon page refresh, complete with message history and live WebSocket reconnection.
* **🏷️ Context-Aware Sender Display:** Displays `"Support Agent"` in customer chat views and the **Customer Name / ID** in employee dashboard views.
* **🐘 Single Database Stack:** Standardized on PostgreSQL across development, Docker, and production.
* **🌓 Adaptive Dark Mode:** Custom light and dark themes using CSS variables and HSL color tokens.
* **🐳 Containerized Orchestration:** Complete multi-container setup with Docker Compose & live volume mounts.

---

## 🐳 Running with Docker (Recommended)

Start the entire stack (**Frontend + FastAPI Backend + PostgreSQL + Redis + Adminer**) simultaneously with a single command:

```bash
docker compose up --build
```

This starts:
- **Frontend App**: `http://localhost:5174` (or `http://localhost:5173` locally)
- **Backend API**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432` (`resolvify_db`)
- **Redis Pub/Sub**: `localhost:6379`
- **Adminer Web Database Viewer**: `http://localhost:8080`

---

## ☁️ Deployment Guide (Render + Vercel)

Resolvify is architected for seamless deployment using **Render** (Backend) and **Vercel** (Frontend).

### 1. Deploying Backend to Render

1. **Create a Web Service on Render**:
   - Connect your repository and set the Root Directory to `backend/`.
   - Choose **Docker** as the Runtime (or Python 3.12 with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
2. **Add Render Managed Databases**:
   - Create a **Render PostgreSQL** database and copy the Internal/External Connection String.
   - Create a **Render Redis** instance and note the Host & Port.
3. **Configure Environment Variables in Render**:
   - `DATABASE_URL` = `postgresql://user:pass@host:5432/resolvify_db`
   - `REDIS_HOST` = `<your-render-redis-host>`
   - `REDIS_PORT` = `<your-render-redis-port>`
   - `SECRET_KEY` = `<your-production-secret-key>`
   - `CORS_ORIGINS` = `["https://<your-vercel-app>.vercel.app"]`

---

### 2. Deploying Frontend to Vercel

1. **Import Repository to Vercel**:
   - Set the Root Directory to `frontend`.
   - Framework Preset: **Vite**.
2. **Set Environment Variables in Vercel Dashboard**:
   - `VITE_API_URL` = `https://<your-render-backend-app>.onrender.com`
   - `VITE_WS_URL` = `wss://<your-render-backend-app>.onrender.com`
3. **Routing**:
   - The included [frontend/vercel.json](file:///d:/Resolvify/frontend/vercel.json) handles client-side SPA routing rewrites automatically.

---

## ⚙️ Local Development Setup

### Prerequisites
* **Python 3.11+**
* **Node.js v18+**
* **PostgreSQL** (running locally on port `5432` or via Docker)
* **Redis** (running locally on port `6379` or via Docker)

---

### 1. Backend Setup

1. Navigate into `backend/` and create a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env`:
   ```ini
   DATABASE_URL=postgresql://resolvify_user:resolvify_pass@localhost:5432/resolvify_db
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```
4. Seed initial database roles, permissions, shops, and demo accounts into PostgreSQL:
   ```bash
   python -m scripts.seed
   ```
5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

---

### 2. Frontend Setup

1. Navigate into `frontend/` and install packages:
   ```bash
   cd ../frontend
   npm install
   ```
2. Start the Vite dev server:
   ```bash
   npm run dev
   ```
3. Access the application:
   * **Customer Support Chat:** `http://localhost:5174/chat` (or `http://localhost:5173/chat`)
   * **Agent Portal Login:** `http://localhost:5174/login`

---

## 🔐 Demo Credentials

### 👤 Application Login Accounts
* **System Admin:** `admin` / `admin123`
* **Shop Manager:** `manager1` / `manager123`
* **Support Agent:** `support1` / `support123`

### 🐘 Adminer Database GUI (`http://localhost:8080`)
* **System:** PostgreSQL
* **Server:** `postgres` *(or `localhost` if connecting outside Docker)*
* **Username:** `resolvify_user`
* **Password:** `resolvify_pass`
* **Database:** `resolvify_db`
