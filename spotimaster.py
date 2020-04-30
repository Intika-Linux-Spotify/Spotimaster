#!/usr/bin/env python3.6

App = 'Spotimaster v3.4'
Link = 'https://github.com/Intika-Linux-Spotify/Spotimaster'

# Spotimaster
# Control spotifyd/spotify with dbus and web-api...
# intika - http://github.com/intika

#   
# Install:   
# 1. change the python value on the first line to match your version (using python3.6 by default)... 
#    this application require python3.x
# 2. Check the required applications/packages bellow
# 3. Run 'chmod 755 ./spotimaster.py'
# 4. Link or copy the application to bin folder with
#    'ln -s ./spotimaster.py /usr/bin/spotimaster'
#
# required packages are: dbus-python, requests, urllib3 ('pip3 install dbus-python requests urllib3')
# required applications: spotifyd/spotify, spotty for web-api functions and dbus-send for openuri command
# spotty is available here: https://github.com/michaelherger/spotty, git clone it then use 'cargo build --release'
# you do need an app-id to use spotty, you can generate it here https://developer.spotify.com/dashboard/applications/
# app-secret and web authorisations (redirects...) are not required.
#
# Note :
# - Change the cache location if required by editing the variable 'cache_location' bellow
# - If you want to save spotty parameters directly here, you can edit the variable 'spotty_params' bellow, leave empty if not used. 
# - If you want to use this application's dbus function with an other player change the playername bellow
#

cache_location = '/tmp'
spotty_params = ''
player='spotifyd'

#########################################################################################################################################
#########################################################################################################################################

import os
import sys
import dbus
import time
import json
import requests
import subprocess
import urllib.request as urx
from dbus import DBusException

#########################################################################################################################################

if (not len(sys.argv) > 1) or (sys.argv[1] == '--help'):

    print('\033[1;34;40m')
    print(App)
    print(Link)
    print('')
    print('Local commands:')
    print('---------------')
    print('\033[0;37;40m')
    print('--help           display help page')
    print('')
    print('-playpause       pause/play playback over dbus mpris')
    print('-next            load next song over dbus mpris')
    print('-prev            load previous song over dbus mpris')
    print('')
    print('-openuri         load song/playlist over dbus mpris... examples:')
    print('\033[0;32;40m                 spotimaster -openuri spotify:track:2oNibyaUGIHWXtYIkVtxIt')
    print('\033[0;32;40m                 spotimaster -openuri spotify:user:spotify:playlist:37i9dQZF1DZ06evO3OC4Te')
    print('\033[0;37;40m')
    print('-check           this parameter can not be combined with others, it is used to')
    print('                 check if spotifyd is running correctly, this will check')
    print('                 dbus mpris communication and return the text true if')
    print('                 everything is ok...')
    print('')
    print('--spotify        target spotify instead of spotifyd for dbus functions')

    print('\033[1;34;40m')
    print('Online commands:')
    print('----------------')
    print('\033[0;37;40m')

    print('-wplaypause      pause/play playback over spotify web-api, please read the Web-API note bellow')
    print('-wnext           load next song over spotify web-api, please read the Web-API note bellow')
    print('-wprev           load previous song over spotify web-api, please read the Web-API note bellow')
    print('')
    
    print('-love            save the current song to the library, please read the Web-API note bellow')
    print('-unlove          delete the current song from the library, please read the Web-API note bellow')
    print('-isloved         check if the current song was added to the library, please read the Web-API note bellow')
    print('')

    print('-wopenuri        load song/playlist over spotify web-api examples:')
    print('\033[0;32;40m                 spotimaster -wopenuri spotify:track:2oNibyaUGIHWXtYIkVtxIt ...')
    print('\033[0;32;40m                 spotimaster -wopenuri spotify:user:spotify:playlist:37i9dQZF1DZ06evO3OC4Te ...')
    print('\033[0;37;40m                 device_id parameter may be added on a futur version... currently this will play ')
    print('                 the uri on the current playback device...')
    print('')
    print('-get-devices     list available devices on the current spotify account... this can be used for instance with ')
    print('                 --nostatus --quiet to get a clean json output to be used on an other application...')
    
    print('\033[1;34;40m')
    print('Advanced:')
    print('---------')
    print('\033[0;37;40m')
    print('--superlove      work only with -love, it re save the song to push it at the top of the saved list')
    print('--clear          delete cache file and exit, when using this all other parameters will be ignored')
    print('--quiet          minimal stout, no detail.')
    print('--nostatus       command status is always indicated by the exit code but also with an additional')
    print('                 text value true/false at the end of the output, this parameter disable that text')
    print('                 exit codes are not modified, 0 for successful and 1 for failed.')
    print('')
    print('--use-chache     this is valid only for Web-API commands, and do provide:')
    print('                     - force usage of the cached token')
    print('                     - do not request a new token')
    print('                     - do not check timestamp')
    print('                     - do not run spotty')
    print('                     - ignore spotty arguments')
    print('')
    print('--force          force token update ignore complitely the caching system:')
    print('                     - request a new token with spotty')
    print('                     - ignore cached token if there is one')
    print('                     - delete current cache')
    print('                     - do not create cache file')
    print('\033[1;34;40m')
    print('Notes:')
    print('------')
    print('\033[0;37;40m')
    print('Special:         parameters -use-cache, -force, -spotify, -superlove, -clear and -quiet can be anywhere on the line.')
    print('')
    print('Online Web-API:  parameter that are using the spotify Web-API require spotty to be installed, spotty is used')
    print('                 to generate a valid token, that token is cached to /tmp folder and is regenerated when required.')
    print('                 Spotty need some parameters for the authentication to succeed; All parameters following the first')
    print('                 one will be passed to spotty... this is required! (except for -use-cache)')
    print('')
    print('                 examples:')
    print('\033[0;32;40m')
    print('                 spotimaster -love -n APP-NAME-WHATEVER -c /tmp/spotty -u USERNAME -t -i MY-APP-ID -p MYPASSWORD \\') 
    print('                 --scope user-modify-playback-state,user-library-modify,user-read-currently-playing,user-read-playback-state')
    print('\033[0;37;40m')
    print('')
    sys.exit(0)

