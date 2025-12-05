from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..models import User, UserProfile
from ...utils.security import get_password_hash, verify_password


class UserRepository:
    """Repository for user-related database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_user(self, email: str, password: str, first_name: str = None, last_name: str = None) -> User:
        """Create a new user."""
        password_hash = get_password_hash(password)
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        user = await self.get_user_by_email(email)
        if user and verify_password(password, user.password_hash):
            return user
        return None
    
    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information."""
        user = await self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
        return user
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            await self.session.commit()
            return True
        return False