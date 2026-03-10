from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    BACKEND_HOST: str = "http://127.0.0.1:8000"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    CODE_GEN_MAX_RETRIES: int = 3


settings = Settings() # type: ignore