if ((sys.argv[1] != "-love") and (sys.argv[1] != "-playpause") and (sys.argv[1] != "-next") and (sys.argv[1] != "-prev") and
    (sys.argv[1] != "-unlove") and (sys.argv[1] != "-wplaypause") and (sys.argv[1] != "-wnext") and (sys.argv[1] != "-wprev") and 
    (sys.argv[1] != "-isloved") and (sys.argv[1] != "-openuri") and (sys.argv[1] != "-check") and (sys.argv[1] != "-quiet") and 
    (sys.argv[1] != "-use-cache") and (sys.argv[1] != "-force") and (sys.argv[1] != "-clear") and (sys.argv[1] != "-superlove") and 
    (sys.argv[1] != "-spotify") and (sys.argv[1] != "--use-cache") and (sys.argv[1] != "--force") and (sys.argv[1] != "--spotify") and
    (sys.argv[1] != "--superlove") and (sys.argv[1] != "--clear") and (sys.argv[1] != "--quiet") and (sys.argv[1] != "-wopenuri") and
    (sys.argv[1] != "-get-devices") and (sys.argv[1] != "-nostatus") and (sys.argv[1] != "--nostatus")):

    arguments = ' '.join(sys.argv[1:])

    print('')
    print(App)
    print(Link)
    print('')
    print(sys.argv[1])
    print('invalid parameter')
    print('Check: spotimaster --help')
    print('')
    if not '-nostatus' in arguments:
        print('false')
    sys.exit(1)

#########################################################################################################################################

force = False
quiet = False
nostatus = False
superlove = False
wopenuri_link = ''
force_cache = False
spotifyd_bus = None
spotifyd_properties = None
spotifyd_need_reboot = False
session_bus = dbus.SessionBus()

#########################################################################################################################################

arguments = ' '.join(sys.argv[1:])

#quiet need to be the first check
if '-quiet' in arguments:
    quiet = True
    if '--quiet' in arguments: sys.argv.remove('--quiet')
    else: sys.argv.remove('-quiet')

if not quiet:
    print('')
    print(App)
    print(Link)
    print('')
    
if '-clear' in arguments:
    try: 
        os.remove(cache_location + '/spotimaster.json')
        if not quiet: print('Cache file cleaned...')
    except:
        if not quiet: print('Cache already cleaned...')

    if not quiet: print('')
    sys.exit(0)

if '-superlove' in arguments:
    superlove = True
    if '--superlove' in arguments: sys.argv.remove('--superlove')
    else: sys.argv.remove('-superlove')

if '-spotify' in arguments:
    player = 'spotify'
    if '--spotify' in arguments: sys.argv.remove('--spotify')
    else: sys.argv.remove('-spotify')

