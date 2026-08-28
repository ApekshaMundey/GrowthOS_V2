from supabase import create_client, Client
from app.config import settings


def init_supabase() -> Client:
    """Initialize the Supabase client using the backend-only secret key."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SECRET_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SECRET_KEY must be configured."
        )

    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SECRET_KEY,
    )


# Singleton client instance
_client: Client | None = None


def get_supabase() -> Client:
    """Get or initialize the singleton Supabase client."""
    global _client

    if _client is None:
        _client = init_supabase()

    return _client