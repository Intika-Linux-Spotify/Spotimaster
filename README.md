
# Spotimaster

Control spotifyd/spotify with dbus and web-api...

![Alt text](screens-1.png?raw=true "Features")

![Alt text](screens-2.png?raw=true "Advanced")

# Install:   
```
# 
# 1. Check the required applications/packages bellow
# 2. Run 'chmod 755 ./spotimaster.py'
# 3. Link or copy the application to bin folder with
#    'ln -s ./spotimaster.py /usr/bin/spotimaster'
# 4. Install the required packages...  
# required packages are: dbus-python, requests, urllib3 ('pip3 install dbus-python requests urllib3')
# required applications: spotifyd/spotify, spotty for web-api functions and dbus-send for openuri 
# command spotty is available here: https://github.com/michaelherger/spotty 
# git clone it then use 'cargo build --release'.
#
# To use this app you do need an app-id; you can generate it here 
# https://developer.spotify.com/dashboard/applications/
# app-secret, web authorizations, login and password are not needed.
# you only need the app-id :), note that the app-id need to be yours (belong to the target account) 
# for this to work. 
#
# Disclaimer : using spotty's code to connect to Spotify's API is probably forbidden by them. 
# Use at your own risk.  
#
# Note :
# - Change the cache location if required by editing the variable 'cache_location' bellow
# - If you want to save spotty parameters directly here, you can edit the variable 
#   'spotty_params' bellow, leave empty if not used. 
# - If you want to use this application's dbus function with an other player change 
#   the playername bellow
#
```
