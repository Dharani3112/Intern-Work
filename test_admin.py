#!/usr/bin/env python3
"""
Quick test script to verify admin routes work correctly
"""
import requests
import sys

def test_admin_routes():
    """Test admin routes functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Admin Routes")
    print("=" * 40)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Test 1: Admin login page
        print("1. Testing admin login page...")
        response = session.get(f"{base_url}/admin/login")
        if response.status_code == 200:
            print("   ✅ Admin login page loads successfully")
        else:
            print(f"   ❌ Admin login page failed: {response.status_code}")
            return False
        
        # Test 2: Login with admin credentials
        print("2. Testing admin authentication...")
        login_data = {"password": "AdminSecure2025!"}
        response = session.post(f"{base_url}/admin/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:  # Redirect after successful login
            print("   ✅ Admin authentication successful")
        else:
            print(f"   ❌ Admin authentication failed: {response.status_code}")
            return False
        
        # Test 3: Admin dashboard
        print("3. Testing admin dashboard...")
        response = session.get(f"{base_url}/admin")
        if response.status_code == 200:
            print("   ✅ Admin dashboard loads successfully")
        else:
            print(f"   ❌ Admin dashboard failed: {response.status_code}")
            return False
        
        # Test 4: Admin orders page
        print("4. Testing admin orders page...")
        response = session.get(f"{base_url}/admin/orders")
        if response.status_code == 200:
            print("   ✅ Admin orders page loads successfully")
        else:
            print(f"   ❌ Admin orders page failed: {response.status_code}")
            return False
        
        # Test 5: Admin summary page
        print("5. Testing admin summary page...")
        response = session.get(f"{base_url}/admin/summary")
        if response.status_code == 200:
            print("   ✅ Admin summary page loads successfully")
        else:
            print(f"   ❌ Admin summary page failed: {response.status_code}")
            return False
        
        print("\n🎉 All admin routes working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = test_admin_routes()
    if not success:
        sys.exit(1)