if '-nostatus' in arguments:
    nostatus = True
    if '--nostatus' in arguments: sys.argv.remove('--nostatus')
    else: sys.argv.remove('-nostatus')
    
if '-force' in arguments:
    force = True

    if '--force' in arguments: sys.argv.remove('--force')
    else: sys.argv.remove('-force')

    try: 
        os.remove(cache_location + '/spotimaster.json')
        if not quiet: print('Cache file cleaned...')
    except:
        if not quiet: print('Cache already cleaned...')
    
if '-use-cache' in arguments:
    force_cache = True
    if '--use-cache' in arguments: sys.argv.remove('--use-cache')
    else: sys.argv.remove('-use-cache')

if ((('-use-cache' in arguments) and ('-force' in arguments)) or
    (('--use-cache' in arguments) and ('-force' in arguments)) or
    (('--use-cache' in arguments) and ('--force' in arguments)) or
    (('-use-cache' in arguments) and ('--force' in arguments))):

    if not quiet: print('')
    print('Silly... you can not use -force and -use-cache together')
    if not quiet: print('')
    if not nostatus: print('false')
    sys.exit(1)
    
# wopenuri need to be the last check 
if (sys.argv[1] == "-wopenuri"):
    if (not len(sys.argv) > 2):
        print('Please provide an uri, example: "spotimaster -wopenuri spotify:track:2oNibyaUGIHWXtYIkVtxIt"')
        if not quiet: print('')
        if not nostatus: print('false')
        sys.exit(1)
    else:
        wopenuri_link = sys.argv[2]
        sys.argv.remove(sys.argv[2]) #need to be removed to keep clean spotty parameters        
    
#########################################################################################################################################

if (sys.argv[1] == "-check"):    
    try:
        spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2." + player, "/org/mpris/MediaPlayer2")
        spotifyd_properties = dbus.Interface(spotifyd_bus, "org.freedesktop.DBus.Properties")
    except DBusException:
        spotifyd_need_reboot = True

    if not spotifyd_need_reboot:
        try:
            metadata = spotifyd_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            playback_status = spotifyd_properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
        except DBusException:
            spotifyd_need_reboot = True

    if spotifyd_need_reboot:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    else:
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
        
    sys.exit(0)

#########################################################################################################################################

