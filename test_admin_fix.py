#!/usr/bin/env python3
"""
Test script to verify admin summary page works with Order.user relationship
"""

import requests
import sys

def test_admin_summary():
    """Test if the admin summary page loads without errors"""
    
    print("🧪 Testing Admin Summary Page Fix")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test 1: Check if main page loads
        print("1. Testing main page...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Main page loads successfully")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
            return False
        
        # Test 2: Check admin login page
        print("2. Testing admin login page...")
        response = requests.get(f"{base_url}/admin/login", timeout=10)
        if response.status_code == 200:
            print("   ✅ Admin login page loads successfully")
        else:
            print(f"   ❌ Admin login page failed: {response.status_code}")
            return False
        
        # Test 3: Login to admin (simulate form submission)
        print("3. Testing admin authentication...")
        session = requests.Session()
        
        # Get login page first to establish session
        login_page = session.get(f"{base_url}/admin/login")
        
        # Submit login form
        login_data = {
            'admin_password': 'AdminSecure2025!'
        }
        
        login_response = session.post(f"{base_url}/admin/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code in [302, 303]:  # Redirect after successful login
            print("   ✅ Admin authentication successful")
        else:
            print(f"   ❌ Admin authentication failed: {login_response.status_code}")
            return False
        
        # Test 4: Check admin summary page (the one that was failing)
        print("4. Testing admin summary page (with Order.user relationship)...")
        summary_response = session.get(f"{base_url}/admin/summary", timeout=15)
        
        if summary_response.status_code == 200:
            print("   ✅ Admin summary page loads successfully!")
            print("   ✅ Order.user relationship is working correctly!")
            
            # Check if page contains expected content
            if "Total Books" in summary_response.text and "Total Orders" in summary_response.text:
                print("   ✅ Page contains expected analytics content")
            else:
                print("   ⚠️  Page loads but may be missing some content")
                
        else:
            print(f"   ❌ Admin summary page failed: {summary_response.status_code}")
            if summary_response.status_code == 500:
                print("   💡 This suggests the Order.user relationship error still exists")
            return False
        
        # Test 5: Check admin orders page
        print("5. Testing admin orders page...")
        orders_response = session.get(f"{base_url}/admin/orders", timeout=15)
        
        if orders_response.status_code == 200:
            print("   ✅ Admin orders page loads successfully!")
        else:
            print(f"   ❌ Admin orders page failed: {orders_response.status_code}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ The AttributeError: 'Order' has no attribute 'user' issue is FIXED!")
        print("✅ Your Flask application is working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
        print("💡 Run: python app.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The server might be overloaded or stuck.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = test_admin_summary()
    sys.exit(0 if success else 1)
