from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re

import bcrypt
from sqlalchemy import func, or_

from app.database.db import session_scope
from app.models.user_model import User
from app.services.log_service import LogService
from config import DEFAULT_ADMIN_PASSWORD, LEGACY_DEFAULT_ADMIN_PASSWORDS, ROLE_ADMIN, ROLE_USER


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class SessionUser:
    id: int
    username: str
    full_name: str
    email: str | None
    phone: str | None
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    @property
    def can_manage_users(self) -> bool:
        return self.is_admin

    @property
    def can_delete(self) -> bool:
        return self.is_admin

    @property
    def can_edit(self) -> bool:
        return self.is_admin

    @property
    def can_import_export(self) -> bool:
        return self.is_admin

    @property
    def can_manage_conventions(self) -> bool:
        return self.is_admin

    @property
    def is_viewer(self) -> bool:
        return not self.is_admin


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
    def _session_user(user: User) -> SessionUser:
        return SessionUser(user.id, user.username, user.full_name, user.email, user.phone, user.role)

    @staticmethod
    def _normalize_email(email: str | None) -> str | None:
        value = (email or "").strip().lower()
        return value or None

    @staticmethod
    def _find_duplicate(session, username: str, email: str | None, exclude_user_id: int | None = None) -> str | None:
        username_query = session.query(User).filter(func.lower(User.username) == username.lower())
        if exclude_user_id is not None:
            username_query = username_query.filter(User.id != exclude_user_id)
        if username_query.first():
            return "Ce nom d'utilisateur est déjà utilisé."

        if email:
            email_query = session.query(User).filter(func.lower(User.email) == email.lower())
            if exclude_user_id is not None:
                email_query = email_query.filter(User.id != exclude_user_id)
            if email_query.first():
                return "Cet email est déjà utilisé."
        return None

    @staticmethod
    def validate_registration(data: dict) -> dict:
        cleaned = {
            "full_name": (data.get("full_name") or "").strip(),
            "username": (data.get("username") or "").strip(),
            "email": AuthService._normalize_email(data.get("email")),
            "phone": (data.get("phone") or "").strip() or None,
            "password": data.get("password") or "",
            "confirm_password": data.get("confirm_password") or "",
        }
        if not cleaned["full_name"] or not cleaned["username"] or not cleaned["email"] or not cleaned["password"]:
            raise ValueError("Veuillez remplir tous les champs obligatoires.")
        if not EMAIL_PATTERN.match(cleaned["email"]):
            raise ValueError("Veuillez saisir un email valide.")
        if len(cleaned["password"]) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
        if cleaned["password"] != cleaned["confirm_password"]:
            raise ValueError("Les mots de passe ne correspondent pas.")
        return cleaned

    @staticmethod
    def register_user(data: dict) -> SessionUser:
        cleaned = AuthService.validate_registration(data)
        with session_scope() as session:
            duplicate = AuthService._find_duplicate(session, cleaned["username"], cleaned["email"])
            if duplicate:
                raise ValueError(duplicate)
            user = User(
                full_name=cleaned["full_name"],
                username=cleaned["username"],
                email=cleaned["email"],
                phone=cleaned["phone"],
                password_hash=AuthService.hash_password(cleaned["password"]),
                role=ROLE_USER,
                is_active=True,
            )
            session.add(user)
            session.flush()
            LogService.log(session, user.id, "Register", "user", user.id, "Création du compte utilisateur")
            return AuthService._session_user(user)

    @staticmethod
    def login(identifier: str, password: str) -> tuple[SessionUser | None, str | None, bool]:
        identifier = identifier.strip()
        if not identifier or not password:
            return None, "Veuillez saisir votre identifiant et votre mot de passe.", False
        identifier_lower = identifier.lower()
        with session_scope() as session:
            user = (
                session.query(User)
                .filter(or_(func.lower(User.username) == identifier_lower, func.lower(User.email) == identifier_lower))
                .first()
            )
            if not user:
                return None, "Identifiant ou mot de passe incorrect.", False
            if not user.is_active:
                return None, "Ce compte est désactivé. Contactez un administrateur.", False
            if not AuthService.verify_password(password, user.password_hash):
                return None, "Identifiant ou mot de passe incorrect.", False
            user.last_login = datetime.now().isoformat(timespec="seconds")
            LogService.log(session, user.id, "Login", "user", user.id, "Connexion réussie")
            default_password = any(
                AuthService.verify_password(default, user.password_hash)
                for default in (DEFAULT_ADMIN_PASSWORD, *LEGACY_DEFAULT_ADMIN_PASSWORDS)
            )
            return (
                AuthService._session_user(user),
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
