from functools import lru_cache
import aiohttp
from core import config




class AuthService:
    def __init__(self):
        self.auth_url = config.AUTH_SERVICE

    async def validate(self, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(self.auth_url) as response:
                return await response.json()


@lru_cache()
def get_auth_service() -> AuthService:
    return AuthService()
