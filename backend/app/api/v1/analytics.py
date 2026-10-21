from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_order_repository
from app.repositories.order import OrderRepository
from app.schemas.analytics import AnalyticsPublic
from app.services.order import OrderService
from app.models.user import User


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsPublic)
async def get_analytics(order_repo: OrderRepository = Depends(get_order_repository),
                        _current_user: User = Depends(get_current_user)):
    service = OrderService(order_repo)
    return await service.get_analytics()
