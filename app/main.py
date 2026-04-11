from fastapi import FastAPI
from app.api.routes_health import router as health_router
from app.api.routes_chat import router as chat_router
from app.api.routes_voice import router as voice_router
from app.api.routes_tts import router as tts_router


def create_app() -> FastAPI:
    app = FastAPI(title="NOVA", version="0.1.0")
    app.include_router(health_router)
    app.include_router(chat_router, prefix="/chat", tags=["chat"])
    app.include_router(voice_router, prefix="/voice", tags=["voice"])
    app.include_router(tts_router, prefix="/tts", tags=["tts"])
    return app


app = create_app()