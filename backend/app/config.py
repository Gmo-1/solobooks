from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración global de la aplicación Solobooks."""

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/solobooks"
    APP_NAME: str = "Solobooks API"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
