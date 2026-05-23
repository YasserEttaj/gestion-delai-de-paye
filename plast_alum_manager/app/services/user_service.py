from __future__ import annotations

from sqlalchemy import or_

from app.database.db import session_scope
from app.models.user_model import User
from app.services.auth_service import AuthService
from app.services.log_service import LogService
from config import ROLE_ADMIN, ROLE_USER


VALID_ROLES = {ROLE_ADMIN, ROLE_USER}


class UserService:
    @staticmethod
    def list_users(search: str = "") -> list[User]:
        with session_scope() as session:
            query = session.query(User)
            if search:
                like = f"%{search}%"
                query = query.filter(or_(User.username.ilike(like), User.full_name.ilike(like), User.email.ilike(like), User.phone.ilike(like)))
            return list(query.order_by(User.created_at.desc()).all())

    @staticmethod
    def create_user(data: dict, actor_id: int | None) -> User:
        with session_scope() as session:
            username = data["username"].strip()
            full_name = data["full_name"].strip()
            email = (data.get("email") or "").strip().lower() or None
            if not full_name or not username:
                raise ValueError("Nom complet et utilisateur sont obligatoires.")
            duplicate = AuthService._find_duplicate(session, username, email)
            if duplicate:
                raise ValueError(duplicate)
            if data["role"] not in VALID_ROLES:
                raise ValueError("Rôle utilisateur invalide.")
            if len(data["password"]) < 8:
                raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                phone=(data.get("phone") or "").strip() or None,
                password_hash=AuthService.hash_password(data["password"]),
                role=data["role"],
                is_active=bool(data.get("is_active", True)),
            )
            session.add(user)
            session.flush()
            LogService.log(session, actor_id, "Add user", "user", user.id, user.username)
            return user

    @staticmethod
    def update_user(user_id: int, data: dict, actor_id: int | None) -> None:
        with session_scope() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("Utilisateur introuvable.")
            username = data["username"].strip()
            full_name = data["full_name"].strip()
            email = (data.get("email") or "").strip().lower() or None
            if not full_name or not username:
                raise ValueError("Nom complet et utilisateur sont obligatoires.")
            duplicate = AuthService._find_duplicate(session, username, email, exclude_user_id=user_id)
            if duplicate:
                raise ValueError(duplicate)
            if data["role"] not in VALID_ROLES:
                raise ValueError("Rôle utilisateur invalide.")
            user.username = data["username"].strip()
            user.full_name = full_name
            user.email = email
            user.phone = (data.get("phone") or "").strip() or None
            user.role = data["role"]
            user.is_active = bool(data.get("is_active", True))
            if data.get("password"):
                if len(data["password"]) < 8:
                    raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
                user.password_hash = AuthService.hash_password(data["password"])
            LogService.log(session, actor_id, "Edit user", "user", user.id, user.username)

    @staticmethod
    def delete_user(user_id: int, actor_id: int | None) -> None:
        if user_id == actor_id:
            raise ValueError("Vous ne pouvez pas supprimer votre propre compte.")
        with session_scope() as session:
            user = session.get(User, user_id)
            if not user:
                raise ValueError("Utilisateur introuvable.")
            LogService.log(session, actor_id, "Delete user", "user", user.id, user.username)
            session.delete(user)
