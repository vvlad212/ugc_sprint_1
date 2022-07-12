import math
from enum import Enum
from typing import List, Union

from api.errors.httperrors import FilmHTTPNotFoundError
from api.models.resp_models import FilmRespModel, FilmsResponseModel
from fastapi import APIRouter, Depends, Path, Query, Header
from pydantic import Required

from api.views_decorators import check_roles
from services.auth import AuthService, get_auth_service
from services.films import FilmService, get_film_service

router = APIRouter()


@router.get(
    '/{film_id}',
    response_model=FilmRespModel,
    tags=["films"],
    responses={
        200: {
            "description": "Film requested by ID",
        },
        404: {
            "description": "Not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Film(s) not found"}
                }
            },
        },
    },
)
async def film_details(
        film_id: str = Path(
            default=Required,
            title="Film id",
            description="UUID of the film to get",
            example="2a090dde-f688-46fe-a9f4-b781a985275e",
        ),
        film_service: FilmService = Depends(get_film_service)
) -> FilmRespModel:
    """
    Get film detail info by film uuid.
    """
    film = await film_service.get_by_id(film_id)
    if not film:
        raise FilmHTTPNotFoundError
    return FilmRespModel.parse_obj(film.dict())


class FilmRating(str, Enum):
    desc = "desc_rating"
    asc = "asc_rating"


@router.get(
    '/',
    response_model=FilmsResponseModel,
    tags=["films"],
    responses={
        200: {
            "description": "Paginated filtered films array.",
        },
    }
)
@check_roles()
async def get_films_list(
        token=Header(
            default=None,
            description="JWT token"),
        name: Union[str, None] = Query(
            default=None,
            title="Name of the film(s)",
            description="Filter by film name.",
            min_length=3,
        ),
        genres: Union[List[str], None] = Query(
            default=None,
            title="Film(s) genres",
            description="Filter by film genre.",
        ),
        sort: FilmRating = Query(
            default=FilmRating.desc,
            title="Film(s) genres",
            description="Sorting order by imdb rating.",
        ),
        page_number: int = Query(
            default=1,
            gt=0,
            description="Pagination page number.",
        ),
        page_size: int = Query(
            default=20,
            gt=0,
            description="Pagination size number.",
        ),
        user_roles=Depends(),
        film_service: FilmService = Depends(get_film_service),
        auth_service: AuthService = Depends(get_auth_service)
) -> FilmsResponseModel:
    """
    Get filtered films list with pagination.
    """

    total_count, films = await film_service.get_list(
        roles=user_roles,
        name=name,
        genres=genres,
        sort=sort,
        page_number=page_number,
        page_size=page_size
    )

    films_res = [FilmRespModel.parse_obj(film.dict()) for film in films]

    message = f'Response '
    if not 'subscription' in user_roles:
        if 'failed' in user_roles:
            message += f'authorization not verified response limited. Authorization service is fail.'
        elif 'unauthorized' in user_roles:
            message += f'authorization not verified response limited.'
        elif 'not_subscription' in user_roles:
            message += f'for user without subscription'
        else:
            message += f'for user without {user_roles}'
    else:
        message += "for subscribed user"

    return FilmsResponseModel(
        total_count=total_count,
        page_count=math.ceil(total_count / page_size),
        page_number=page_number,
        page_size=page_size,
        records=films_res,
        message=message
    )
