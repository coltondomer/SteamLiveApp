[app]
# (str) Title of your application
title = Steam Live Tracker

# (str) Package name
package.name = steamtracker

# (str) Package domain
package.domain = org.coltondomer

# (str) Source code where the main.py live
source.dir = .

# (str) Source files to include (let's make sure we include the json file)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application version
version = 0.1

# (list) Application requirements
# Added openssl for HTTPS and certifi for secure Steam API connections
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,chardet,idna,pyjnius,openssl

# (str) Custom source folders for requirements
# android.permissions: INTERNET is for Steam data, STORAGE is for Favorites/Friends
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API (API 33 is modern and stable)
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version (Required for Python 3.11)
android.ndk = 25b

# (str) Android SDK version
android.sdk = 33

# (bool) Use the private storage for your app (Required for Android 10+)
android.private_storage = True

# (int) Log level (Set to 2 for better debugging if it crashes)
log_level = 2

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (list) Supported orientations
orientation = portrait
