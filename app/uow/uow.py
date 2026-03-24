from app.database.session import session_factory
from app.repositories.notification import NotificationRepository
from app.repositories.user import UserRepository
from app.repositories.post import PostRepository
from app.repositories.like import LikeRepository

class UnitOfWork:
    def __init__(self):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.notifications = NotificationRepository(self.session)
        self.users = UserRepository(self.session)
        self.posts = PostRepository(self.session)
        self.likes = LikeRepository(self.session)
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.session.commit() 
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()