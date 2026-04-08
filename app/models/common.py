from typing import Annotated, Optional
from pydantic import BaseModel, StringConstraints


class SearchQuery(BaseModel):
    search: Annotated[Optional[str], StringConstraints(
        min_length=1, 
        max_length=100, 
        strip_whitespace=True, 
        pattern=r'^[^<>\"\\]*$'
        )] = None

