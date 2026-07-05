from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


load_dotenv()


class Config(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "TaskPlaningAPI"
    DEBUG: bool = False
    DB_URL: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""
    SECRET_KEY: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINTUES: int = 15


config = Config() # type: ignore[call-arg]
