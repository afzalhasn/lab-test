from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import UserCreate
from passlib.context import CryptContext
from app.core.security import hash_password, verify_password
from uuid import UUID

class UserCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def create_user(self, user: UserCreate) -> User:
        db_user = User(
            username=user.username,
            password_hash=hash_password(user.password),
            full_name=user.full_name,
            role=user.role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

# # Create a new user
# def create_user(db: Session, user: UserCreate) -> User:
#     db_user = User(
#         username=user.username,
#         password_hash=hash_password(user.password),
#         full_name=user.full_name,
#         role=user.role
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# # Authenticate a user
# def authenticate_user(db: Session, username: str, password: str) -> User | None:
#     user = db.query(User).filter(User.username == username).first()
#     if not user or not verify_password(password, user.password_hash):
#         return None
#     return user

# # Get user by ID
# def get_user_by_id(db: Session, user_id: UUID) -> User | None:
#     return db.query(User).filter(User.id == user_id).first()
