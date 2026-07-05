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

    app_name: str = "TaskPlaningAPI"
    debug: bool = False
    db_url: str = ""
    db_password: str = ""
    db_name: str = ""
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_mintues: int = 15


config = Config() # type: ignore[call-arg]
