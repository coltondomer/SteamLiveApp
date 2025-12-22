[app]
# (str) Title of your application
title = Steam Live Tracker

# (str) Package name
package.name = steamtracker

# (str) Package domain
package.domain = org.coltondomer

# (str) Source code where the main.py live
source.dir = .

# (str) Application version (THE FIX FOR YOUR ERROR)
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,chardet,idna,pyjnius

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (int) Log level
log_level = 2
