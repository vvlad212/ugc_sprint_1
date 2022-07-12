import click
from flask import Flask
from marshmallow import Schema, ValidationError
from marshmallow import fields as ma_fields
from marshmallow import validate

from db import db
from models.roles import Role
from models.user import User
from services.roles_service import get_roles_service
from services.user_service import get_user_service

user_service = get_user_service()
roles_service = get_roles_service()

class SuperUserValidator(Schema):
    login = ma_fields.Email(required=True,)
    password = ma_fields.String(required=True, validate=validate.Length(min=3))


ADMIN_ROLE_NAME = "admin"

def init_clicommands(app: Flask):
    @app.cli.command("createsuperuser")
    @click.argument("login")
    @click.argument("password")
    def createsuperuser(login, password):
        try:
            data = SuperUserValidator().loads(
                f'{{"login": "{login}", "password": "{password}"}}'
            )
        except ValidationError as err:
            print({"errors": err.messages})
            return

        admin_user = User.query.filter_by(login=login).first()
        if not admin_user:
            admin_user = user_service.create_user(data['login'], data['password'])

        admin_role = Role.query.filter_by(name=ADMIN_ROLE_NAME).first()
        if not admin_role:
            admin_role = roles_service.create_role(ADMIN_ROLE_NAME)

        if ADMIN_ROLE_NAME not in [role.name for role in admin_user.roles]:
            admin_user.roles.append(admin_role)
            db.session.commit()
