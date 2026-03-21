from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from enum import StrEnum


load_dotenv()


class Config(BaseSettings):

    app_name: str = "TaskSchedulerAPI"
    debug: bool = False
    db_user: str = ""
    db_password: str = ""
    db_name: str = "task.db"

    @property
    def db_url(self):
        return f"sqlite:///./{self.db_name}"


config = Config()


class TaskStatus(StrEnum):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class TaskPriority(StrEnum):
    BLOCKER = 'blocker'
    CRITICAL = 'critical'
    MAJOR = 'major'
    MINOR = 'minor'
