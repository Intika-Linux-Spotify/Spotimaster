#!/usr/bin/env python3.6

# Spotimaster v1.5
# Control spotifyd with dbus and web-api...
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
# required packages are: dbus-python, requests ('pip3 install dbus-python requests')
# required applications: spotifyd/spotify, spotty for web-api functions and dbus-send for openuri command
# spotty is available here: https://github.com/michaelherger/spotty, git clone it then use 'cargo build --release'
#
# Note :
# - Change the cache location if required by editing the variable 'cache_location' bellow
# - If you want to save spotty parameters directly here, you can edit the variable 'spotty_params' bellow, leave empty if not used. 
#

cache_location = '/tmp'
spotty_params = ''

#########################################################################################################################################

import re
import sys
import dbus
import time
import json
import subprocess
import urllib.request as urx
from dbus import DBusException

#########################################################################################################################################

if (not len(sys.argv) > 1) or (sys.argv[1] == '--help'):
    print('')
    print('Available parameters: ')
    print('')
    print('--help           display help page')
    print('')
    print('-love            save the current song to the library, please read the Web-API note bellow')
    print('-unlove          delete the current song from the library, please read the Web-API note bellow')
    print('-isloved         check if the current song was added to the library, please read the Web-API note bellow')
    print('')
    print('-playpause       pause/play playback over dbus mpris')
    print('-next            load next song over dbus mpris')
    print('-prev            load previous song over dbus mpris')
    print('')
    print('-wplaypause      pause/play playback over spotify web-api, please read the Web-API note bellow')
    print('-wnext           load next song over spotify web-api, please read the Web-API note bellow')
    print('-wprev           load previous song over spotify web-api, please read the Web-API note bellow')
    print('')
    print('-openuri         load song/playlist over dbus mpris')
    print('                 example: "spotimaster -openuri spotify:track:2oNibyaUGIHWXtYIkVtxIt"')
    print('-wopenuri        ...not implemented yet')
    print('')
    print('-check           this parameter can not be combined with others, it is used to')
    print('                 check if spotifyd is running correctly, this will check')
    print('                 dbus mpris communication and return the text true if')
    print('                 everything is ok...')
    print('')
    print('Web-API Note:    parameter that are using the spotify Web-API require spotty to be installed, spotty is used')
    print('                 to generate a valid token, that token is cached to /tmp folder and is regenerated when required.')
    print('                 Spotty need some parameters for the authentication to succeed; All parameters following the first')
    print('                 one will be passed to spotty... this is required! here are two examples:')
    print('                 spotimaster -love -n APP-NAME-WHATEVER -c /tmp/spotty -u USERNAME -t -i MY-APP-ID -p MYPASSWORD')
    print('                 spotimaster -wnext -n APP-NAME-WHATEVER -c /tmp/spotty -u USERNAME -t -i MY-APP-ID -p MYPASSWORD')
    print('')
    sys.exit()

if ((sys.argv[1] != "-love") and (sys.argv[1] != "-playpause") and (sys.argv[1] != "-next") and (sys.argv[1] != "-prev") and
    (sys.argv[1] != "-unlove") and (sys.argv[1] != "-wplaypause") and (sys.argv[1] != "-wnext") and (sys.argv[1] != "-wprev") and 
    (sys.argv[1] != "-isloved") and (sys.argv[1] != "-openuri") and (sys.argv[1] != "-check")):
    print('Invalid parameter')
    print('')
    sys.exit()

#########################################################################################################################################

spotifyd_bus = None
spotifyd_properties = None
spotifyd_need_reboot = False
session_bus = dbus.SessionBus()

#########################################################################################################################################

if (sys.argv[1] == "-check"):    
    try:
        spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotifyd", "/org/mpris/MediaPlayer2")
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
        print('false')
    else:
        print('true')
        
    sys.exit()

#########################################################################################################################################

