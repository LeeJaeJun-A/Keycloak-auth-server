from keycloak import KeycloakOpenID
from config.keycloak import keycloak_openid

class KeycloakOAuthService:
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        token = keycloak_openid.token(code=code, redirect_uri=redirect_uri)
        return token

    def get_user_info(self, access_token: str) -> dict:
        user_info = keycloak_openid.userinfo(access_token)
        return user_info

    def refresh_token(self, refresh_token: str) -> dict:
        return keycloak_openid.refresh_token(refresh_token)

    def logout(self, refresh_token: str) -> None:
        keycloak_openid.logout(refresh_token)