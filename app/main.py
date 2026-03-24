from fastapi import FastAPI

from app import models as _models  # noqa: F401
from app.routers import auth

app = FastAPI(title="Finance Tracker API")

app.include_router(auth.router)
