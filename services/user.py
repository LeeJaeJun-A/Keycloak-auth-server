from config.keycloak import keycloak_openid
from config.keycloak import settings

import requests

class KeycloakUserService:
    @staticmethod
    def login(username: str, password: str):
        token = keycloak_openid.token(username, password)
        return token

    @staticmethod
    def logout(refresh_token: str):
        requests.post(
            f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/logout",
            data={
                "client_id": settings.KEYCLOAK_CLIENT_ID,
                "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
                "refresh_token": refresh_token,
            },
        )