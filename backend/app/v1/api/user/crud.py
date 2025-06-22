from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password
from app.core.auth import get_refresh_token_expire_time
from .schema import UserCreate, UserUpdate

class UserCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        try:
            db_user = User(
                username=user_data.username,
                password_hash=hash_password(user_data.password),
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=True
            )
            self.db.add(db_user)
            await self.db.flush()
            # No need for commit/rollback here as it's handled by session
            return db_user
        except IntegrityError:
            raise ValueError("Username already exists")

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_users(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        result = await self.db.execute(query.order_by(User.created_at.desc()))
        return list(result.scalars().all())
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        update_data = user_data.model_dump(exclude_unset=True)
        
        if not update_data:
            # Nothing to update
            return await self.get_user_by_id(user_id)
            
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
            .returning(User)
        )
        
        updated_user = result.scalar_one_or_none()
        if updated_user:
            await self.db.commit()
        else:
            await self.db.rollback()
            
        return updated_user

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user (hard delete)"""
        result = await self.db.execute(
            delete(User).where(User.id == user_id)
        )
        
        if result.rowcount > 0:
            await self.db.commit()
            return True
        else:
            await self.db.rollback()
            return False

    async def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate user (soft delete)"""
        return await self.update_user(user_id, UserUpdate(is_active=False))

    async def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activate user"""
        return await self.update_user(user_id, UserUpdate(is_active=True))

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await self.get_user_by_username(username)
        
        if not user or not user.is_active:
            return None
            
        if not verify_password(password, user.password_hash):
            return None
            
        return user

    async def update_password(self, user_id: UUID, new_password: str) -> Optional[User]:
        """Update user password"""
        password_hash = hash_password(new_password)
        
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash, updated_at=datetime.utcnow())
            .returning(User)
        )
        
        updated_user = result.scalar_one_or_none()
        if updated_user:
            await self.db.commit()
        else:
            await self.db.rollback()
            
        return updated_user

    async def store_refresh_token(self, user_id: UUID, refresh_token: str) -> bool:
        """Store refresh token for user"""
        expires_at = get_refresh_token_expire_time()
        
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                refresh_token=refresh_token,
                refresh_token_expires_at=expires_at,
                updated_at=datetime.utcnow()
            )
        )
        
        if result.rowcount > 0:
            await self.db.commit()
            return True
        else:
            await self.db.rollback()
            return False

    async def get_user_by_refresh_token(self, refresh_token: str) -> Optional[User]:
        """Get user by valid refresh token"""
        result = await self.db.execute(
            select(User).where(
                User.refresh_token == refresh_token,
                User.refresh_token_expires_at > datetime.utcnow(),
                User.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, user_id: UUID) -> bool:
        """Revoke user's refresh token"""
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                refresh_token=None,
                refresh_token_expires_at=None,
                updated_at=datetime.utcnow()
            )
        )
        
        if result.rowcount > 0:
            await self.db.commit()
            return True
        else:
            await self.db.rollback()
            return False

    async def get_users_by_role(self, role: UserRole, is_active: bool = True) -> List[User]:
        """Get users by role"""
        result = await self.db.execute(
            select(User).where(
                User.role == role,
                User.is_active == is_active
            ).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

def get_user_crud(db: AsyncSession) -> UserCRUD:
    """Get UserCRUD instance"""
    return UserCRUD(db)
