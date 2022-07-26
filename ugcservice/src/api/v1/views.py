import datetime
import logging
from urllib import response
from uuid import UUID

from api.errors.httperrors import StorageInternalError
from fastapi import APIRouter, Depends, Response, status
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel, Field

from services.moviewatchmark import MovieWatchMarkService, get_watchmark_service

logger = logging.getLogger(__name__)

router = APIRouter()


class PostMovieWatchMarkReqBody(BaseModel):
    film_id: UUID = Field(example="4f91f972-f071-4ac9-9c31-55f7ee3bc8aa")
    user_id: UUID = Field(example="75c89c44-e146-4918-8368-9cc78c48f491", default=None)
    timestamp: datetime.time = Field(
        description="Time in ISO 8601 format",
        example="01:23:55.003"
    )


@router.post(
    '/viewlabel',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error occurred while trying to save movie watch mark."}
                }
            },
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "content": {
                "application/json": {
                    "example": {"detail": "Too Many Requests"}
                }
            },
        }
    },
    tags=["Movie Labels"],
    dependencies=[Depends(RateLimiter(times=20, seconds=10))]
)
async def save_movie_watchmark(
    body_req: PostMovieWatchMarkReqBody,
    movies_watchmark_service: MovieWatchMarkService = Depends(
        get_watchmark_service
    )
) -> None:
    """
    Send movie view label(timestamp) to UGC store.
    """
    if await movies_watchmark_service.save_watchmark(
        film_id=body_req.film_id,
        user_id=body_req.user_id,
        timestamp=body_req.timestamp
    ):
        return None
    else:
        raise StorageInternalError
