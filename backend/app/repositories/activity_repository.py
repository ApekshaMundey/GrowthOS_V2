from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from app.database.client import get_supabase

class ActivityRepository:
    @staticmethod
    def create(user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new activity for a specific user."""
        client = get_supabase()
        now_str = datetime.now(timezone.utc).isoformat()
        
        row = {
            "user_id": user_id,
            "activity_type": activity_data["activity_type"],
            "source": activity_data.get("source", "Manual"),
            "title": activity_data["title"],
            "raw_content": activity_data["content"],
            "source_metadata": activity_data.get("source_metadata"),
            "activity_date": activity_data.get("activity_date") or now_str,
            "status": "Pending",
            "created_at": now_str,
            "updated_at": now_str,
        }
        
        response = client.table("activities").insert(row).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        raise RuntimeError("Failed to insert activity into database")

    @staticmethod
    def get_by_id(activity_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch activity by ID ensuring user ownership."""
        client = get_supabase()
        response = (
            client.table("activities")
            .select("*")
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    @staticmethod
    def list_activities(
        user_id: str,
        page: int = 1,
        limit: int = 20,
        source: Optional[str] = None,
        activity_type: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List user's activities with optional filtering and pagination."""
        client = get_supabase()
        
        # Build query for counting total matching items
        count_query = client.table("activities").select("id", count="exact").eq("user_id", user_id)
        if source:
            count_query = count_query.eq("source", source)
        if activity_type:
            count_query = count_query.eq("activity_type", activity_type)
        
        count_res = count_query.execute()
        total = count_res.count if count_res.count is not None else (len(count_res.data) if count_res.data else 0)

        # Build query for fetching paginated items
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit - 1
        
        query = client.table("activities").select("*").eq("user_id", user_id)
        if source:
            query = query.eq("source", source)
        if activity_type:
            query = query.eq("activity_type", activity_type)
            
        query = query.order("activity_date", desc=True).range(start_idx, end_idx)
        res = query.execute()
        
        items = res.data if res.data else []
        return items, total

    @staticmethod
    def update(activity_id: str, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing activity for a user."""
        client = get_supabase()
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        response = (
            client.table("activities")
            .update(updates)
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    @staticmethod
    def delete(activity_id: str, user_id: str) -> bool:
        """Delete an activity by ID for a user."""
        client = get_supabase()
        response = (
            client.table("activities")
            .delete()
            .eq("id", activity_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(response.data and len(response.data) > 0)
