from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.core.auth import decode_token, TokenType
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import select

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """Authentication middleware for automatic token validation"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        """Process request and validate authentication if needed"""
        
        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Try to extract and validate token
        token = self._extract_token(request)
        
        if token:
            try:
                # Validate token and add user to request state
                user = await self._validate_token(token, request)
                request.state.current_user = user
            except HTTPException:
                # Token is invalid, let the endpoint handle it
                pass
        
        return await call_next(request)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (doesn't require authentication)"""
        public_paths = [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/v1/auth/login",
            "/v1/auth/signup",
            "/v1/auth/refresh",
            "/static",
            "/health"
        ]
        
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract token from Authorization header or cookies"""
        # Try Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        
        # Fallback to cookie
        return request.cookies.get("access_token")
    
    async def _validate_token(self, token: str, request: Request) -> User:
        """Validate token and return user"""
        try:
            # Decode token
            payload = decode_token(token, TokenType.ACCESS)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            
            # Get database session
            db_gen = get_db()
            db = await db_gen.__anext__()
            
            try:
                # Get user from database
                result = await db.execute(
                    select(User).where(User.id == user_id, User.is_active == True)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
                
                return user
                
            finally:
                await db_gen.aclose()
                
        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

async def auth_middleware(request: Request, call_next):
    """Functional middleware for authentication"""
    middleware = AuthMiddleware(None)
    return await middleware(request, call_next) 