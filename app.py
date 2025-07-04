from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime
from atproto import Client, client_utils
from pydantic import BaseModel
import subprocess
import requests
import os


app = FastAPI()

class SocialPost(BaseModel):
    username: str
    password: str
    text: str
    link: str | None = None
    baseURL: Union[str, None] = None  # Mastodon root URL (optional)

    class Config:
        allow_population_by_field_name = True
        alias_generator = lambda s: s.upper()
        populate_by_name = True

@app.get("/", response_class=HTMLResponse)
def read_root():
    # Existing code remains unchanged
    try:
        uptime_output = subprocess.run(
            ["uptime"], 
            capture_output=True, 
            text=True,
            shell=True
        )
        
        uptimeoutput = "N/A"

        if uptime_output.returncode == 0:
            uptimeoutput = uptime_output.stdout
            
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

    # Get app version from environment variable
    app_version = os.environ.get("VERSION", "unknown")

    return f"""
        <pre>
         ______        ______      ______              _               
        | ___ \       | ___ \     | ___ \            | |              
        | |_/ / _   _ | |_/ / ___ | |_/ /  ___   ___ | |_   ___  _ __ 
        |  __/ | | | || ___ \/ __||  __/  / _ \ / __|| __| / _ \| '__|
        | |    | |_| || |_/ /\__ \| |    | (_) |\__ \| |_ |  __/| |   
        \_|     \__, |\____/ |___/\_|     \___/ |___/ \__| \___||_|   
                __/ |                                                
                |___/                                                 
        </pre>
        <br/>
        <br/>
        <h1>Container Metrics</h1>
        <p><b>App Version:</b> {app_version}</p>
        <p>Uptime: {uptimeoutput}</p>
        <p>Last Updated: {current_time}</p>
        <h2>Recent Logs:</h2>
        <ul>{''.join(f'<li>{log}</li>' for log in logs)}</ul>
    """


@app.post("/preview")
async def preview_social(post: SocialPost):
    """
    Generate a text preview of the user's post with trimming logic applied.
    
    Args:
        post (SocialPost): The post data including username, text, and optional link.

    Returns:
        dict: A dictionary containing the trimmed preview text and link.
    """
    # Extract text and link from the user's input
    text = post.text
    link = post.link if post.link else ""

    # Calculate the total length of text and link
    total_length = len(text) + len(link)
    
    # Trim the text if combined length exceeds 300 characters
    if total_length > 300:
        preview_text = text[:(300 - len(link) - 4)] + "... "  # Trim and add ellipsis
    else:
        preview_text = text

    # Return the preview response
    return {
        "preview_text": preview_text,
        "link": link
    }

@app.post("/post")
async def post_social(post: SocialPost):
    # Debug
    # print(f"Received username: {post.username}", flush=True)
    # print(f"Received password: {post.password}", flush=True)
    # print(f"Received text: {post.text}", flush=True)
    # print(f"Received link: {post.link}", flush=True)

    # Calculate the total length of text and link 
    text = post.text
    link = post.link if post.link else ""
    username = post.username
    password = post.password

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

        return response
    except Exception as e:
        print(f"Failed to post: {e}")
        return {'error': 'Failed to send post'}, 500



@app.post("/post/mastodon")
async def post_to_mastodon(post: SocialPost):
    """
    Post to Mastodon.

    Args:
        post (SocialPost): Contains the text, optional link, and the Mastodon instance URL (baseURL).
        the password is the API key for Mastodon.

    Returns:
        dict: Response from Mastodon or status message.
    """
    # Ensure the baseURL is provided for Mastodon posts
    if not post.baseURL:
        raise HTTPException(status_code=400, detail="baseURL is required for Mastodon posting.")

    # Construct the API URL from the baseURL provided
    mastodon_api_url = f"{post.baseURL.rstrip('/')}/api/v1/statuses"

    # Construct the payload for Mastodon API
    text = post.text[:499] + "..." if len(post.text) > 499 else post.text
    payload = {
        "status": text + (" " + post.link if post.link else "")
    }

    # The API Key will be used as the password for authentication
    if not post.password:
        raise HTTPException(status_code=400, detail="Password (API key) is required for Mastodon posting.")
    mastodon_api_key = post.password

    if not mastodon_api_key:
        raise HTTPException(status_code=500, detail="Missing Mastodon API key")

    # Send POST request to Mastodon API
    try:
        response = requests.post(
            mastodon_api_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {mastodon_api_key}",
                "Content-Type": "application/json"
            }
        )
        # Check if Mastodon accepted the post
        if response.status_code == 200:
            return {"message": "Post successfully shared on Mastodon"}
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"Failed to post to Mastodon: {e}")
        return {'error': 'Failed to send post'}, 500