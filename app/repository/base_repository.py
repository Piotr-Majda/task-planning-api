from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import ColumnElement, desc
from app.db.schema import Base
from app.domain.enums import OrderBy, SortBy


T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self._db = db
        self._model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        column = getattr(self._model, 'id', None)
        if column is None:
            raise ValueError(f"Model {self._model} not has id field: {id}")
        return self._db.query(self._model).filter(column == id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        filters: List[ColumnElement] | None = None,
        sort_by: SortBy | None = None,
        order=OrderBy.ASC
    ) -> List[T]:
        query = self._db.query(self._model)

        if filters:
            query = query.filter(*filters)

        if sort_by:
            column = getattr(self._model, sort_by, None)
            if column is None:
                raise ValueError(f"Model {self._model} not has sort field: {sort_by}")
            query = query.order_by(desc(column) if order == OrderBy.DESC else column)

        return query.offset(skip).limit(limit).all()
    
    def create(self, entity: T) -> T:
        self._db.add(entity)
        self._db.commit()
        self._db.refresh(entity)
        return entity
    
    def update(self, entity: T) -> T:
        self._db.add(entity)
        self._db.commit()
        self._db.refresh(entity)
        return entity
    
    def delete(self, entity: T) -> None:
        self._db.delete(entity)
        self._db.commit()
