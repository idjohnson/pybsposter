from flask import Flask, request, jsonify
from atproto import Client, client_utils

app = Flask(__name__)

@app.route('/post', methods=['POST'])
def handle_post():
    data = request.json
    
    username = data.get('USERNAME')
    password = data.get('PASSWORD')
    text = data.get('TEXT')
    link = data.get('LINK')

    # Calculate the total length of text and link 
    total_length = len(text) + len(link)
    if total_length > 300:
        text = text[:(300 - len(link) - 4)] + "... "  # Trim and add ellipsis

    try:
        client = Client()
    except Exception as e:
        print(f"Failed to connect to server: {e}")

    profile = client.login(username, password)
    
    builder = client_utils.TextBuilder().text(text).link(link,link)
    text_string = str(builder) # Convert TextBuilder to a string

    try:
        post = client.send_post(builder)
        response = {
            "YOU ARE:": profile.display_name,
            "TEXT": text_string,
            "LINK": link
        }

        return jsonify(response)
    except Exception as e:
        print(f"Failed to post: {e}")
        return {'error': 'Failed to send post'}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
