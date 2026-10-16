import json
import os
import urllib.parse
import urllib.request

STREAMER = "caedrel"
STATE_FILE = "state.txt"

CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"]
NTFY_TOPIC = os.environ["NTFY_TOPIC"]


def get_token():
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    }).encode()
    with urllib.request.urlopen("https://id.twitch.tv/oauth2/token", data=data) as r:
        return json.load(r)["access_token"]


def get_stream(token):
    url = "https://api.twitch.tv/helix/streams?user_login=" + STREAMER
    req = urllib.request.Request(url, headers={
        "Client-ID": CLIENT_ID,
        "Authorization": "Bearer " + token,
    })
    with urllib.request.urlopen(req) as r:
        items = json.load(r)["data"]
    return items[0] if items else None


def notify(stream):
    title = stream["user_name"] + " is LIVE"
    body = (stream.get("title") or "") + "\nPlaying: " + (stream.get("game_name") or "?")
    req = urllib.request.Request(
        "https://ntfy.sh/" + NTFY_TOPIC,
        data=body.encode("utf-8"),
        headers={
            "Title": title.encode("ascii", "ignore").decode(),
            "Click": "https://twitch.tv/" + STREAMER,
            "Priority": "high",
            "Tags": "tv",
        },
    )
    urllib.request.urlopen(req)


def main():
    last = ""
    if os.path.exists(STATE_FILE):
        last = open(STATE_FILE).read().strip()

    stream = get_stream(get_token())
    if stream is None:
        print("Offline")
        return

    if stream["id"] == last:
        print("Live, already notified")
        return

    notify(stream)
    open(STATE_FILE, "w").write(stream["id"])
    print("Notified")


if __name__ == "__main__":
    main()
