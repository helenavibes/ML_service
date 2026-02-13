from fastapi import APIRouter

api_router = APIRouter()

# Здесь будут подключаться роутеры пользователей, транзакций, ML моделей
# @api_router.include_router(users.router, prefix="/users", tags=["users"])
# @api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
# @api_router.include_router(ml_models.router, prefix="/models", tags=["ml_models"])
# @api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])

@api_router.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "service": "ML Service Platform"}
