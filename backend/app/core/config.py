from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "WIMSA Backend"
    debug: bool = True
    database_url: str = "postgresql://neondb_owner:npg_TxKoMVw2Nm4r@ep-sweet-field-appjav8z.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
