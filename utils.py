import json

FILE = "data.json"

def load():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {"sessions": {}, "settings": {"auto": False, "delay": 3, "broadcast_msgs": []}, "sudo": []}

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
