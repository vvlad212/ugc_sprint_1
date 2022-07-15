from functools import wraps
from core import config
import logging
from services.auth import get_auth_service

logger = logging.getLogger(__name__)


def check_roles():
    def wrapper(fn):
        @wraps(fn)
        async def decorator(*args, **kwargs):
            logger.info(f"Trying to get a response from the auth service.")
            try:
                auth_service = get_auth_service()
                result = await auth_service.validate(kwargs['token'])
                user_roles = result.get('user_roles')
                if not user_roles:
                    kwargs['user_roles'] = ['unauthorized']
                    logger.info(f"User is not logged in due to {result}")
                else:
                    kwargs['user_roles'] = user_roles
                logger.info(f"Token verified.")
            except Exception as ex:
                logger.info(f"Authorization service unavailable. {ex}")
                kwargs['user_roles'] = ['failed']

            if config.ENV == 'test':
                kwargs['user_roles'] = ['subscription']

            return await fn(*args, **kwargs)

        return decorator

    return wrapper