#Prepare the access token for the Web-API
if ((sys.argv[1] == "-love") or (sys.argv[1] == "-unlove") or (sys.argv[1] == "-isloved") or (sys.argv[1] == "-wplaypause") or (sys.argv[1] == "-wnext") or 
    (sys.argv[1] == "-wprev") or (sys.argv[1] == "-wopenuri") or (sys.argv[1] == "-get-devices")):

    if ((not len(sys.argv) > 2) and (spotty_params == '') and not force_cache):
        print('Please provide spotty parameters, check --help for more infos')
        if not quiet: print('')
        if not nostatus: print('false')
        sys.exit(1)
    else:
        if (spotty_params == ''):
            spotty_params = ' '.join(sys.argv[2:])

    token_require_update = False

    if not force:
        try:
            with open(cache_location + '/spotimaster.json') as json_file:
                token_data = json.load(json_file)
                if not quiet: print('Cached token loaded...')
                if not quiet: print('')
                if not quiet: print(token_data)
                if not quiet: print('')
                if ((token_data['timestamp'] + 3200) > (time.time())):
                    if not quiet: print('Token still valid ;)')
                    if not quiet: print('')
                else:
                    if not quiet: print('Token expired...')
                    if not quiet: print('')
                    token_require_update = True
        except:
            token_require_update = True
    else:
        token_require_update = True
            
    if token_require_update and not force_cache:
        if not quiet: print('Updating/getting a token...')
        if not quiet: print('')
        spottyresult = subprocess.Popen("spotty " + spotty_params, shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")

        #Note json.load vs json.loads = load json vs load string to json 
        try:
            token_data = json.loads(spottyresult)
            if not quiet: print('Adding timestamp to the token...')
            token_data['timestamp'] = time.time()
            if not quiet: print('')
            if not quiet: print(token_data)
            if not quiet: print('')
        except:
            if not quiet: print(spottyresult)
            if not quiet: print('')
            print('Unable to read/get the token... request cancelled')
            if not quiet: print('')
            if not nostatus: print('false')
            sys.exit(1)

    if not force:
        try:
            with open(cache_location + '/spotimaster.json', 'w') as outfile:
                json.dump(token_data, outfile)
        except:
            if not quiet: print('')
            if not quiet: print('Cache content:')
            if not quiet: print('')
            if not quiet: print(token_data)
            if not quiet: print('')
            print('Unable to save cache file... request cancelled')
            if not quiet: print('')
            if not nostatus: print('false')
            sys.exit(1)

    if force_cache:
        if not quiet: print('Forcing token usage...')
        if not quiet: print('')

    try:    
        access_token = token_data['accessToken']
        if not quiet: print('Token:')
        if not quiet: print(access_token)
        if not quiet: print('')
    except:
        print('Failed to parse a token...')
        if not quiet: print('')
        if not nostatus: print('false')
        sys.exit(1)       
            
#########################################################################################################################################


if (sys.argv[1] == "-love"):

    if not quiet: print('Getting current spotify song...')
    ####################################################
    if not quiet: print('')
        
    req = urx.Request("https://api.spotify.com/v1/me/player/currently-playing")
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    
    data_new = json.loads(urx.urlopen(req).read())
    currentSongID = data_new['item']["id"]
    
    if not quiet: print("Song: " + data_new['item']['artists'][0]['name'] + " - " + data_new['item']['name'])
    if not quiet: print("Song ID: " + data_new['item']['id'])
    if not quiet: print('')

    if not quiet: print('Check if it is already saved...')
    ####################################################
    if not quiet: print('')
    
    req = urx.Request("https://api.spotify.com/v1/me/tracks/contains?ids=%s" % currentSongID, method='GET')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    data_check = json.loads(urx.urlopen(req).read())
    
    if data_check[0] and not superlove:
        if not quiet: print('Song already saved')
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
    
    if not quiet: print('Saving current spotify song...')
    ####################################################
    if not quiet: print('')
    
    req = urx.Request("https://api.spotify.com/v1/me/tracks?ids=%s" % currentSongID, method='PUT')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    urx.urlopen(req)
    
    if not quiet: print('Check if saved again...')
    ####################################################
    if not quiet: print('')
    
    req = urx.Request("https://api.spotify.com/v1/me/tracks/contains?ids=%s" % currentSongID, method='GET')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    data_check = json.loads(urx.urlopen(req).read())

    if data_check[0]: 
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
    else:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    
    sys.exit(0)

#########################################################################################################################################
    
if (sys.argv[1] == "-unlove"):

    if not quiet: print('Getting current spotify song...')
    ####################################################
    if not quiet: print('')
        
    req = urx.Request("https://api.spotify.com/v1/me/player/currently-playing")
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    
    data_new = json.loads(urx.urlopen(req).read())
    currentSongID = data_new['item']["id"]

    if not quiet: print("Song: " + data_new['item']['artists'][0]['name'] + " - " + data_new['item']['name'])
    if not quiet: print("Song ID: " + data_new['item']['id'])
    if not quiet: print('')    

    if not quiet: print('Check if it is already removed...')
    ####################################################
    if not quiet: print('')
    
    req = urx.Request("https://api.spotify.com/v1/me/tracks/contains?ids=%s" % currentSongID, method='GET')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    data_check = json.loads(urx.urlopen(req).read())

    if not data_check[0]: 
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
    else:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    
    if not quiet: print('Delete current spotify song...')
    ####################################################
    if not quiet: print('')
    
    req = urx.Request("https://api.spotify.com/v1/me/tracks?ids=%s" % currentSongID, method='DELETE')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    urx.urlopen(req)
    
    if not quiet: print('Check the operation succeed...')
    ####################################################
    if not quiet: print('')
    
    req = urx.Request("https://api.spotify.com/v1/me/tracks/contains?ids=%s" % currentSongID, method='GET')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    data_check = json.loads(urx.urlopen(req).read())
    
    if not data_check[0]: 
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
    else:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    
    sys.exit(0)

#########################################################################################################################################
    
if (sys.argv[1] == "-isloved"):

    if not quiet: print('Getting current spotify song...')
    ####################################################
    if not quiet: print('')
        
    req = urx.Request("https://api.spotify.com/v1/me/player/currently-playing")
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    
    data_new = json.loads(urx.urlopen(req).read())
    currentSongID = data_new['item']["id"]

    if not quiet: print("Song: " + data_new['item']['artists'][0]['name'] + " - " + data_new['item']['name'])
    if not quiet: print("Song ID: " + data_new['item']['id'])
    if not quiet: print('')
    
    if not quiet: print('Check if it is saved...')
    ####################################################
    if not quiet: print('')

    req = urx.Request("https://api.spotify.com/v1/me/tracks/contains?ids=%s" % currentSongID, method='GET')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    data_check = json.loads(urx.urlopen(req).read())

    if data_check[0]: 
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
    else: 
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)

    sys.exit(0)

