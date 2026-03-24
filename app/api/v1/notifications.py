from typing import List

from fastapi import APIRouter, Depends

from app.api.depends import get_current_user, get_notification_service
from app.api.schemas.notifications_schema import (
    NotificationReadResponse,
    NotificationResponse,
)
from app.models.user import User
from app.services.notifications_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.get_user_notifications(user_id=current_user.id)


@router.patch("/{notification_id}/read", response_model=NotificationReadResponse)
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )
