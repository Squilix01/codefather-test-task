from fastapi import HTTPException, status

from app.uow.uow import UnitOfWork


class NotificationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_user_notifications(self, user_id: int):
        async with self.uow:
            return await self.uow.notifications.get_by_user_id(user_id=user_id)

    async def mark_as_read(self, notification_id: int, user_id: int) -> dict:
        async with self.uow:
            updated = await self.uow.notifications.mark_as_read(
                notification_id=notification_id,
                user_id=user_id,
            )
            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Сповіщення не знайдено",
                )

            await self.uow.commit()
            return {"message": "Позначено як прочитане"}
