import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from db import db


class UserRefreshToken(db.Model):
    __tablename__ = 'user_refresh_tokens'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    user_agent = db.Column(
        db.String,
        nullable=False
    )
    token = db.Column(
        db.String,
        nullable=False
    )
    user = db.relationship('User', backref='refresh_tokens')
    __table_args__ = (
        UniqueConstraint('user_id', 'user_agent', name='uix_user_agent'),
    )
