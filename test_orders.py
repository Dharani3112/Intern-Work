#!/usr/bin/env python3
"""
Test script to verify the admin orders management system
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_admin_login():
    """Test admin login functionality"""
    print("Testing admin login...")
    response = requests.post(f"{BASE_URL}/admin/login", data={
        'password': 'admin123'
    }, allow_redirects=False)
    
    print(f"Admin login status: {response.status_code}")
    if response.status_code == 302:
        print("✅ Admin login successful")
        return response.cookies
    else:
        print("❌ Admin login failed")
        return None

def test_orders_page(cookies):
    """Test the admin orders page"""
    print("\nTesting admin orders page...")
    response = requests.get(f"{BASE_URL}/admin/orders", cookies=cookies)
    
    print(f"Orders page status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Orders page accessible")
        # Check if the page contains expected content
        content = response.text
        if "Orders Management" in content:
            print("✅ Orders page contains expected content")
        if "Filter Orders" in content:
            print("✅ Filter functionality present")
        if "status-filter" in content:
            print("✅ Status filter present")
    else:
        print("❌ Orders page not accessible")

def test_order_filtering(cookies):
    """Test order filtering functionality"""
    print("\nTesting order filtering...")
    
    # Test filtering by status
    response = requests.get(f"{BASE_URL}/admin/orders", 
                          params={'status': 'completed'}, 
                          cookies=cookies)
    
    if response.status_code == 200:
        print("✅ Status filtering works")
    else:
        print("❌ Status filtering failed")

def test_order_detail(cookies):
    """Test individual order detail page"""
    print("\nTesting order detail page...")
    
    # First get orders to find a valid order ID
    response = requests.get(f"{BASE_URL}/admin/orders", cookies=cookies)
    if response.status_code == 200:
        # Try to access order detail for order ID 1
        detail_response = requests.get(f"{BASE_URL}/admin/order/1", cookies=cookies)
        if detail_response.status_code == 200:
            print("✅ Order detail page accessible")
        elif detail_response.status_code == 404:
            print("ℹ️ Order ID 1 not found (normal if no orders exist)")
        else:
            print(f"❌ Order detail page error: {detail_response.status_code}")

if __name__ == "__main__":
    print("🧪 Testing Admin Orders Management System")
    print("=" * 50)
    
    # Test admin login
    cookies = test_admin_login()
    
    if cookies:
        # Test orders page
        test_orders_page(cookies)
        
        # Test filtering
        test_order_filtering(cookies)
        
        # Test order detail
        test_order_detail(cookies)
        
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Cannot proceed without admin authentication")
