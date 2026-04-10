from fastapi import FastAPI
from app.api.routes_health import router as health_router
from app.api.routes_chat import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI(title="NOVA", version="0.1.0")
    app.include_router(health_router)
    app.include_router(chat_router, prefix="/chat", tags=["chat"])
    return app


app = create_app()