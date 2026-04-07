import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_predict_safety(latitude: float, longitude: float):
    """Test the safety prediction endpoint"""
    print(f"\nTesting safety prediction for coordinates: ({latitude}, {longitude})")
    
    payload = {
        "latitude": latitude,
        "longitude": longitude
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict-safety", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
            
            print(f"\nSummary:")
            print(f"Number of locations analyzed: {len(data['locations'])}")
            print(f"Average Safety Score: {data['average_safety_score']}/10")
            print(f"Average Safety Percentage: {data['average_safety_percentage']}%")
            
            print(f"\nTop 10 Nearest Locations:")
            for i, loc in enumerate(data['locations'], 1):
                print(f"{i}. {loc['name']}: {loc['safety_score']}/10")
        else:
            print(f"Error: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running.")
        print("Start the server with: python app.py")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("-" * 50)

def test_invalid_coordinates():
    """Test with invalid coordinates"""
    print("\nTesting with invalid coordinates...")
    
    # Test invalid latitude
    payload = {
        "latitude": 100,  # Invalid
        "longitude": 72.84
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict-safety", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("-" * 50)

if __name__ == "__main__":
    print("=" * 50)
    print("SafeSphere ML API Test Suite")
    print("=" * 50)
    
    # Test root endpoint
    test_root()
    
    # Test with Mumbai coordinates (Andheri area)
    test_predict_safety(19.0744, 72.8869)
    
    # Test with another Mumbai location (Bandra)
    test_predict_safety(19.0550, 72.8402)
    
    # Test with invalid coordinates
    test_invalid_coordinates()
    
    print("\nAll tests completed!")

