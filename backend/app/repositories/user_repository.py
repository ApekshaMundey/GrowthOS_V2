from typing import Optional, Dict, Any
from datetime import datetime, timezone
from app.database.client import get_supabase

class UserRepository:
    @staticmethod
    def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile by user_id from public.users table."""
        client = get_supabase()
        response = client.table("users").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    @staticmethod
    def create_user_profile(user_id: str, email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Create a default user profile row in public.users table."""
        client = get_supabase()
        display_name = name or (email.split("@")[0] if email else "User")
        now_str = datetime.now(timezone.utc).isoformat()
        
        user_data = {
            "id": user_id,
            "name": display_name,
            "email": email,
            "profile_image": None,
            "profession": None,
            "bio": None,
            "timezone": "UTC",
            "created_at": now_str,
            "updated_at": now_str,
        }
        
        response = client.table("users").insert(user_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return user_data

    @staticmethod
    def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile fields for user_id."""
        client = get_supabase()
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        response = client.table("users").update(updates).eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return UserRepository.get_by_id(user_id)
