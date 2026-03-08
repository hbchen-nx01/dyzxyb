import os
import sys
import requests
from threading import Thread
import time

# Add the project directory to the path
sys.path.append(os.path.abspath('.'))

# Import the app
from app import app

def run_app():
    """Run the Flask app in a separate thread"""
    app.run(debug=False, host='0.0.0.0', port=5001)

def test_flask_app():
    """Test the Flask app by making a request to the root route"""
    print("Starting Flask app for testing...")
    
    # Start the app in a separate thread
    app_thread = Thread(target=run_app)
    app_thread.daemon = True
    app_thread.start()
    
    # Give the app time to start
    time.sleep(2)
    
    try:
        # Make a request to the root route
        response = requests.get('http://localhost:5001/')
        
        print(f"Request to root route returned status code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Flask app is running and root route is accessible!")
            print(f"Response content length: {len(response.content)} bytes")
            return True
        else:
            print(f"ERROR: Flask app returned status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to connect to Flask app: {e}")
        return False

if __name__ == '__main__':
    success = test_flask_app()
    sys.exit(0 if success else 1)