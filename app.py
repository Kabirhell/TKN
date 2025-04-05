import requests
import json
import re

def extract_access_token(cookies):
    """
    Extracts a Facebook access token using the provided cookies by simulating a mobile endpoint request.

    Args:
        cookies (dict): Dictionary of Facebook cookies (e.g., 'c_user', 'xs', 'datr', etc.)

    Returns:
        str: Facebook access token, or None if extraction fails
    """
    # Target a mobile endpoint that might expose an access token
    mobile_url = "https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed"

    # Prepare headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36",
        "Cookie": "; ".join(f"{key}={value}" for key, value in cookies.items()),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    try:
        # Make the request to the mobile endpoint
        response = requests.get(mobile_url, headers=headers, timeout=10)

        # Check if the response was successful
        if response.status_code == 200:
            # Look for an access token in the response text using regex
            token_match = re.search(r'"accessToken":"(EA[A-Za-z0-9]+)"', response.text)
            if token_match:
                return token_match.group(1)
            else:
                print("No access token found in response.")
                return None
        else:
            raise Exception(f"Request failed with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Network error occurred: {str(e)}")
        return None
    except Exception as e:
        print(f"Error extracting access token: {str(e)}")
        return None

def validate_token(token):
    """
    Validates the extracted access token by making a test request to the Graph API.

    Args:
        token (str): The extracted Facebook access token

    Returns:
        bool: True if the token is valid, False otherwise
    """
    graph_api_url = "https://graph.facebook.com/v13.0/me"
    params = {"access_token": token}

    try:
        response = requests.get(graph_api_url, params=params)
        return response.status_code == 200
    except Exception:
        return False

def main():
    # Sample usage example with dummy cookie data
    cookies = {
        "c_user": "1234567890",
        "xs": "abcdefghijklmnopqrstuvwxyz",
        "datr": "1234567890abcdef",
        "fr": "dummyfrvalue",
    }

    # Extract the access token
    access_token = extract_access_token(cookies)

    if access_token:
        print(f"Extracted access token: {access_token}")
        # Validate the token
        if validate_token(access_token):
            print("Token is valid!")
        else:
            print("Token is invalid or expired.")
    else:
        print("Failed to extract access token.")

if __name__ == "__main__":
    main()
