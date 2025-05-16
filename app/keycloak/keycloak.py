
from jose import jwt
from typing import Optional, Dict
import httpx
from fastapi import HTTPException, Depends, Request
from pydantic import BaseModel
from functools import lru_cache
from app.users.models import User
import logging

logging.basicConfig(level=logging.INFO)


# class User(BaseModel):
#     sub: str
#     username: str
#     email: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None


class KeycloakManager:
    def __init__(self, keycloak_url: str, realm: str):
        self.keycloak_url = keycloak_url
        self.realm = realm
        self.realm_public_key = self._fetch_realm_public_key()

    def _fetch_realm_public_key(self) -> str:
        url = f"{self.keycloak_url}/realms/{self.realm}"
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            return "-----BEGIN PUBLIC KEY-----\n" + response.json()["public_key"] + "\n-----END PUBLIC KEY-----"

    def decode_token(self, token: str) -> Dict:
        try:
            return jwt.decode(token, self.realm_public_key, algorithms=["RS256"])
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    async def get_user_from_token(self, request: Request) -> User:
        logging.info("Получаем токен из заголовка")
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        token = auth_header.split(" ")[1]
        payload = self.decode_token(token)

        user = User(
            sub=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            first_name=payload.get("given_name"),
            last_name=payload.get("family_name")
        )
        print('user ---- ',user)
        return user


@lru_cache()
def get_keycloak_manager():
    from dotenv import load_dotenv
    import os
    load_dotenv()
    logging.info("Loading .env")
    load_dotenv()
    logging.info(f"KEYCLOAK_URL: {os.getenv('KEYCLOAK_URL')}")
    logging.info(f"KEYCLOAK_REALM: {os.getenv('KEYCLOAK_REALM')}")
    return KeycloakManager(
        keycloak_url=os.getenv("KEYCLOAK_URL"),
        realm=os.getenv("KEYCLOAK_REALM")
    )

