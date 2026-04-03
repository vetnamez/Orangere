import json
import os
from game_logic import Farm

SAVE_FILE = "save.json"

def save_game(farm):
    state = farm.get_state_for_save()
    with open(SAVE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, 'r') as f:
            state = json.load(f)
        farm = Farm()
        farm.load_from_state(state)
        return farm
    except:
        return None