#########################################################################################################################################
    
if (sys.argv[1] == "-wplaypause"):

    if not quiet: print('Getting playback state and current spotify song...')
    ####################################################
    if not quiet: print('')
        
    req = urx.Request("https://api.spotify.com/v1/me/player/currently-playing")
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")

    data_new = json.loads(urx.urlopen(req).read())
    isPlaying = data_new['is_playing']
    
    if not quiet: print("Song: " + data_new['item']['artists'][0]['name'] + " - " + data_new['item']['name'])
    if not quiet: print("Song ID: " + data_new['item']['id'])
    if not quiet: print('')
    if not quiet: print('Is playing:')
    if not quiet:
        if isPlaying: print('true')
        else: print ('false')
        print('')

    if not quiet: print('Switching playback result...')
    ####################################################
    if not quiet: print('')
    
    if isPlaying:
        req = urx.Request("https://api.spotify.com/v1/me/player/pause", method='PUT')
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", "Bearer " + access_token)
        req.add_header("User-Agent", "Mozilla/5.0")
        try:
            urx.urlopen(req).read()
            if not nostatus: print('true')
            if not quiet: print('')
            sys.exit(0)
        except:
            if not nostatus: print('false')
            if not quiet: print('')
            sys.exit(1)
    else:
        req = urx.Request("https://api.spotify.com/v1/me/player/play", method='PUT')
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", "Bearer " + access_token)
        req.add_header("User-Agent", "Mozilla/5.0")
        try:
            urx.urlopen(req).read()
            if not nostatus: print('true')
            if not quiet: print('')
            sys.exit(0)
        except:
            if not nostatus: print('false')
            if not quiet: print('')
            sys.exit(1)
            
    sys.exit(0)

#########################################################################################################################################
    
if (sys.argv[1] == "-wnext"):

    if not quiet: print('Requesting next song...')
    ####################################################
    if not quiet: print('')
    
    req = urx.Request("https://api.spotify.com/v1/me/player/next", method='POST')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        urx.urlopen(req).read()
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
    except:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
        
    sys.exit(0)

#########################################################################################################################################
    
if (sys.argv[1] == "-wprev"):

    if not quiet: print('Requesting previous song...')
    ####################################################
    if not quiet: print('')
    
    req = urx.Request("https://api.spotify.com/v1/me/player/previous", method='POST')
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", "Bearer " + access_token)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        urx.urlopen(req).read()
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
    except:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
        
    sys.exit(0)

#########################################################################################################################################

if (sys.argv[1] == "-get-devices"):

    if not quiet: print('Requesting device list...')
    ####################################################
    if not quiet: print('')

    Headers = {"Authorization": "Bearer " + access_token}

    resp = requests.get("https://api.spotify.com/v1/me/player/devices", headers=Headers)

    try:
        print(resp.text)
        if not quiet: print('')
        if not quiet: print('Answer status code:')
        if not quiet: print(resp.status_code)
        if not quiet: print('')
    except:
        if not quiet: print('Parsing web request details not complete')

    if resp.status_code > 399:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    else:
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
        
    sys.exit(0)

#########################################################################################################################################
    
if (sys.argv[1] == "-wopenuri"):

    if not quiet: print('Preparing the given uri...')
    ####################################################
    if not quiet: print('')
    
    if wopenuri_link == '':
        print('Unable to read the given uri')
        if not quiet: print('')
        if not nostatus: print('false')
        sys.exit(1)

    if not quiet: print('Uri:')
    if not quiet: print(wopenuri_link)
    if not quiet: print('')
    
    if not quiet: print('Requesting the given uri...')
    ####################################################
    if not quiet: print('')

    Params = {}
    Payload = {}
    Headers = {"Authorization": "Bearer " + access_token}

    #needed for additional features...     
    #params['device_id'] = 'xxxxxxxxxxxxxxxxxxx'

    if 'track' in wopenuri_link:    Payload = {'uris':         [wopenuri_link]}
    else:                           Payload = {'context_uri':   wopenuri_link}

    if not quiet: print('Payload:')
    if not quiet: print(wopenuri_link)
    if not quiet: print('')
        
    try:
        response = requests.put("https://api.spotify.com/v1/me/player/play", params=Params, headers=Headers, json=Payload)
        #if not quiet: print(response.request.headers)
        if not quiet: print('Answer status code:')
        if not quiet: print(response.status_code)
        if not quiet: print('')
    except:
        if not quiet: print('Parsing web request details not complete')

    if response.status_code > 399:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    else:
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
            
    sys.exit(0)
    
