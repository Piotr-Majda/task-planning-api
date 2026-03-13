from sqlalchemy import ForeignKey, Integer, String, Column
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tasks = relationship('Task', back_populates='user')

class Task(Base):
    __tablename__ = 'tasks'

    id= Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='tasks')
