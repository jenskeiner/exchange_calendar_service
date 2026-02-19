from fastapi import Depends, HTTPException, Request
from fastapi.security import SecurityScopes

from .auth import AnonymousSuperuser, AuthenticatedUser


async def authentication(_: Request) -> AuthenticatedUser:
    """Authenticate the user."""
    return AnonymousSuperuser()


async def authorization(
    security_scopes: SecurityScopes, user: AuthenticatedUser = Depends(authentication)
):
    """Authorize the user."""
    if "*" not in user.scopes:
        missing = set(security_scopes.scopes) - set(user.scopes)
        if missing:
            raise HTTPException(403, detail=f"Missing scopes: {missing}")
    return user
