from pydantic_settings import BaseSettings
from keycloak import KeycloakOpenID, KeycloakAdmin


class Settings(BaseSettings):
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_ADMIN_USERNAME: str
    KEYCLOAK_ADMIN_PASSWORD: str

    class Config:
        env_file = ".env.fastapi"


settings = Settings()


# OpenID Connect (사용자 인증 관련)
keycloak_openid = KeycloakOpenID(
    server_url=f"{settings.KEYCLOAK_URL}/",
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
    realm_name=settings.KEYCLOAK_REALM,
    verify=True,
)

# Admin API (사용자 생성, 역할 관리 등)
keycloak_admin = KeycloakAdmin(
    server_url=f"{settings.KEYCLOAK_URL}/",
    username=settings.KEYCLOAK_ADMIN_USERNAME,
    password=settings.KEYCLOAK_ADMIN_PASSWORD,
    realm_name=settings.KEYCLOAK_REALM,
    client_id="admin-cli",
    verify=True,
)
