from http import HTTPStatus

from fastapi import HTTPException


StorageInternalError = HTTPException(
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    detail='UGC storage error'
)
