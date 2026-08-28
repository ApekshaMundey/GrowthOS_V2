import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
# Also load from backend/.env explicitly if running from root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

class Settings(BaseModel):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SECRET_KEY: str = os.getenv("SUPABASE_SECRET_KEY", "")
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    
    # Derives JWKS URL if not explicitly set
    _jwks_url: str = os.getenv("SUPABASE_JWKS_URL", "")
    
    @property
    def SUPABASE_JWKS_URL(self) -> str:
        if self._jwks_url:
            return self._jwks_url
        if self.SUPABASE_URL:
            return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        return ""

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    
    ENV: str = os.getenv("ENV", "development")

settings = Settings()
