
# Spotimaster v3.4

Control spotifyd/spotify with dbus and web-api...

![Alt text](screens-1.png?raw=true "Features")

![Alt text](screens-2.png?raw=true "Advanced")

# Install:   
```
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
# required applications: spotifyd/spotify, spotty for web-api functions and dbus-send for openuri 
# command spotty is available here: https://github.com/michaelherger/spotty 
# git clone it then use 'cargo build --release'.
#
# You do need an app-id to use spotty, you can generate it here 
# https://developer.spotify.com/dashboard/applications/
# app-secret and web authorisations, are not required.
#
# Note :
# - Change the cache location if required by editing the variable 'cache_location' bellow
# - If you want to save spotty parameters directly here, you can edit the variable 
#   'spotty_params' bellow, leave empty if not used. 
# - If you want to use this application's dbus function with an other player change 
#   the playername bellow
#
```
