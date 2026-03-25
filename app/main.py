from fastapi import FastAPI

from app import models as _models  # noqa: F401
from app.routers import auth, category, transaction

app = FastAPI(title="Finance Tracker API")

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(transaction.router)
