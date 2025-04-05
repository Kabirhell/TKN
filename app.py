from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

# HTML template with embedded Python logic
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
            max-width: 600px;
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
        <p>{{ result }}</p>
    </div>
</body>
</html>
'''

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
        
        return "No token found in provided cookies"
    except Exception as e:
        return f"Error: {str(e)}"

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
    app.run(debug=True)
