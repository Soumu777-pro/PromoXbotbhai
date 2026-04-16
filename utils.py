import json
import os

FILE = "data.json"


# ================= LOAD =================
def load():
    if not os.path.exists(FILE):
        return {"sessions": {}, "sudo": [], "settings": {}}

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {"sessions": {}, "sudo": [], "settings": {}}


# ================= SAVE =================
def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
