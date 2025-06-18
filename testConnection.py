import requests
from requests.auth import HTTPBasicAuth

# Site and credentials
username = ''
app_password = ''
site_url = ''  # correct endpoint
# Content to post
post = {
    "title": "Test Post from Python",
    "content": "Hello world! This post was created using Python.",
    "status": "publish"
}

# Send it
response = requests.post(
    site_url,  # no /posts added here
    auth=HTTPBasicAuth(username, app_password),
    json=post
)

# Check result
if response.status_code == 201:
    print("Success! Post created.")
    print(response.json()['link'])
else:
    print("Failed:", response.status_code, response.text)
