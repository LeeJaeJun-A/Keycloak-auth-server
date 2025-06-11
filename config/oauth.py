from pydantic_settings import BaseSettings

class OAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    class Config:
        env_file = ".env.oauth"

oauth_settings = OAuthSettings()
