from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text

from app.database.db import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
