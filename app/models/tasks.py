from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str


class TaskRead(BaseModel):
    id: str
    name: str
