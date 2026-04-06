import json
import os

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

BOARD_FILE = os.path.join(BASE_DIR, config["board_file"])
BOARD_INDEX = config["board_index"]
SHOW_PATH = config["show_path"]
MAX_NODES = config["max_nodes"]