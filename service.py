# service.py
from time import sleep
import requests

# This runs in the background on your phone
while True:
    try:
        # Pings the API every 60 seconds to keep data fresh
        r = requests.get("https://api.steampowered.com/...")
        # In a real widget, you'd save this to a file the widget can read
        print("Background update successful")
    except:
        pass
    sleep(60)
