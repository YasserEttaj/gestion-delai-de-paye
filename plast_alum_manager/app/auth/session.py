from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from config import ROLE_ADMIN

if TYPE_CHECKING:
    from app.services.auth_service import SessionUser


class AuthSession:
    _current_user: ClassVar["SessionUser | None"] = None

    @classmethod
    def start(cls, user: "SessionUser") -> None:
        cls._current_user = user

    @classmethod
    def clear(cls) -> None:
        cls._current_user = None

    @classmethod
    def current_user(cls) -> "SessionUser | None":
        return cls._current_user

    @classmethod
    def require_user(cls) -> "SessionUser":
        if cls._current_user is None:
            raise PermissionError("Connexion requise.")
        return cls._current_user

    @classmethod
    def require_admin(cls) -> "SessionUser":
        user = cls.require_user()
        if user.role != ROLE_ADMIN:
            raise PermissionError("Accès administrateur requis.")
        return user
