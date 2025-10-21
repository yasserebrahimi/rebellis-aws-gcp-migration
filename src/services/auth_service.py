import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User
from src.api.schemas.auth import UserCreate
from src.core.security import create_token

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _hash(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    async def get_user_by_email(self, email: str):
        q = await self.db.execute(select(User).where(User.email == email))
        return q.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int):
        q = await self.db.execute(select(User).where(User.id == user_id))
        return q.scalar_one_or_none()

    async def create_user(self, data: UserCreate) -> User:
        user = User(email=data.email, hashed_password=self._hash(data.password), full_name=data.full_name)
        self.db.add(user)
        await self.db.flush()
        return user

    async def authenticate_user(self, email: str, password: str):
        user = await self.get_user_by_email(email)
        if user and user.hashed_password == self._hash(password):
            return user
        return None

    async def create_access_token(self, user: User) -> str:
        return create_token({"sub": str(user.id), "email": user.email})
