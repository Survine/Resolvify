from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import auth_router
from routers import shops, employees, teams, roles, chat
from databases.database import engine, get_db
from permissions import create_default_permissions, create_default_roles
import models 

app = FastAPI(
    title="Customer Support Management System",
    description="A comprehensive customer support system with role-based permissions and real-time chat",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(auth_router.router)
app.include_router(shops.router)
app.include_router(employees.router)
app.include_router(teams.router)
app.include_router(roles.router)
app.include_router(chat.router)

# Create tables if not exist
models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def on_startup():
    db = next(get_db())
    create_default_permissions(db)
    create_default_roles(db)
    db.close()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

@app.get("/support", response_class=HTMLResponse)
async def support_dashboard(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

@app.get("/customer", response_class=HTMLResponse)
async def customer_chat(request: Request):
    return templates.TemplateResponse("customer.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Customer Support System is running"}
