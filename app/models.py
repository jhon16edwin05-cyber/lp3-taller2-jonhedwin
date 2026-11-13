"""
Modelos de datos usando SQLModel.
Define la estructura de las tablas de la base de datos.
SQLModel combina SQLAlchemy con Pydantic para validación automática.
"""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import field_validator
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, index=True)
    correo: str = Field(unique=True, max_length=150, index=True)
    fecha_registro: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    favoritos: List["Favorito"] = Relationship(back_populates="usuario")

    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre={self.nombre}, correo={self.correo})>"

    @property
    def cantidad_favoritos(self) -> int:
        return len(self.favoritos) if self.favoritos else 0

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Correo electrónico inválido")
        return v.lower()


class Pelicula(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(max_length=200, index=True)
    director: str = Field(max_length=150)
    genero: str = Field(max_length=100)
    duracion: int = Field(description="Duración en minutos")
    año: int = Field(ge=1888, le=2100)
    clasificacion: str = Field(max_length=10)
    sinopsis: Optional[str] = Field(default=None, max_length=1000)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    favoritos: List["Favorito"] = Relationship(back_populates="pelicula")


class Favorito(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id")
    id_pelicula: int = Field(foreign_key="pelicula.id")
    fecha_marcado: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    usuario: Optional[Usuario] = Relationship(back_populates="favoritos")
    pelicula: Optional[Pelicula] = Relationship(back_populates="favoritos")

    __table_args__ = (
        UniqueConstraint("id_usuario", "id_pelicula", name="unique_user_movie"),
    )


