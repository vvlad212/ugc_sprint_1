from http import HTTPStatus
import logging
from functools import lru_cache
from typing import List, Optional, Union
from uuid import UUID

from flask_restx import abort
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from db import db
from models.roles import Role, UserRole
from models.user import User

logger = logging.getLogger(__name__)


class RoleIsMissing(Exception):
    """Raised when role is missing in db"""
    pass


class RolesService:

    def create_role(self, new_role_name: str) -> Optional[Role]:
        logger.info(f"create_role started, new role name: {new_role_name}")
        try:
            new_role = Role(
                name=new_role_name,
            )
            db.session.add(new_role)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(HTTPStatus.CONFLICT, 'Role already exist.')
        except Exception:
            logger.exception(f'Error creating new role: {new_role_name}.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        logger.info(f"Role:{new_role_name} has been created successfully.")
        return new_role

    def delete_role(self, role_name: str) -> bool:
        """
        Returns:
            If role has been deleted returns True
            else False
        """
        logger.info(f"delete_role started, deleting role name: {role_name}")
        try:
            role = Role.query.filter(Role.name == role_name).first()
            if not role:
                raise RoleIsMissing
            else:
                db.session.delete(role)
                db.session.commit()
        except RoleIsMissing:
            logger.info(f"Role: {role_name} is missing in db.")
            return False
        except Exception:
            logger.exception(f'Error removing role: {role_name}.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return True

    def get_user_roles(self, user_id: Union[str, UUID]) -> List[dict]:
        """
        Get user roles from db by user id
        """
        logger.info(f"get_user_roles started user_id: {user_id}")
        try:
            user_roles = UserRole.query.filter(UserRole.user_id == user_id)
        except Exception:
            logger.exception(f'Error getting user:{user_id} roles.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return [
            {
                'role_name': user_role.role.name,
                'assignment_timestamp': user_role.timestamp.isoformat()
                if user_role.timestamp else None
            } for user_role in user_roles
        ]

    def get_all_roles(self) -> List:
        """
        Returns:
            list roles
        """
        try:
            return [{str(r.id): r.name} for r in Role.query.all()]
        except Exception:
            logger.exception('Getting all roles error.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    def add_role_to_user(self, user_id: str, role_id: str):
        """
        Добавление роли пользователю
        """
        logger.info(f'Trying to assign a role to a user {user_id}.')
        user = User.query.filter_by(id=user_id).first()
        if not user:
            logger.info(f"User: {user_id} is missing in db.")
            raise ValidationError("User_id is missing in db.")

        role = Role.query.filter_by(id=role_id).first()
        if not role:
            logger.info(f"Role: {role_id} is missing in db.")
            raise ValidationError("Role is missing in db.")

        if role in user.roles:
            logger.info(f"The role {role_id} is already assigned to the user {user_id}.")
            raise ValidationError(f"The role {role_id} is already assigned to the user {user_id}.")
        try:
            user.roles.append(role)
            db.session.commit()
        except Exception:
            logger.exception(f'error when assigning a role to a user {user_id}.')
            logger.exception('Getting all roles error.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    def delete_role_to_user(self, user_id: str, role_id: str):
        """
        Удаление роли у пользователя
        """
        logger.info(f'Trying to delete role {role_id} for user {user_id}.')

        user = User.query.filter_by(id=user_id).first()
        if not user:
            logger.info(f"User: {user_id} is missing in db.")
            raise ValidationError("User_id is missing in db.")

        role = Role.query.filter_by(id=role_id).first()
        if not role:
            logger.info(f"Role: {role_id} is missing in db.")
            raise ValidationError("Role_id is missing in db.")
        if not role in user.roles:
            logger.info(f"User {user_id} does not have this role {role_id}.")
            raise ValidationError(f"User {user_id} does not have this role {role_id}.")
        try:
            UserRole.query.filter_by(user_id=user_id, role_id=role.id).delete()
            db.session.commit()
            logger.info(f"Role {role_id} removed from user {user_id}.")
        except Exception:
            logger.exception(f'Deleting role error.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)

    def update_role(
            self,
            role_id: Union[str, UUID],
            new_role_name: str
    ) -> Optional[bool]:
        """
        Returns True if role has been updated
        else None
        """
        logger.info(f"update_role started role_id: {role_id}")
        try:
            role = Role.query.filter(Role.id == role_id).first()
            if not role:
                logger.info(f"Role:{role_id} is missing in db")
                return
            role.name = new_role_name
            db.session.add(role)
            db.session.commit()
        except Exception:
            logger.exception(f'Error updating role:{role_id}.')
            abort(HTTPStatus.INTERNAL_SERVER_ERROR)
        return True


@lru_cache()
def get_roles_service():
    return RolesService()
