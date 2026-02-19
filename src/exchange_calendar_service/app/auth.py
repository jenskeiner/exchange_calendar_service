from collections.abc import Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class AuthenticatedUser(Protocol):
    """Protocol model for an authenticated user."""

    @property
    def user_id(self) -> str: ...
    @property
    def scopes(self) -> Sequence[str]: ...


class AnonymousSuperuser:
    """An anonymous superuser.

    This user has all scopes. Used as default when actual authentication is disabled.
    """

    user_id: str = "anonymous"
    scopes: list[str] = ["*"]
