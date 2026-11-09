"""
Configuración de la aplicación.
Maneja diferentes entornos: desarrollo, pruebas y producción.
"""

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Lee las variables de entorno desde el archivo .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Configuración básica de la aplicación
    app_name: str = "API de Películas"
    app_version: str = "1.0.0"

    # Configuración del entorno
    environment: Literal["development", "testing", "production"] = "development"

    # Configuración de la base de datos
    # Para SQLite: sqlite:///./peliculas.db
    # Para PostgreSQL: postgresql://usuario:password@localhost/dbname
    database_url: str = "sqlite:///./peliculas.db"

    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Configuración de CORS
    # En desarrollo puedes usar ["*"], en producción especifica los orígenes permitidos
    cors_origins: list[str] = ["*"]

    # Configuración de seguridad (para futuras mejoras)
    secret_key: str = "your-secret-key-here"  # Cambiar en producción
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Configuración de logging
    log_level: str = "INFO"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value:
            raise ValueError("DATABASE_URL no puede estar vacío")
        return value


# Crear una instancia global de Settings
settings = Settings()


# Opcional - Crear diferentes configuraciones para cada entorno
class DevelopmentSettings(Settings):
    """Configuración para el entorno de desarrollo."""

    debug: bool = True
    log_level: str = "DEBUG"


class TestingSettings(Settings):
    """Configuración para el entorno de pruebas."""

    database_url: str = "sqlite:///./test_peliculas.db"
    debug: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    """Configuración para el entorno de producción."""

    debug: bool = False
    log_level: str = "WARNING"

    # Agregar configuraciones específicas de producción
    # Cambiar a una base de datos más robusta (PostgreSQL, MySQL)
    # database_url: str = "postgresql://usuario:password@localhost/peliculas_prod"


def get_settings() -> Settings:
    """Retorna la configuración apropiada según el entorno."""

    env = settings.environment.lower()

    if env == "testing":
        return TestingSettings()
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()


def validate_settings():
    """Valida que todas las configuraciones necesarias estén presentes."""

    required_settings = ["database_url", "app_name"]
    for setting in required_settings:
        if not getattr(settings, setting, None):
            raise ValueError(f"Configuración requerida no encontrada: {setting}")
