from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Config(BaseSettings):

    def __init__(self) -> None:
        self.app_name = 'Task Scheduler API'


config = Config()
