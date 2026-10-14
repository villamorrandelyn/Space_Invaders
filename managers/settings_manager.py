import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    default_settings = {
        "sound_volume": 80,
        "music_enabled": True,
        "mobile_controls": False,
    }

    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings

    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return default_settings

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as file:
            json.dump(settings, file, indent=4)
    except IOError as e:
        print(f"Error sa pag-save: {e}")