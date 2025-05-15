import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    SESSION_MIDDLEWARE_SECRET_KEY: str
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_POSTGRES_USER: str
    KEYCLOAK_POSTGRES_PASSWORD: str
    KEYCLOAK_POSTGRES_DB: str
    KEYCLOAK_DB_PORT: str
    KEYCLOAK_ADMIN: str
    KEYCLOAK_ADMIN_PASSWORD: str
    KEYCLOAK_PORT: str
    FRONT_URL: str
    SSO_SESSION_MAX_LIFESPAN: int
    SSO_SESSION_IDLE_TIMEOUT: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )




settings = Settings()

#print(settings.model_dump())

def get_db_url():
    # print("DB_HOST:", settings.DB_HOST)
    # print("DB_PORT:", settings.DB_PORT)
    # print("DB_NAME:", settings.DB_NAME)
    # print("DB_USER:", settings.DB_USER)
    # print("DB_PASSWORD:", settings.DB_PASSWORD)
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}



