[app]
title = Steam Live Tracker
package.name = steamtracker
package.domain = org.yourname
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# These are the libraries your app needs to run
requirements = python3,kivy,requests,urllib3,certifi,chardet,idna

orientation = portrait
fullscreen = 1
android.permissions = INTERNET, FOREGROUND_SERVICE

# This line links your service.py to the Android system
services = SteamMonitor:service.py

# Android SDK/NDK settings for GitHub Actions
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
