from typing import Annotated, Optional
from pydantic import AfterValidator, BaseModel, Field, StringConstraints
from app.domain.enums import SortBy, OrderBy


class SearchQuery(BaseModel):
    search: Annotated[Optional[str], StringConstraints(
        min_length=1, 
        max_length=100, 
        strip_whitespace=True, 
        pattern=r'^[^<>\"\\]*$'
        )] = None


def ensure_search_format(search: Optional[str]) -> Optional[str]:
    if search is None:
        return search
    return SearchQuery(search=search).search


class SearchQueryParams(BaseModel):
    search: Annotated[Optional[str], AfterValidator(ensure_search_format)] = Field(None, description="Search query that contains in name")
    sort: SortBy = Field(SortBy.NAME, description="Attr on which you want to sort by")
    order: OrderBy = Field(OrderBy.ASC, description="Sort by this order ascending or descending")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Users per page")
    
    @property
    def skip(self):
        return (self.page - 1) * self.limit
