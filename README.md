
# Spotimaster v1.5

Control spotifyd with dbus and web-api...
intika - http://github.com/intika

```
Install:   
1. change the python value on the first line to match your version (using python3.6 by default)... 
   this application require python3.x
2. Check the required applications/packages bellow
3. Run 'chmod 755 ./spotimaster.py'
4. Link or copy the application to bin folder with
   'ln -s ./spotimaster.py /usr/bin/spotimaster'

required packages are: dbus-python, requests ('pip3 install dbus-python requests')
required applications: spotifyd/spotify, spotty for web-api functions and dbus-send for openuri 
command

Spotty is available here: https://github.com/michaelherger/spotty, git clone it then use 
'cargo build --release'

Note :
- Change the cache location if required by editing the variable 'cache_location' bellow
- If you want to save spotty parameters directly here, you can edit the variable 'spotty_params' 
  bellow, leave empty if not used. 
```

Features:

```
Available parameters: 

--help           display help page

-love            save the current song to the library, please read the Web-API note bellow
-unlove          delete the current song from the library, please read the Web-API note bellow
-isloved         check if the current song was added to the library, please read the Web-API note bellow

-playpause       pause/play playback over dbus mpris
-next            load next song over dbus mpris
-prev            load previous song over dbus mpris

-wplaypause      pause/play playback over spotify web-api, please read the Web-API note bellow
-wnext           load next song over spotify web-api, please read the Web-API note bellow
-wprev           load previous song over spotify web-api, please read the Web-API note bellow

-openuri         load song/playlist over dbus mpris
                 example: "spotimaster -openuri spotify:track:2oNibyaUGIHWXtYIkVtxIt"
-wopenuri        ...not implemented yet

-check           this parameter can not be combined with others, it is used to
                 check if spotifyd is running correctly, this will check
                 dbus mpris communication and return the text true if
                 everything is ok...

Web-API Note:    parameter that are using the spotify Web-API require spotty to be installed, spotty is used
                 to generate a valid token, that token is cached to /tmp folder and is regenerated when required.
                 Spotty need some parameters for the authentication to succeed; All parameters following the first
                 one will be passed to spotty... this is required! here are two examples:
                 spotimaster -love -n APP-NAME-WHATEVER -c /tmp/spotty -u USERNAME -t -i MY-APP-ID -p MYPASSWORD
                 spotimaster -wnext -n APP-NAME-WHATEVER -c /tmp/spotty -u USERNAME -t -i MY-APP-ID -p MYPASSWORD
```
