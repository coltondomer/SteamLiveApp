[app]
# (str) Title of your application
title = Steam Live Dashboard

# (str) Package name
package.name = steamlive

# (str) Package domain (needed for android packaging)
package.domain = org.gamertools

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,json

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# IMPORTANT: These must match the libraries used in the code
requirements = python3,kivy==2.3.0,requests,urllib3,certifi,plyer

# (str) Custom source file for application icon
# Make sure your image is named icon.png in the same folder!
icon.filename = icon.png

# (str) Supported orientations
orientation = portrait

# (list) Permissions
# Needed for Steam API and Sale Notifications
android.permissions = INTERNET, FOREGROUND_SERVICE, VIBRATE, POST_NOTIFICATIONS

# (int) Android API to use
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (list) The Android themes to apply
android.theme = @android:style/Theme.NoTitleBar.Fullscreen

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
