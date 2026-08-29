import os
import sys
import getpass
import requests
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config import settings

def run_profile_verification():
    print("=" * 60)
    print("PHASE 3 PROFILE & FASTAPI FOUNDATION VERIFICATION TEST")
    print("=" * 60)

    client = TestClient(app)

    # 1. Test unauthenticated request -> MUST return 401
    print("\n[Step 1] Testing unauthenticated GET /api/v1/users/me...")
    unauth_resp = client.get("/api/v1/users/me")
    print(f"Response status: {unauth_resp.status_code}")
    print(f"Response body: {unauth_resp.text}")
    
    if unauth_resp.status_code != 401:
        print("\n❌ FAIL: Unauthenticated GET /users/me did not return 401 status!")
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

    # 3. Test authenticated GET /api/v1/users/me
    print("\n[Step 3] Testing authenticated GET /api/v1/users/me...")
    get_resp = client.get("/api/v1/users/me", headers=auth_headers)
    print(f"Response status: {get_resp.status_code}")
    print(f"Response body: {get_resp.text}")

    if get_resp.status_code != 200:
        print(f"❌ FAIL: Authenticated GET /users/me failed with status {get_resp.status_code}")
        return False

    original_profile = get_resp.json()
    if original_profile.get("id") != expected_user_id:
        print(f"❌ FAIL: Returned profile ID '{original_profile.get('id')}' != expected '{expected_user_id}'")
        return False
    print(f"✓ Fetched profile correctly for user: {original_profile.get('name')}")

    # 4. Test authenticated PUT /api/v1/users/me
    print("\n[Step 4] Testing authenticated PUT /api/v1/users/me (updating bio/profession)...")
    test_update = {
        "profession": "Verification Engineer Test",
        "bio": "Automated verification test run"
    }

    put_resp = client.put("/api/v1/users/me", json=test_update, headers=auth_headers)
    print(f"Response status: {put_resp.status_code}")
    print(f"Response body: {put_resp.text}")

    if put_resp.status_code != 200:
        print(f"❌ FAIL: Authenticated PUT /users/me failed with status {put_resp.status_code}")
        return False

    updated_profile = put_resp.json()
    if updated_profile.get("profession") != test_update["profession"] or updated_profile.get("bio") != test_update["bio"]:
        print("❌ FAIL: Updated fields do not match sent payload!")
        return False
    print("✓ Update applied successfully.")

    # 5. Verify persistence via GET /api/v1/users/me
    print("\n[Step 5] Re-fetching GET /api/v1/users/me to verify persistence...")
    verify_resp = client.get("/api/v1/users/me", headers=auth_headers)
    if verify_resp.status_code != 200:
        print(f"❌ FAIL: Re-fetch failed with status {verify_resp.status_code}")
        return False
    
    persisted_profile = verify_resp.json()
    if persisted_profile.get("bio") != test_update["bio"]:
        print("❌ FAIL: Changes were not persisted to database!")
        return False
    print("✓ Changes successfully verified in database.")

    # 6. Restore original profile state
    print("\n[Step 6] Restoring original profile state...")
    restore_payload = {
        "name": original_profile.get("name"),
        "profession": original_profile.get("profession"),
        "bio": original_profile.get("bio"),
        "timezone": original_profile.get("timezone", "UTC")
    }
    client.put("/api/v1/users/me", json=restore_payload, headers=auth_headers)
    print("✓ Original profile state restored.")

    print("\n" + "=" * 60)
    print("✅ PASS: ALL FASTAPI FOUNDATION & PROFILE CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_profile_verification()
    sys.exit(0 if success else 1)
