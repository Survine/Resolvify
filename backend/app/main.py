import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, get_db
from app.models import Base
from app.services.permissions import create_default_permissions, create_default_roles
from app.routers import auth, shops, employees, teams, roles, chat, customers, permissions

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    create_default_permissions(db)
    create_default_roles(db)
    db.close()
    yield


app = FastAPI(
    title="Resolvify",
    description="Customer support management platform with real-time chat and RBAC",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(shops.router)
app.include_router(employees.router)
app.include_router(teams.router)
app.include_router(roles.router)
app.include_router(chat.router)
app.include_router(customers.router)
app.include_router(permissions.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
