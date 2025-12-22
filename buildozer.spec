[app]
# (str) Title of your application
title = Steam Live Tracker

# (str) Package name
package.name = steamtracker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.coltondomer

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# Added pyjnius and certifi specifically for Steam API calls
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,chardet,idna,pyjnius

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# REQUIRED for Steam API
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
# r25b is the most stable for Kivy/Python 3.11
android.ndk = 25b

# (bool) Use --private data storage (standard)
android.private_storage = True

# (str) Android NDK directory (leave empty to download automatically)
android.ndk_path = 

# (str) Android SDK directory (leave empty to download automatically)
android.sdk_path = 

# (str) ANT directory (leave empty to download automatically)
android.ant_path = 

# (bool) If True, skip the elegant display of the buildozer logo
buildozer.skip_logo = 1

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

[buildozer]
# (str) Path to build artifacts
bin_dir = ./bin
