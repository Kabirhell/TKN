from flask import Flask, request, render_template_string
import re
import sys
import socket

app = Flask(__name__)

TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Token Extractor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
        }
        textarea {
            width: 100%;
            height: 100px;
            margin: 10px 0;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        #result {
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #ddd;
            {% if result %}display: block;{% else %}display: none;{% endif %}
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h2>Facebook Token Extractor</h2>
    <p>Paste your Facebook cookies below:</p>
    <form method="POST">
        <textarea id="cookies" name="cookies" placeholder="Enter Facebook cookies here...">{{ cookies or '' }}</textarea>
        <button type="submit">Extract Token</button>
    </form>
    <div id="result">
        <h3>Result:</h3>
        <p>{{ result | safe }}</p>
    </div>
</body>
</html>
'''

def extract_token_from_cookies(cookies):
    try:
        # Token patterns
        token_patterns = [
            r'EAA[0-9A-Za-z]{20,}',
            r'access_token=([^&;\s]+)',
            r'"accessToken":"([^"]+)"',
            r'token=([^&;\s]+)',
        ]
        
        # Check for direct token
        for pattern in token_patterns:
            match = re.search(pattern, cookies)
            if match:
                return f"Found token: {match.group(1) if match.lastindex else match.group(0)}"
        
        # Parse cookies
        cookie_dict = {}
        for cookie in cookies.split(';'):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookie_dict[key.strip()] = value.strip()
        
        # Check cookie fields
        possible_token_fields = ['c_user', 'xs', 'fr', 'datr', 'sb', 'wd', 'presence']
        found_cookies = list(cookie_dict.keys())
        
        result = "No direct access token found in cookies.<br><br>"
        result += f"Available cookies: {', '.join(found_cookies)}<br><br>"
        
        # Check if key cookies are present
        if 'c_user' in cookie_dict and 'xs' in cookie_dict:
            result += "Valid session cookies detected (c_user and xs), but no API token.<br>"
            result += "Facebook API tokens are typically not stored in cookies anymore.<br><br>"
            result += "<strong>Next Steps:</strong><br>"
            result += "1. Open Facebook in your browser<br>"
            result += "2. Press F12 (Developer Tools)<br>"
            result += "3. Go to Application tab > Storage > Local Storage > facebook.com<br>"
            result += "4. Look for a key containing 'token' or 'accessToken'<br>"
            result += "5. Alternatively, use the browser's Network tab to capture API requests<br>"
            result += "   - Look for requests with Authorization headers<br>"
        else:
            result += "Missing essential session cookies. Please ensure you're copying all cookies from an active Facebook session."
        
        return result
        
    except Exception as e:
        return f"Error processing cookies: {str(e)}"

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_available_port(start_port=5000, max_attempts=10):
    port = start_port
    for _ in range(max_attempts):
        if check_port(port):
            return port
        port += 1
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    cookies = None
    result = None
    
    if request.method == 'POST':
        cookies = request.form.get('cookies', '')
        if cookies:
            result = extract_token_from_cookies(cookies)
    
    return render_template_string(TEMPLATE, cookies=cookies, result=result)

if __name__ == '__main__':
    port = find_available_port()
    if port is None:
        print(f"Error: Could not find an available port starting from 5000")
        sys.exit(1)
    
    try:
        print(f"Starting server on http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        sys.exit(1)
