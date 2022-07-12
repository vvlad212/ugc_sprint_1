from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator


class Person(BaseModel):
    id: str
    full_name: str


class Genre(BaseModel):
    id: str
    name: str


class FilmByPersonModel(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float] = Field(
        ge=0,
        le=10,
    )

    @validator('imdb_rating')
    def set_imdb_rating(cls, rating):
        return rating or 0


class PersonFilmWork(BaseModel):
    id: str
    name: str


class ListResponseModel(BaseModel):
    records: Union[List[Person], List[Genre], List[FilmByPersonModel]]
    total_count: int
    current_page: int
    total_page: int
    page_size: int


class FilmListResponseModel(BaseModel):
    records: Union[List[Person], List[Genre], List[FilmByPersonModel]]
    total_count: int
    current_page: int
    total_page: int
    page_size: int
    message: str


class FilmRespModel(BaseModel):
    id: str
    imdb_rating: float
    genres: Optional[list] = Field(None, alias='genre')
    title: str
    description: Optional[str] = None
    director: Union[str, List[str]]
    actors: Optional[List[PersonFilmWork]] = None
    writers: Optional[List[PersonFilmWork]] = None


class FilmsResponseModel(BaseModel):
    total_count: int
    page_count: int
    page_number: int
    page_size: int
    records: List[FilmRespModel]
    message: str
