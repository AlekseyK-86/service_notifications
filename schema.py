from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class NotificationBase(BaseModel):
    user_id: int = Field(
        ge=1,
        description="ID пользователя, целое число=1"
    )
    notification: str = Field(
        min_length=1,
        max_length=500,
        description="Текст сообщения"
    )
    send_at: datetime = Field(
        description="Когда отправить сообщение",
        examples=["2025-12-28"]
    )  # ISO8601, напр. 2025-09-01T12:00:00Z


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    """Схема для частичного обновления (PATCH)"""
    notification: str | None = Field(
        min_length=1,
        max_length=500,
        default=None
    )
    send_at: datetime | None


class NotificationResponse(NotificationBase):
    id: UUID
