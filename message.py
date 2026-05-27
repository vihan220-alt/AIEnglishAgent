import json
import os

DATA_FILE = "chat_history.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"Chat 1": []}
    return {"Chat 1": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)
