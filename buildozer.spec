[app]
# (str) Title of your application
title = Steam Live Dashboard

# (str) Package name
package.name = steamlive

# (str) Package domain (needed for android packaging)
package.domain = org.gamertools

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,json,txt

# (str) Application versioning
version = 1.1.0

# (list) Application requirements
# Added certifi and charset-normalizer to prevent SSL network errors
requirements = python3,kivy==2.3.0,requests,certifi,charset-normalizer,idna,urllib3,plyer

# (str) Custom source file for application icon
icon.filename = icon.png

# (str) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET, FOREGROUND_SERVICE, POST_NOTIFICATIONS

# --- STABILITY SETTINGS ---
# (int) Android API to use
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use (SPECIFIC VERSION PREVENTS TIMEOUTS)
android.ndk = 25b

# (bool) Use the shared hide-sensitive-information feature
android.skip_update = False

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) indicates if the application should be allowed to exit when the user presses the back button
android.allow_backup = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
