from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .routers import auth, feed, forums, notifications, projects

app = FastAPI(title="CampusConnect API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,  # required so the browser sends/receives the auth cookie cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(forums.router)
app.include_router(projects.router)
app.include_router(notifications.router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - failure path only
        return {"status": "error", "detail": str(exc)}
