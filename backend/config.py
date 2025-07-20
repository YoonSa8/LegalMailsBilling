from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Google OAuth
    google_client_secret_file: str = "client_secret.json"
    google_scopes: str = "https://www.googleapis.com/auth/gmail.readonly"
    redirect_uri: str = "http://localhost:8000/oauth2callback"

    # Together AI
    together_api_key: str
    together_model: str = "mistralai/Mistral-7B-Instruct-v0.1"

    # Clio
    clio_client_id: str
    clio_client_secret: str
    clio_redirect_uri: str = "http://127.0.0.1:8000/api/clio/callback"
    clio_base_url: str = "https://eu.app.clio.com"

    # Application
    debug: bool = False
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def google_scopes_list(self) -> List[str]:
        return [s.strip() for s in self.google_scopes.split(",") if s.strip()]

settings = Settings()
