from flask import Flask, request, jsonify
from atproto import Client, client_utils
from datetime import datetime
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Get uptime using "uptime" command and parse output
        # ["cat", "/proc/uptime", "|", "sed '{print $2}'"], 
        uptime_output = subprocess.run(
            ["awk '{print $1}'", "/proc/uptime"], 
            capture_output=True, 
            text=True,
            shell=True
        )
        
        if uptime_output.returncode == 0:
            print("Response:", flush=True)
            print(uptime_output.stdout, flush=True)
            print("STDERR:", flush=True)
            print(uptime_output.stderr, flush=True)

            uptime_seconds = float(uptime_output.stdout.strip())
            minutes, seconds = divmod(int(uptime_seconds * 60), 60)
        else:
            minutes, seconds = "N/A", "N/A"
            
        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Read last 50 lines of log file
        log_output = subprocess.run(
            ["tail", "-n", "50", "/var/log/pybsposter.log"], 
            capture_output=True, 
            text=True
        )
        
        if log_output.returncode == 0:
            logs = log_output.stdout.split('\n')
            logs = [log.strip() for log in logs if log]
        else:
            logs = ["No log entries found"]
    
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        uptime_seconds, current_time, logs = "N/A", "N/A", ["Error reading metrics or logs"]

    return f"""
        <h1>Container Metrics</h1>
        <p>Uptime: {minutes} minutes and {seconds} seconds</p>
        <p>Last Updated: {current_time}</p>
        <h2>Recent Logs:</h2>
        <ul>{''.join(f'<li>{log}</li>' for log in logs)}</ul>
    """

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
