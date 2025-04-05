from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def extract_token_from_cookies(cookies):
    try:
        # Common patterns for Facebook access tokens
        token_patterns = [
            r'EAA[0-9A-Za-z]+',  # Common Facebook token pattern
            r'access_token=([^&]+)'
        ]
        
        # First try to find token directly in cookies
        for pattern in token_patterns:
            match = re.search(pattern, cookies)
            if match:
                return match.group(0) if pattern == token_patterns[0] else match.group(1)
        
        # If no direct token found, try to extract from common cookie fields
        cookie_dict = {}
        for cookie in cookies.split(';'):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookie_dict[key.strip()] = value.strip()
        
        # Check common Facebook cookie names that might contain token
        possible_token_fields = ['c_user', 'xs', 'fr', 'datr']
        for field in possible_token_fields:
            if field in cookie_dict:
                for pattern in token_patterns:
                    match = re.search(pattern, cookie_dict[field])
                    if match:
                        return match.group(0) if pattern == token_patterns[0] else match.group(1)
        
        return None
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json()
        cookies = data.get('cookies', '')
        
        if not cookies:
            return jsonify({'error': 'No cookies provided'})
        
        token = extract_token_from_cookies(cookies)
        
        if token:
            return jsonify({'token': token})
        else:
            return jsonify({'error': 'Could not extract token from provided cookies'})
            
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
