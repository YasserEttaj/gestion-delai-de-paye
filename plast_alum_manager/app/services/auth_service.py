from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import bcrypt
from sqlalchemy import or_

from app.database.db import session_scope
from app.models.user_model import User
from app.services.log_service import LogService
from config import DEFAULT_ADMIN_PASSWORD, ROLE_ACCOUNTANT, ROLE_ADMIN, ROLE_VIEWER


@dataclass(frozen=True)
class SessionUser:
    id: int
    username: str
    full_name: str
    email: str | None
    role: str

    @property
    def can_manage_users(self) -> bool:
        return self.role == ROLE_ADMIN

    @property
    def can_delete(self) -> bool:
        return self.role == ROLE_ADMIN

    @property
    def can_edit(self) -> bool:
        return self.role in {ROLE_ADMIN, ROLE_ACCOUNTANT}

    @property
    def can_import_export(self) -> bool:
        return self.role in {ROLE_ADMIN, ROLE_ACCOUNTANT}

    @property
    def is_viewer(self) -> bool:
        return self.role == ROLE_VIEWER


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except ValueError:
            return False

    @staticmethod
    def login(identifier: str, password: str) -> tuple[SessionUser | None, str | None, bool]:
        identifier = identifier.strip()
        if not identifier or not password:
            return None, "Veuillez saisir l'utilisateur et le mot de passe.", False
        with session_scope() as session:
            user = (
                session.query(User)
                .filter(or_(User.username == identifier, User.email == identifier))
                .first()
            )
            if not user or not user.is_active:
                return None, "Compte introuvable ou désactivé.", False
            if not AuthService.verify_password(password, user.password_hash):
                return None, "Mot de passe incorrect.", False
            user.last_login = datetime.now().isoformat(timespec="seconds")
            LogService.log(session, user.id, "Login", "user", user.id, "Connexion réussie")
            default_password = AuthService.verify_password(DEFAULT_ADMIN_PASSWORD, user.password_hash)
            return (
                SessionUser(user.id, user.username, user.full_name, user.email, user.role),
                None,
                default_password and user.username == "admin",
            )

    @staticmethod
    def logout(user_id: int) -> None:
        with session_scope() as session:
            LogService.log(session, user_id, "Logout", "user", user_id, "Déconnexion")

    @staticmethod
    def change_password(user_id: int, new_password: str) -> None:
        with session_scope() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("Utilisateur introuvable.")
            user.password_hash = AuthService.hash_password(new_password)
            LogService.log(session, user_id, "Edit user", "user", user_id, "Changement de mot de passe")