#Prepare Web-API
if ((sys.argv[1] == "-love") or (sys.argv[1] == "-unlove") or (sys.argv[1] == "-isloved") or (sys.argv[1] == "-wplaypause") or (sys.argv[1] == "-wnext") or (sys.argv[1] == "-wprev")):

    if ((not len(sys.argv) > 2) and (spotty_params == '')):
        print('Please provide spotty parameters, check --help for more infos')
        print('')
        sys.exit()
    else:
        if (spotty_params == ''):
            spotty_params = ' '.join(sys.argv[2:])

    token_require_update = False
    
    try:
        with open(cache_location + '/spotimaster.json') as json_file:
            token_data = json.load(json_file)
            print('Cached token loaded...')
            print('')
            print(token_data)
            print('')
            if ((token_data['timestamp'] + 3200) > (time.time())):
                print('Token still valid ;)')
                print('')
            else:
                print('Token expired...')
                print('')
                token_require_update = True
    except:
        token_require_update = True
    
    if token_require_update:
        print('Updating/getting a token...')
        print('')
        spottyresult = subprocess.Popen("spotty " + spotty_params, shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")

        #Note json.load vs json.loads = load json vs load string to json 
        try:
            token_data = json.loads(spottyresult)
            print('Adding timestamp to the token...')
            token_data['timestamp'] = time.time()
            print('')
            print(token_data)
            print('')
        except:
            print(spottyresult)
            print('')
            print('Unable to read/get the token... request cancelled')
            print('')
            sys.exit()

    try:
        with open(cache_location + '/spotimaster.json', 'w') as outfile:
            json.dump(token_data, outfile)
    except:
        print('')
        print('Cache content:')
        print('')
        print(token_data)
        print('')
        print('Unable to save cache file... request cancelled')
        print('')
        sys.exit()

    access_token = token_data['accessToken']       
            
#########################################################################################################################################


if (sys.argv[1] == "-love"):
    print('')
    sys.exit()

#########################################################################################################################################
    
if (sys.argv[1] == "-unlove"):
    print('')
    sys.exit()

#########################################################################################################################################
    
if (sys.argv[1] == "-isloved"):
    print('')
    sys.exit()

#########################################################################################################################################
    
if (sys.argv[1] == "-wplaypause"):
    print('')
    sys.exit()

#########################################################################################################################################
    
if (sys.argv[1] == "-wnext"):
    print('')
    sys.exit()

#########################################################################################################################################
    
if (sys.argv[1] == "-wprev"):
    print('')
    sys.exit()
    
#########################################################################################################################################

if (sys.argv[1] == "-playpause"):
    try:
        spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotifyd", "/org/mpris/MediaPlayer2")
        spotifyd_interface = dbus.Interface(spotifyd_bus, "org.mpris.MediaPlayer2.Player")
    except DBusException:
        spotifyd_need_reboot = True

    if not spotifyd_need_reboot:
        try:
            spotifyd_interface.PlayPause()
        except DBusException:
            spotifyd_need_reboot = True        

    if spotifyd_need_reboot:
        print('Request-Failed')
    sys.exit()

#########################################################################################################################################

if (sys.argv[1] == "-next"):
    try:
        spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotifyd", "/org/mpris/MediaPlayer2")
        spotifyd_interface = dbus.Interface(spotifyd_bus, "org.mpris.MediaPlayer2.Player")
    except DBusException:
        spotifyd_need_reboot = True

    if not spotifyd_need_reboot:
        try:
            spotifyd_interface.Next()
        except DBusException:
            spotifyd_need_reboot = True        

    if spotifyd_need_reboot:
        print('Request-Failed')
    sys.exit()

#########################################################################################################################################
    
if (sys.argv[1] == "-prev"):
    try:
        spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotifyd", "/org/mpris/MediaPlayer2")
        spotifyd_interface = dbus.Interface(spotifyd_bus, "org.mpris.MediaPlayer2.Player")
    except DBusException:
        spotifyd_need_reboot = True

    if not spotifyd_need_reboot:
        try:
            spotifyd_interface.Previous()
        except DBusException:
            spotifyd_need_reboot = True        

    if spotifyd_need_reboot:
        print('Request-Failed')
    sys.exit()

#########################################################################################################################################
    
if (sys.argv[1] == "-openuri"):
    if (not len(sys.argv) > 2):
        print('Please provide an uri, example: "spotimaster -openuri spotify:track:2oNibyaUGIHWXtYIkVtxIt"')
        print('')
        sys.exit()
    else:
        uri = sys.argv[2]

    # Often, spotifyd require this many times, i don't know why, plus it does not work with the classic dbus interface where it does work with spotify 
    
    result = subprocess.Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotifyd /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:'" + uri + "'",
             shell=True, stdout=subprocess.PIPE).stdout.read()
    result = subprocess.Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotifyd /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:'" + uri + "'",
             shell=True, stdout=subprocess.PIPE).stdout.read()
    result = subprocess.Popen("dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotifyd /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:'" + uri + "'",
             shell=True, stdout=subprocess.PIPE).stdout.read()
             
    print(result)
    sys.exit()
    
    # Work with spotify but not spotifyd
    #uri="spotify:track:2oNibyaUGIHWXtYIkVtxIt" #test uri...
    #try:
    #    spotifyd_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotifyd", "/org/mpris/MediaPlayer2")
    #    spotifyd_interface = dbus.Interface(spotifyd_bus, "org.mpris.MediaPlayer2.Player")
    #except DBusException:
    #    spotifyd_need_reboot = True

    #if not spotifyd_need_reboot:
    #    try:
    #        spotifyd_interface.OpenUri(uri)
    #    except DBusException:
    #        spotifyd_need_reboot = True        

    #if spotifyd_need_reboot:
    #    print('Command failed')
    #sys.exit()
		
#########################################################################################################################################
