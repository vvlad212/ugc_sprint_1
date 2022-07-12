import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from db import db


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "users_2022"
        PARTITION OF "users" FOR VALUES FROM ('2022-01-01') TO ('2022-12-31');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "users_2023"
        PARTITION OF "users" FOR VALUES FROM ('2023-01-01') TO ('2024-12-31');"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "users_2024"
        PARTITION OF "users" FOR VALUES FROM ('2024-01-01') TO ('2024-12-31');"""
    )


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('id', 'registration_timestamp', name='uix_user_reg_time'),
        {
            'postgresql_partition_by': 'RANGE (registration_timestamp)',
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
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    iterations = db.Column(db.Integer, nullable=False)
    auth_history = db.relationship('AuthHistory', backref='user')
    roles = db.relationship(
        'Role',
        secondary='user_roles',
        back_populates='users'
    )
    registration_timestamp = db.Column(
        db.DateTime,
        default=db.func.now(),
    )

    def __repr__(self):
        return f'<User {self.login}>'


class SocialAccount(db.Model):
    __tablename__ = 'social_account'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4, unique=True
    )
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    user = db.relationship(
        User,
        backref=db.backref('social_accounts', lazy=True)
    )

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            'social_id', 'social_name', name='social_name_id_idx'
        ),
    )

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
