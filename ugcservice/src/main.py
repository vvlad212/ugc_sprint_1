import logging

import aioredis
import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter

from api.v1 import views
from core.config import Config
from db import kafka

logger = logging.getLogger(__name__)

app = FastAPI(
    docs_url='/ugcservice_api/openapi',
    openapi_url='/ugcservice_api/openapi.json',
    default_response_class=ORJSONResponse,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="UGC service api",
        version="1.0.0",
        description="This is the first version of the user generated content service api.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
async def startup():
    redis_uri = f"redis://{Config().REDIS_LIMITER_HOST}:{Config().REDIS_LIMITER_PORT}/1"
    logger.info(f"Connecting to Redis {redis_uri}")
    redis = await aioredis.from_url(
        redis_uri,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(redis)

    # logger.info(f"Connecting to Kafka {Config().KAFKA_HOST}:{Config().KAFKA_PORT}")
    # kafka.kafka = AIOKafkaProducer(
    #     bootstrap_servers=f'{Config().KAFKA_HOST}:{Config().KAFKA_PORT}'
    # )
    # await kafka.kafka.start()


@app.on_event("shutdown")
async def shutdown():
    await FastAPILimiter.close()
    await kafka.kafka.stop()

app.include_router(views.router, prefix='/ugcservice_api/v1')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='127.0.0.1',
        port=8000,
        reload=True,
    )
