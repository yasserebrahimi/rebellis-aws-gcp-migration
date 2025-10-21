import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User
from src.api.schemas.auth import UserCreate
from src.core.security import create_token

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _hash(self, password: str) -> str:
        """Hash password using bcrypt with salt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

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
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None

    async def create_access_token(self, user: User) -> str:
        return create_token({"sub": str(user.id), "email": user.email})
