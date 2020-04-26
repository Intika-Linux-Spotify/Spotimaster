import json
import urllib.request as urx
import sys
import keyboard

# rl -X PUT "https://api.spotify.com/v1/me/tracks?ids=ssadasdasd" -H "Accept: application/json"

globalauth = "Bearer TOKEN"

isquit = False

def saveCurrentSong():

    # Get Current Song ID
    # curl -X GET "https://api.spotify.com/v1/me/player/currently-playing"

    req = urx.Request("https://api.spotify.com/v1/me/player/currently-playing")
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", globalauth)
    req.add_header("User-Agent", "Mozilla/5.0")

    data_new = json.loads(urx.urlopen(req).read())

    # Current song ID is data_new['item']['id']

    # print("Saving " + data_new['item']['artists'][0]['name'] + " - " + data_new['item']['name'])

    currentSongID = data_new['item']["id"]
    # Save current song to Self

    req = urx.Request("https://api.spotify.com/v1/me/tracks?ids=%s" % currentSongID, method='PUT')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", globalauth)
    req.add_header("User-Agent", "Mozilla/5.0")

    urx.urlopen(req)

    # print("Saved.")

def quickQuit():
    isquit = True



keyboard.add_hotkey('ctrl+alt+o+p', saveCurrentSong())
keyboard.add_hotkey('ctrl+alt+o+t', quickQuit())

while True:
    if isquit == True:
        sys.exit()
    else:
        pass
