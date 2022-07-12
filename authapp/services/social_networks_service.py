import logging
from functools import lru_cache
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from db import db
from flask_restx import abort
from models.user import SocialAccount

logger = logging.getLogger(__name__)


class SocialNetworkIsMissing(Exception):
    """Raised when social network is missing in db"""
    pass


class SocialNetworksService:

    def delete_user_soc(
            self,
            soc_network_id: UUID
    ) -> Optional[bool]:
        logger.info(f"Removing user social network:{soc_network_id}")
        try:
            soc_acc = (
                SocialAccount.query
                .filter(SocialAccount.id == soc_network_id)
                .first()
            )
            if not soc_acc:
                raise SocialNetworkIsMissing
            else:
                db.session.delete(soc_acc)
                db.session.commit()
        except SocialNetworkIsMissing:
            logger.info(f"Social network:{soc_network_id} is missing in db.")
            return False
        except Exception:
            logger.exception(f'Error removing soc network:{soc_network_id}.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return True


@lru_cache()
def get_soc_networks_service() -> SocialNetworksService:
    return SocialNetworksService()
