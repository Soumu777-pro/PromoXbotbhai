import json

FILE = "data.json"

def load():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "sessions": {},
            "settings": {
                "auto": False,
                "delay": 3,
                "dp": 0,
                "max": 999,
                "batch": False,
                "broadcast_msgs": []
            },
            "sudo": []
        }

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
