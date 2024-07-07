#!/usr/bin/env python
# coding: utf-8

import requests
from urllib.parse import urlencode
import base64
import webbrowser

client_id = "{Enter your Spotify Client ID}"
client_secret = "{Enter your Spotify Client Secret}"

auth_headers = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": "http://localhost:7777/callback",
    "scope": "user-library-read playlist-modify-public"
}

webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

code = "{Enter the auth callback code}"

encoded_credentials = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")

token_headers = {
    "Authorization": "Basic " + encoded_credentials,
    "Content-Type": "application/x-www-form-urlencoded"
}

token_data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": "http://localhost:7777/callback"
}

r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)

token = r.json()["access_token"]

user_headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
}


end=False
ctr = 0
liked_uris = []
liked_names = []

while (end!=True):
    get_liked = requests.get(f"https://api.spotify.com/v1/me/tracks?offset={ctr}&limit=50",headers=user_headers)
    if get_liked.json()["next"] is None:
        end = True
    else:
        ctr = ctr + 50
    get_liked_json = get_liked.json()["items"]
    for item in get_liked_json:
        liked_names.append(item["track"]["name"])
        liked_uris.append(item["track"]["uri"])

user_id = requests.get("https://api.spotify.com/v1/me",headers=user_headers).json()["id"]
print(user_id)

playlist_create_endpoint = f"https://api.spotify.com/v1/users/{user_id}/playlists"
print(playlist_create_endpoint)

post_body = {
    "name":"{Enter Playlist Name}",
    "public":True,
    "description":"{Enter Playlist Description}"
}

create_playlist = requests.post(playlist_create_endpoint,headers=user_headers,json=post_body)
print(create_playlist.status_code)
print(create_playlist.json())

playlist_id = create_playlist.json()["id"]
print(playlist_id)

for i in range(0,int((len(liked_uris)/100))+1):
    if (i == int((len(liked_uris)/100))):
        post_body = {
            "uris": liked_uris[(100*i):len(liked_uris)-1]
        }
    else:
        post_body = {
            "uris": liked_uris[(100*i):(100*i)+99]
        }
    requests.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",json=post_body,headers=user_headers)
