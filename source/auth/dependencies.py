from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from source.db.redis import token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from source.db.main import get_sessiion
from .services import UserService
from source.db.models import User
from typing import List
from source.errors import (
    InvalidToken,
    AccessTokenRequired,
    RefreshTokenRequired,
    InsufficientPermission,
    AccountNotVerified
)

user_service = UserService()


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = self.token_valid(token)

        if not token_data:
            raise InvalidToken()

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()

        print("Token JTI:", token_data["jti"])
        print("Is in blocklist?", await token_in_blocklist(token_data["jti"]))

        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> dict | None:
        return decode_token(token)

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Please override this method in child class")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        # 👇 This is called from parent during token validation
        if token_data.get("refresh", False):
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_sessiion),
):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user=Depends(get_current_user)):
        if not current_user.isverified:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
