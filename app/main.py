from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models as _models  # noqa: F401
from app.core.exceptions import AppException
from app.routers import auth, category, summary, transaction

app = FastAPI(title="Finance Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        headers=dict(exc.headers) if exc.headers else None,
        content={
            "error": "http_error",
            "message": str(exc.detail),
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    message = "; ".join(f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors)
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": message,
            "detail": errors,
            "status_code": 422,
        },
    )


app.include_router(auth.router)
app.include_router(category.router)
app.include_router(transaction.router)
app.include_router(summary.router)
