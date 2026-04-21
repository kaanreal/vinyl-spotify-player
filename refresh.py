import requests;
import time;

import os;

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID");
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET");
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN");

def refresh_access_token():
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )

    data = response.json()
    access_token = data["access_token"]

    with open("access_token.txt", "w") as f:
        f.write(access_token)

    print("Neues Access Token gespeichert!")
    return access_token

while True:
    refresh_access_token()
    time.sleep(3300)  # 55 minutes
