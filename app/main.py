from fastapi import FastAPI
from .database import init_db
from .routes import router

app = FastAPI(title="SMS (simple)")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(router)
