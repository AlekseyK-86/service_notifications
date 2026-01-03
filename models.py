from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID

from database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    notification: Mapped[str] = mapped_column(nullable=False)
    send_at: Mapped[datetime] = mapped_column(nullable=False)
