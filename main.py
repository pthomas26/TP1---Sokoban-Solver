"""
main.py — Entry point: load a board and run all four search algorithms.

Run from inside the TP1_Sokoban/ folder:
    python main.py

To change the board, edit BOARD_INDEX in config.py.
"""

import time
import statistics

from config       import BOARD_FILE, BOARD_INDEX, SHOW_PATH
from board_loader import load_boards
from board_parser import parse_board
from search       import bfs, dfs, greedy, a_star
from display      import render_state, print_result
from heuristic import heuristic_manhattan, heuristic_misplaced_boxes

# Loading of the Boards

boards = load_boards(BOARD_FILE)

if BOARD_INDEX >= len(boards):
    print(f"Error: BOARD_INDEX={BOARD_INDEX} but only {len(boards)} boards found.")
    exit(1)

board_name, board_lines = boards[BOARD_INDEX]
player_start, boxes, targets, walls, grid_size = parse_board(board_lines)
initial_state = (player_start, boxes)




print("=" * 52)
print(f"  SOKOBAN SOLVER")
print("=" * 52)
print(f"  Board #{BOARD_INDEX}  —  {board_name}")
print(f"  Grid size      : {grid_size[0]} x {grid_size[1]}")
print(f"  Boxes          : {len(boxes)}")
print(f"  Targets        : {len(targets)}")
print(f"  Walls          : {len(walls)}")
print(f"\n  Initial state:")
for line in render_state(initial_state, walls, targets, grid_size).splitlines():
    print(f"    {line}")



algorithms =[
    ("BFS",
     lambda s: bfs(s, targets, walls, grid_size)),
    ("DFS (max_depth=150)",
     lambda s: dfs(s, targets, walls, grid_size, max_depth=150)),
    ("Greedy + Manhattan",
     lambda s: greedy(s, targets, walls, grid_size, heuristic_manhattan)),
    ("A* + Manhattan",
     lambda s: a_star(s, targets, walls, grid_size, heuristic_manhattan)),
    # --- ADD THE NEW ONES HERE ---
    ("Greedy + Misplaced",
     lambda s: greedy(s, targets, walls, grid_size, heuristic_misplaced_boxes)),
    ("A* + Misplaced",
     lambda s: a_star(s, targets, walls, grid_size, heuristic_misplaced_boxes)),
]

for name, algo in algorithms:
    execution_times = []
    for _ in range(5):
        start_time = time.time()
        result = algo(initial_state)
        execution_times.append(time.time() - start_time)

    mean_time = statistics.mean(execution_times)
    std_dev = statistics.stdev(execution_times)

    show = SHOW_PATH and name == "A* + Manhattan"
    print_result(name, result, walls, targets, grid_size, mean_time,
                show_path=show)
    print(f"Standard Deviation: {std_dev} seconds")