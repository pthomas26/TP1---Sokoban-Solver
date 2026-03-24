"""
config.py — Global configuration constants.
Member 1
"""

import os

BOARD_FILE  = os.path.join(os.path.dirname(__file__), "..", "board.txt")
BOARD_INDEX = 0          # 0-based index of the board to solve
SHOW_PATH   = True       # print step-by-step A* solution
MAX_NODES   = 500_000    # safety cap to abort on very hard boards
