from fastapi import Header, HTTPException
from config.keycloak import settings


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.KEYCLOAK_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")