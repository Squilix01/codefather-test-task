from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, func, text

from app.database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    liked_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
