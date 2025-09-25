from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import init_db
from .routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(title="SMS (simple)", lifespan=lifespan)
app.include_router(router)
