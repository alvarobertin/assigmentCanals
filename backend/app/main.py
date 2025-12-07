from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base
from app.routers import orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - creates database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Order Management API",
    description="E-commerce order management",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(orders.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

