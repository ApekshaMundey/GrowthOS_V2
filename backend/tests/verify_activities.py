import os
import sys
import getpass
import requests
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config import settings
from app.services.activity_service import ActivityService
from fastapi import HTTPException

def run_activities_verification():
    print("=" * 60)
    print("PHASE 4 ACTIVITY CRUD VERIFICATION TEST")
    print("=" * 60)

    client = TestClient(app)

    # 1. Test unauthenticated access -> MUST return 401
    print("\n[Step 1] Testing unauthenticated GET /api/v1/activities...")
    unauth_resp = client.get("/api/v1/activities")
    print(f"Response status: {unauth_resp.status_code}")
    if unauth_resp.status_code != 401:
        print("❌ FAIL: Unauthenticated GET /activities did not return 401!")
        return False
    print("✓ Unauthenticated request correctly rejected with 401.")

    # 2. Obtain Supabase Access Token
    print("\n[Step 2] Obtaining Supabase access token...")
    email = os.getenv("TEST_USER_EMAIL")
    password = os.getenv("TEST_USER_PASSWORD")

    if not email or not password:
        if len(sys.argv) >= 3:
            email = sys.argv[1]
            password = sys.argv[2]
        else:
            print("Please enter credentials for Supabase user:")
            email = input("Email: ").strip()
            password = getpass.getpass("Password: ")

    supabase_url = settings.SUPABASE_URL
    publishable_key = settings.SUPABASE_PUBLISHABLE_KEY or settings.SUPABASE_SECRET_KEY

    if not supabase_url or not publishable_key:
        print("❌ FAIL: SUPABASE_URL or SUPABASE_PUBLISHABLE_KEY not configured in environment.")
        return False

    auth_endpoint = f"{supabase_url.rstrip('/')}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": publishable_key,
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "password": password
    }

    try:
        auth_resp = requests.post(auth_endpoint, json=payload, headers=headers)
        if auth_resp.status_code != 200:
            print(f"❌ FAIL: Supabase Auth error ({auth_resp.status_code}): {auth_resp.text}")
            return False

        auth_data = auth_resp.json()
        access_token = auth_data.get("access_token")
        expected_user_id = auth_data.get("user", {}).get("id")

        if not access_token or not expected_user_id:
            print("❌ FAIL: Could not extract access_token or user.id from Supabase response.")
            return False

        print(f"✓ Obtained valid access token for user_id: {expected_user_id}")

    except Exception as e:
        print(f"❌ FAIL: Exception while communicating with Supabase Auth: {e}")
        return False

    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Authenticated Create Activity
    print("\n[Step 3] Testing POST /api/v1/activities...")
    create_payload = {
        "activityType": "manual_note",
        "title": "Phase 4 Test Activity",
        "content": "This is a test activity for verifying Phase 4 Activity CRUD endpoints.",
        "source": "Manual"
    }
    create_resp = client.post("/api/v1/activities", json=create_payload, headers=auth_headers)
    print(f"Response status: {create_resp.status_code}")
    print(f"Response body: {create_resp.text}")

    if create_resp.status_code not in (200, 201):
        print(f"❌ FAIL: Create activity failed with status {create_resp.status_code}")
        return False

    activity_data = create_resp.json()
    activity_id = activity_data.get("id")
    if not activity_id:
        print("❌ FAIL: Returned activity object missing 'id'")
        return False
    print(f"✓ Activity created successfully with id: {activity_id}")

    # 4. Authenticated List Activities
    print("\n[Step 4] Testing GET /api/v1/activities...")
    list_resp = client.get("/api/v1/activities", headers=auth_headers)
    print(f"Response status: {list_resp.status_code}")
    if list_resp.status_code != 200:
        print(f"❌ FAIL: List activities failed with status {list_resp.status_code}")
        return False

    list_data = list_resp.json()
    items = list_data.get("items", [])
    if not any(item["id"] == activity_id for item in items):
        print(f"❌ FAIL: Created activity '{activity_id}' not found in list response!")
        return False
    print(f"✓ List activities returned {len(items)} items including created activity.")

    # 5. Get Created Activity
    print(f"\n[Step 5] Testing GET /api/v1/activities/{activity_id}...")
    get_resp = client.get(f"/api/v1/activities/{activity_id}", headers=auth_headers)
    print(f"Response status: {get_resp.status_code}")
    if get_resp.status_code != 200:
        print(f"❌ FAIL: Fetch activity failed with status {get_resp.status_code}")
        return False
    fetched = get_resp.json()
    if fetched["title"] != create_payload["title"]:
        print("❌ FAIL: Fetched activity title does not match created title!")
        return False
    print("✓ Fetched activity successfully.")

    # 6. Update Activity
    print(f"\n[Step 6] Testing PUT /api/v1/activities/{activity_id}...")
    update_payload = {
        "title": "Updated Phase 4 Title",
        "content": "Updated activity content string."
    }
    put_resp = client.put(f"/api/v1/activities/{activity_id}", json=update_payload, headers=auth_headers)
    print(f"Response status: {put_resp.status_code}")
    if put_resp.status_code != 200:
        print(f"❌ FAIL: Update activity failed with status {put_resp.status_code}")
        return False
    updated = put_resp.json()
    if updated["title"] != update_payload["title"]:
        print("❌ FAIL: Response title not updated!")
        return False
    print("✓ Activity updated successfully.")

    # 7. Persistence Check
    print(f"\n[Step 7] Re-fetching GET /api/v1/activities/{activity_id} to verify persistence...")
    refetch_resp = client.get(f"/api/v1/activities/{activity_id}", headers=auth_headers)
    if refetch_resp.status_code != 200 or refetch_resp.json()["rawContent"] != update_payload["content"]:
        print("❌ FAIL: Updated content did not persist!")
        return False
    print("✓ Updated activity persistence verified.")

    # 8. Cross-User Ownership Isolation Test
    print("\n[Step 8] Testing user ownership isolation (attempting to read with another user_id)...")
    fake_user_id = "00000000-0000-0000-0000-000000000000"
    try:
        ActivityService.get_activity(activity_id=activity_id, user_id=fake_user_id)
        print("❌ FAIL: Other user was able to access activity!")
        return False
    except HTTPException as e:
        if e.status_code != 404:
            print(f"❌ FAIL: Expected 404 for cross-user fetch, got {e.status_code}")
            return False
        print("✓ Cross-user access correctly rejected with 404.")

    # 9. Delete Activity
    print(f"\n[Step 9] Testing DELETE /api/v1/activities/{activity_id}...")
    del_resp = client.delete(f"/api/v1/activities/{activity_id}", headers=auth_headers)
    print(f"Response status: {del_resp.status_code}")
    if del_resp.status_code != 204:
        print(f"❌ FAIL: Delete activity failed with status {del_resp.status_code}")
        return False
    print("✓ Activity deleted successfully.")

    # 10. Confirm Deleted Activity Cannot Be Fetched
    print(f"\n[Step 10] Confirming deleted activity cannot be fetched...")
    post_del_resp = client.get(f"/api/v1/activities/{activity_id}", headers=auth_headers)
    print(f"Response status: {post_del_resp.status_code}")
    if post_del_resp.status_code != 404:
        print(f"❌ FAIL: Deleted activity fetch returned status {post_del_resp.status_code} instead of 404!")
        return False
    print("✓ Deleted activity fetch correctly returned 404.")

    print("\n" + "=" * 60)
    print("✅ PASS: ALL PHASE 4 ACTIVITY CRUD VERIFICATION CHECKS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_activities_verification()
    sys.exit(0 if success else 1)
