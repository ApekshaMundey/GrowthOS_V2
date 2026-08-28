import os
import sys
import getpass
import requests
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config import settings

def run_auth_verification():
    print("=" * 60)
    print("PHASE 2 AUTHENTICATION VERIFICATION TEST")
    print("=" * 60)

    client = TestClient(app)

    # 1. Test unauthenticated request -> MUST return 401
    print("\n[Step 1] Testing unauthenticated request to /api/v1/auth/test...")
    unauth_resp = client.get("/api/v1/auth/test")
    print(f"Response status: {unauth_resp.status_code}")
    print(f"Response body: {unauth_resp.text}")
    
    if unauth_resp.status_code != 401:
        print("\n❌ FAIL: Unauthenticated request did not return 401 status!")
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

    # 3. Test authenticated request with Bearer token
    print("\n[Step 3] Testing authenticated request to /api/v1/auth/test...")
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    auth_test_resp = client.get("/api/v1/auth/test", headers=auth_headers)

    print(f"Response status: {auth_test_resp.status_code}")
    print(f"Response body: {auth_test_resp.text}")

    if auth_test_resp.status_code != 200:
        print(f"\n❌ FAIL: Authenticated request failed with status {auth_test_resp.status_code}")
        return False

    res_data = auth_test_resp.json()
    returned_user_id = res_data.get("user_id")

    if returned_user_id != expected_user_id:
        print(f"\n❌ FAIL: Returned user_id '{returned_user_id}' does not match expected '{expected_user_id}'")
        return False

    print("\n" + "=" * 60)
    print("✅ PASS: ALL AUTHENTICATION VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_auth_verification()
    sys.exit(0 if success else 1)