#########################################################################################################################################

if (sys.argv[1] == "-playpause"):
    try:
        spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2." + player, "/org/mpris/MediaPlayer2")
        spotifyd_interface = dbus.Interface(spotifyd_bus, "org.mpris.MediaPlayer2.Player")
    except DBusException:
        spotifyd_need_reboot = True

    if not spotifyd_need_reboot:
        try:
            spotifyd_interface.PlayPause()
        except DBusException:
            spotifyd_need_reboot = True        

    if spotifyd_need_reboot:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    else:
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
        
    sys.exit(0)

#########################################################################################################################################

if (sys.argv[1] == "-next"):
    try:
        spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2." + player, "/org/mpris/MediaPlayer2")
        spotifyd_interface = dbus.Interface(spotifyd_bus, "org.mpris.MediaPlayer2.Player")
    except DBusException:
        spotifyd_need_reboot = True

    if not spotifyd_need_reboot:
        try:
            spotifyd_interface.Next()
        except DBusException:
            spotifyd_need_reboot = True        

    if spotifyd_need_reboot:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    else:
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
        
    sys.exit(0)

#########################################################################################################################################
    
if (sys.argv[1] == "-prev"):
    try:
        spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2." + player, "/org/mpris/MediaPlayer2")
        spotifyd_interface = dbus.Interface(spotifyd_bus, "org.mpris.MediaPlayer2.Player")
    except DBusException:
        spotifyd_need_reboot = True

    if not spotifyd_need_reboot:
        try:
            spotifyd_interface.Previous()
        except DBusException:
            spotifyd_need_reboot = True        

    if spotifyd_need_reboot:
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    else:
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
        
    sys.exit(0)

#########################################################################################################################################
    
if (sys.argv[1] == "-openuri"):
    if (not len(sys.argv) > 2):
        print('Please provide an uri, example: "spotimaster -openuri spotify:track:2oNibyaUGIHWXtYIkVtxIt"')
        if not quiet: print('')
        if not nostatus: print('false')
        sys.exit(1)
    else:
        uri = sys.argv[2]

    # Often, spotifyd require this many times, i don't know why, plus it does not work with the classic dbus interface where it does work with spotify 
    
    attemptone = subprocess.Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2." + player + " /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:'" + uri + "'",
                 shell=True, stdout=subprocess.PIPE).stdout.read()
    attempttwo = subprocess.Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2." + player + " /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:'" + uri + "'",
                 shell=True, stdout=subprocess.PIPE).stdout.read()

    # Capturing full result of last attempt
    childthree = subprocess.Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2." + player + " /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:'" + uri + "'",
                 shell=True, stdout=subprocess.PIPE)

    result, err = childthree.communicate()
    exitcode    = childthree.returncode

    if not quiet: print('')
    if not quiet: print(attemptone)
    if not quiet: print('')
    if not quiet: print(attempttwo)
    if not quiet: print('')
    if not quiet: print(result)
    if not quiet: print('')
    if not quiet: print('Exit code: ' + str(exitcode))
    if not quiet: print('')
    
    if exitcode != 0: 
        if not quiet: print(err)
        if not quiet: print('')
        if not nostatus: print('false')
        if not quiet: print('')
        sys.exit(1)
    else:
        if not nostatus: print('true')
        if not quiet: print('')
        sys.exit(0)
        
    sys.exit(0)
    
    # Work with spotify but not spotifyd
    #uri="spotify:track:2oNibyaUGIHWXtYIkVtxIt" #test uri...
    #try:
    #    spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2." + player, "/org/mpris/MediaPlayer2")
    #    spotifyd_interface = dbus.Interface(spotifyd_bus, "org.mpris.MediaPlayer2.Player")
    #except DBusException:
    #    spotifyd_need_reboot = True

    #if not spotifyd_need_reboot:
    #    try:
    #        spotifyd_interface.OpenUri(uri)
    #    except DBusException:
    #        spotifyd_need_reboot = True        

    #if spotifyd_need_reboot:
    #    if not nostatus: print('false')
    #    if not quiet: print('')
    #    sys.exit(1)
    #else:
    #    if not nostatus: print('true')
    #    if not quiet: print('')
    #    sys.exit(0)
    #
    #sys.exit(0)
		
#########################################################################################################################################
