import uuid

from fastapi_users import schemas

from app.models.user import UserRole


class UserRead(schemas.BaseUser[uuid.UUID]):
    role: UserRole


class UserCreate(schemas.BaseUserCreate):
    role: UserRole = UserRole.member


class UserUpdate(schemas.BaseUserUpdate):
    pass
