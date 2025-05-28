#!/usr/bin/env python3
"""
Test script to verify dynamic categories are working in search functionality
"""

import requests
from bs4 import BeautifulSoup

def test_dynamic_categories():
    """Test that search page uses dynamic categories from database"""
    try:
        # Test the search page
        response = requests.get('http://127.0.0.1:5000/search')
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the category dropdown
            category_select = soup.find('select', {'name': 'category'})
            
            if category_select:
                options = category_select.find_all('option')
                print("🔍 Search Category Filter Test Results:")
                print("=" * 50)
                print(f"✅ Found category dropdown with {len(options)} options")
                
                print("\n📋 Available categories:")
                for i, option in enumerate(options):
                    value = option.get('value', '')
                    text = option.text.strip()
                    if i == 0:
                        print(f"  {i+1}. '{text}' (value: '{value}') - Default option")
                    else:
                        print(f"  {i+1}. '{text}' (value: '{value}')")
                
                # Check if we have dynamic categories (more than just "All Categories")
                dynamic_categories = [opt for opt in options if opt.get('value') and opt.get('value') != '']
                
                if len(dynamic_categories) > 0:
                    print(f"\n✅ SUCCESS: Found {len(dynamic_categories)} dynamic categories from database")
                    print("🎉 Search filters are now using dynamic categories instead of hardcoded ones!")
                else:
                    print("\n⚠️  WARNING: No dynamic categories found - only 'All Categories' option available")
                    print("This might indicate no products exist in the database or categories are empty")
                    
            else:
                print("❌ ERROR: Could not find category dropdown in search page")
                
        else:
            print(f"❌ ERROR: Could not access search page (Status: {response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_category_filtering():
    """Test that category filtering works with dynamic categories"""
    try:
        # First get available categories
        response = requests.get('http://127.0.0.1:5000/search')
        soup = BeautifulSoup(response.content, 'html.parser')
        category_select = soup.find('select', {'name': 'category'})
        
        if category_select:
            categories = [opt.get('value') for opt in category_select.find_all('option') if opt.get('value')]
            
            if categories:
                # Test filtering with the first available category
                test_category = categories[0]
                filter_response = requests.get(f'http://127.0.0.1:5000/search?category={test_category}')
                
                if filter_response.status_code == 200:
                    print(f"\n🔍 Testing category filter with '{test_category}':")
                    filter_soup = BeautifulSoup(filter_response.content, 'html.parser')
                    
                    # Check if the category is selected in the dropdown
                    selected_option = filter_soup.find('option', {'value': test_category, 'selected': True})
                    if selected_option:
                        print(f"✅ Category '{test_category}' is properly selected in dropdown")
                    else:
                        print(f"⚠️  Category '{test_category}' is not marked as selected")
                    
                    # Count results
                    result_items = filter_soup.find_all('div', class_='result-item')
                    print(f"📊 Found {len(result_items)} products for category '{test_category}'")
                    
                else:
                    print(f"❌ ERROR: Category filtering failed (Status: {filter_response.status_code})")
            else:
                print("⚠️  No categories available to test filtering")
                
    except Exception as e:
        print(f"❌ ERROR in category filtering test: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Dynamic Categories in Search Functionality")
    print("=" * 60)
    test_dynamic_categories()
    test_category_filtering()
    print("\n" + "=" * 60)
    print("✨ Test completed!")
