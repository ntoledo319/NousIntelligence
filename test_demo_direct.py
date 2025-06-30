#!/usr/bin/env python3
"""Test demo route directly to see the error"""

from app_working import app

def test_demo_route():
    """Test demo route directly"""
    with app.test_client() as client:
        with app.app_context():
            print("Testing demo route directly...")
            try:
                response = client.get('/demo')
                print(f"Status Code: {response.status_code}")
                if response.status_code != 200:
                    print(f"Response data: {response.data.decode()}")
                else:
                    print("Demo route working correctly!")
                    print(f"Response length: {len(response.data)} bytes")
                    
            except Exception as e:
                print(f"Error testing demo route: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_demo_route()