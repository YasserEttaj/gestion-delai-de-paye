from __future__ import annotations

from sqlalchemy import or_

from app.database.db import session_scope
from app.models.user_model import User
from app.services.auth_service import AuthService
from app.services.log_service import LogService


class UserService:
    @staticmethod
    def list_users(search: str = "") -> list[User]:
        with session_scope() as session:
            query = session.query(User)
            if search:
                like = f"%{search}%"
                query = query.filter(or_(User.username.ilike(like), User.full_name.ilike(like), User.email.ilike(like)))
            return list(query.order_by(User.created_at.desc()).all())

    @staticmethod
    def create_user(data: dict, actor_id: int | None) -> User:
        with session_scope() as session:
            if session.query(User).filter_by(username=data["username"]).first():
                raise ValueError("Nom d'utilisateur déjà utilisé.")
            if data.get("email") and session.query(User).filter_by(email=data["email"]).first():
                raise ValueError("Email déjà utilisé.")
            user = User(
                username=data["username"].strip(),
                full_name=data["full_name"].strip(),
                email=data.get("email") or None,
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
            duplicate = session.query(User).filter(User.id != user_id, User.username == data["username"]).first()
            if duplicate:
                raise ValueError("Nom d'utilisateur déjà utilisé.")
            if data.get("email"):
                duplicate_email = session.query(User).filter(User.id != user_id, User.email == data["email"]).first()
                if duplicate_email:
                    raise ValueError("Email déjà utilisé.")
            user.username = data["username"].strip()
            user.full_name = data["full_name"].strip()
            user.email = data.get("email") or None
            user.role = data["role"]
            user.is_active = bool(data.get("is_active", True))
            if data.get("password"):
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
