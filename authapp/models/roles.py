import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from db import db


class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'users.id', ondelete='CASCADE')
    )
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey(
        'roles.id', ondelete='CASCADE')
    )
    timestamp = db.Column(db.DateTime, default=db.func.now())
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uix_user_role'),
    )
    role = db.relationship(
        'Role',
        foreign_keys='UserRole.role_id',
        lazy='joined',
        viewonly=True
    )


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    name = db.Column(
        db.String,
        unique=True,
        default='unknown'
    )
    users = db.relationship(
        'User',
        secondary='user_roles',
        back_populates='roles'
    )

    def __repr__(self):
        return f'<:Role {self.name}>'
