from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class ResourceNotFoundException(BaseAPIException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found with identifier: {identifier}"
        )

class ValidationException(BaseAPIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class DuplicateResourceException(BaseAPIException):
    def __init__(self, resource: str, field: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with this {field} already exists"
        )

class DatabaseException(BaseAPIException):
    def __init__(self, operation: str, detail: str = ""):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database {operation} failed: {detail if detail else 'Unknown error'}"
        )

class AuthenticationException(BaseAPIException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        ) 