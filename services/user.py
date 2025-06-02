from config.keycloak import keycloak_openid


class KeycloakUserService:
    @staticmethod
    def login(username: str, password: str):
        token = keycloak_openid.token(username, password)
        return token
