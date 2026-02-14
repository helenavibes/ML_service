from fastapi import APIRouter

from app.api.v1.endpoints import auth, balance, models, predict, history

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(balance.router, prefix="/balance", tags=["balance"])
api_router.include_router(models.router, prefix="/models", tags=["ml-models"])
api_router.include_router(predict.router, prefix="/predict", tags=["predictions"])
api_router.include_router(history.router, prefix="/history", tags=["history"])

@api_router.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "service": "ML Service Platform"}
