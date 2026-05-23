from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.database import engine, Base, SessionLocal
from core.security import get_password_hash
from core.config import settings
from models.models import User
from routers import auth, products, transactions, dashboard, export
from pathlib import Path



app = FastAPI(title="ShopStock API", version="1.0.0")
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(export.router)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Serve CSS and JS correctly
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

@app.on_event("startup")
def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not existing:
            admin = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD)
            )
            db.add(admin)
            db.commit()
            print(f"Admin user created: {settings.ADMIN_EMAIL}")
    finally:
        db.close()

@app.get("/")
def root():
    return FileResponse(str(FRONTEND_DIR / "pages" / "login.html"))

@app.get("/{page}.html")
def serve_page(page: str):
    page_file = FRONTEND_DIR / "pages" / f"{page}.html"
    if page_file.exists():
        return FileResponse(str(page_file))
    return FileResponse(str(FRONTEND_DIR / "pages" / "login.html"))

@app.get("/api/health")
def health():
    return {"status": "ok"}
