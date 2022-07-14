from authlib.integrations.flask_client import OAuth
from flask import Flask
from pydantic import BaseModel, BaseSettings, Field, AnyUrl

oauth = OAuth()


class YandexConfig(BaseSettings):

    name: str = Field("yandex", env='yandex_agent_name')
    client_id: str = Field('7bc57d06e83d4a519dfb7d10402901d2', env="YANDEX_CLIENT_ID")
    client_secret: str = Field('1938219175ec4c7f87f406aeace6951e',env="YANDEX_CLIENT_SECRET")
    api_base_url: AnyUrl = Field(
        "https://login.yandex.ru/", env="yandex_api_base_url"
    )
    access_token_url: AnyUrl = Field(
        "https://oauth.yandex.ru/token", env="yandex_access_token_url"
    )
    authorize_url: AnyUrl = Field(
        "https://oauth.yandex.ru/authorize", env="yandex_authorize_url"
    )

    class Config:
        env_prefix = ""
        case_sensitive = False


class GoogleScope(BaseModel):
    scope: str = Field("openid email profile", env="google_scope")


class GoogleConfig(BaseSettings):
    name: str = Field("google", env="google_agent_name")
    client_kwargs: GoogleScope = GoogleScope()
    client_id: str = Field('421420320201-ibdldjmoem7scfvek05m0vhb8516aq62.apps.googleusercontent.com',env="GOOGLE_CLIENT_ID")
    client_secret: str = Field('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', env="GOOGLE_CLIENT_SECRET")
    server_metadata_url: AnyUrl = Field(
        "https://accounts.google.com/.well-known/openid-configuration",
        env="google_server_metadata_url"
    )


def init_oauth(app: Flask):
    oauth.register(
        **YandexConfig().dict()
    )

    oauth.register(
        **GoogleConfig().dict()
    )
    oauth.init_app(app)
