[app]
title = Steam Live
package.name = steamlive
package.domain = org.colton
source.dir = .
source.include_exts = py,png,jpg,json,txt
version = 1.1.0

# Critical: Added certifi and charset-normalizer for network stability
requirements = python3,kivy==2.3.0,requests,certifi,charset-normalizer,idna,urllib3,plyer

orientation = portrait
android.permissions = INTERNET, POST_NOTIFICATIONS, FOREGROUND_SERVICE

# --- STABLE COMPILER SETTINGS ---
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Build only for modern phones to save time
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
