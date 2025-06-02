from pydantic import BaseModel


class OAuthCallbackRequest(BaseModel):
    code: str
    redirect_uri: str
