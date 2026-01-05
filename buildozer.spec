[app]
# --- Basic Info ---
title = Steam Live Dashboard
package.name = steamlive
package.domain = org.gamertools
source.dir = .
source.include_exts = py,png,jpg,json,txt
version = 1.1.0

# --- Requirements ---
# We include certifi and urllib3 explicitly to handle the Steam API SSL handshake on Android
requirements = python3,kivy==2.3.0,requests,certifi,charset-normalizer,idna,urllib3,plyer

# --- Visuals ---
# IMPORTANT: Ensure icon.png exists in your repo or comment this line out with #
icon.filename = icon.png
orientation = portrait

# --- Android Specifics ---
android.permissions = INTERNET, FOREGROUND_SERVICE, POST_NOTIFICATIONS
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_path = 
android.sdk_path = 
android.accept_sdk_license = True
android.skip_update = False
android.archs = arm64-v8a, armeabi-v7a

# --- Styling ---
android.theme = @android:style/Theme.NoTitleBar.Fullscreen
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
