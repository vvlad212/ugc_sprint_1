import uuid
from sqlalchemy import UniqueConstraint

from sqlalchemy.dialects.postgresql import UUID

from db import db


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_2022"
        PARTITION OF "auth_history" FOR VALUES FROM ('2022-01-01') TO ('2022-12-31');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_2023"
        PARTITION OF "auth_history" FOR VALUES FROM ('2023-01-01') TO ('2024-12-31');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_2024"
        PARTITION OF "auth_history" FOR VALUES FROM ('2024-01-01') TO ('2024-12-31');"""
    )


class AuthHistory(db.Model):
    __tablename__ = 'auth_history'
    __table_args__ = (
        UniqueConstraint('id', 'timestamp', name='uix_auth_timestamp'),
        {
            'postgresql_partition_by': 'RANGE (timestamp)',
            'listeners': [('after_create', create_partition)],
        }
    )

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
    timestamp = db.Column(
        db.DateTime,
        default=db.func.now()
    )
    user_agent = db.Column(
        db.String,
        unique=False,
        default='unknown'
    )
    user_ip = db.Column(
        db.String,
        unique=False,
        default='unknown'
    )

    def __repr__(self):

        return f'<AuthHistory: {self.user_id}>'
