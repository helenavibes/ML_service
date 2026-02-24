from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router
from app.database.database import engine, init_db
from app.models.db.base import Base

# Создаем таблицы (если еще не созданы)
Base.metadata.create_all(bind=engine)

# Инициализируем БД начальными данными (демо-пользователи, модели)
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Подключаем API роуты (ПРЕДИКАТЕЛЬНО - сначала API)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Подключаем web роуты (ПОСЛЕ API)
from app.web.routes import router as web_router
app.include_router(web_router)

@app.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
