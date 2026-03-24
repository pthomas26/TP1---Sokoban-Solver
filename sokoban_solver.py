

import heapq
import time
import os
from collections import deque


BOARD_FILE  = os.path.join(os.path.dirname(__file__), "board.txt")
BOARD_INDEX = 0          # 0-based index in the file (0 = first board)
SHOW_PATH   = True       # print step-by-step solution for A*
MAX_NODES   = 500_000    # safety limit to avoid infinite search on hard boards


def _is_grid_line(line):
    """A line belongs to a board if it contains at least one Sokoban character."""
    return any(c in line for c in '#$@.+*')


def load_boards(filepath):
    """
    Parse a board file and return a list of (name, lines) tuples.
    Boards are groups of consecutive grid lines separated by blank/label lines.
    """
    with open(filepath, encoding="utf-8") as f:
        raw = f.readlines()

    boards = []
    current_name = "Board"
    current_lines = []

    for raw_line in raw:
        line = raw_line.rstrip("\n")
        if _is_grid_line(line):
            current_lines.append(line)
        else:
            if current_lines:
                boards.append((current_name, current_lines))
                current_lines = []
                current_name = "Board"
            label = line.strip()
            if label:
                current_name = label

    if current_lines:
        boards.append((current_name, current_lines))

    return boards


def parse_board(lines):
    """
    Convert a list of grid lines into game elements.

    Returns:
        player_start  : (row, col)
        boxes         : frozenset of (row, col)
        targets       : frozenset of (row, col)
        walls         : frozenset of (row, col)
        grid_size     : (rows, cols)
    """
    # Remove common leading whitespace so coordinates start at column 0
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        raise ValueError("Empty board")
    min_indent = min(len(l) - len(l.lstrip(" ")) for l in non_empty)
    lines = [l[min_indent:] for l in lines]

    # Pad all rows to the same width
    max_width = max(len(l) for l in lines)
    lines = [l.ljust(max_width) for l in lines]

    grid_size = (len(lines), max_width)
    player_start = None
    boxes, targets, walls = [], [], []

    for r, row in enumerate(lines):
        for c, ch in enumerate(row):
            if   ch == "#": walls.append((r, c))
            elif ch == ".": targets.append((r, c))
            elif ch == "@": player_start = (r, c)
            elif ch == "+": player_start = (r, c); targets.append((r, c))
            elif ch == "$": boxes.append((r, c))
            elif ch == "*": boxes.append((r, c)); targets.append((r, c))

    if player_start is None:
        raise ValueError("No player (@) found in board")
    if not boxes:
        raise ValueError("No boxes ($) found in board")
    if not targets:
        raise ValueError("No targets (.) found in board")

    return player_start, frozenset(boxes), frozenset(targets), frozenset(walls), grid_size




DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def is_valid_cell(pos, walls, grid_size):
    r, c = pos
    return (0 <= r < grid_size[0] and 0 <= c < grid_size[1]
            and pos not in walls)



def is_corner_deadlock(pos, targets, walls, grid_size):
    """
    A box stuck in a corner (blocked on one vertical side AND one horizontal
    side) that is not on a target can never be pushed to any target.
    """
    if pos in targets:
        return False
    r, c = pos
    blocked_v = (not is_valid_cell((r - 1, c), walls, grid_size) or
                 not is_valid_cell((r + 1, c), walls, grid_size))
    blocked_h = (not is_valid_cell((r, c - 1), walls, grid_size) or
                 not is_valid_cell((r, c + 1), walls, grid_size))
    return blocked_v and blocked_h



def get_successors(state, walls, targets, grid_size):
    """
    Returns all states reachable in one player move (walk or push).
    Branches leading to corner deadlocks are pruned immediately.
    """
    player, boxes = state
    pr, pc = player
    successors = []

    for dr, dc in DIRECTIONS:
        new_player = (pr + dr, pc + dc)

        if not is_valid_cell(new_player, walls, grid_size):
            continue

        new_boxes = set(boxes)

        if new_player in boxes:
            new_box_pos = (new_player[0] + dr, new_player[1] + dc)
            if (not is_valid_cell(new_box_pos, walls, grid_size)
                    or new_box_pos in boxes):
                continue
            if is_corner_deadlock(new_box_pos, targets, walls, grid_size):
                continue
            new_boxes.remove(new_player)
            new_boxes.add(new_box_pos)

        successors.append((new_player, frozenset(new_boxes)))

    return successors


def is_goal(state, targets):
    _, boxes = state
    return boxes == targets


# Heuristic

def _manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def heuristic_manhattan(state, targets):
    """
    Sum of minimum Manhattan distances from each box to its nearest target.
    Admissible: each push moves a box exactly 1 cell, so this never
    overestimates the remaining cost.
    """
    _, boxes = state
    return sum(min(_manhattan(box, t) for t in targets) for box in boxes)


# Search Algorithms

def _make_result(success, cost, expanded, frontier_size, path):
    return {
        "success":   success,
        "cost":      cost,
        "expanded":  expanded,
        "frontier":  frontier_size,
        "path":      path,
    }




def bfs(initial_state, targets, walls, grid_size, max_nodes=MAX_NODES):
    """Breadth-First Search — complete & optimal (uniform cost)."""
    queue = deque([(initial_state, [initial_state])])
    visited = {initial_state}
    expanded = 0

    while queue:
        if expanded >= max_nodes:
            return _make_result(False, None, expanded, len(queue), [])
        state, path = queue.popleft()
        expanded += 1

        if is_goal(state, targets):
            return _make_result(True, len(path) - 1, expanded, len(queue), path)

        for s in get_successors(state, walls, targets, grid_size):
            if s not in visited:
                visited.add(s)
                queue.append((s, path + [s]))

    return _make_result(False, None, expanded, 0, [])




def dfs(initial_state, targets, walls, grid_size,
        max_depth=150, max_nodes=MAX_NODES):
    """Depth-First Search — not optimal; depth limit prevents infinite loops."""
    stack = [(initial_state, [initial_state])]
    visited = set()
    expanded = 0

    while stack:
        if expanded >= max_nodes:
            return _make_result(False, None, expanded, len(stack), [])
        state, path = stack.pop()

        if state in visited:
            continue
        visited.add(state)
        expanded += 1

        if is_goal(state, targets):
            return _make_result(True, len(path) - 1, expanded, len(stack), path)

        if len(path) >= max_depth:
            continue

        for s in get_successors(state, walls, targets, grid_size):
            if s not in visited:
                stack.append((s, path + [s]))

    return _make_result(False, None, expanded, 0, [])




def greedy(initial_state, targets, walls, grid_size,
           heuristic, max_nodes=MAX_NODES):
    """Greedy Best-First Search — fast but not guaranteed optimal."""
    counter = 0
    heap = [(heuristic(initial_state, targets), counter, initial_state,
             [initial_state])]
    visited = set()
    expanded = 0

    while heap:
        if expanded >= max_nodes:
            return _make_result(False, None, expanded, len(heap), [])
        h, _, state, path = heapq.heappop(heap)

        if state in visited:
            continue
        visited.add(state)
        expanded += 1

        if is_goal(state, targets):
            return _make_result(True, len(path) - 1, expanded, len(heap), path)

        for s in get_successors(state, walls, targets, grid_size):
            if s not in visited:
                counter += 1
                heapq.heappush(heap, (heuristic(s, targets), counter, s,
                                      path + [s]))

    return _make_result(False, None, expanded, 0, [])




def a_star(initial_state, targets, walls, grid_size,
           heuristic, max_nodes=MAX_NODES):
    """
    A* Search — complete & optimal with an admissible heuristic.
    heap entry: (f, g, tie_break, state, path)
      f = g + h  total estimated cost
      g          actual cost from initial state
      h          heuristic estimate to goal
    """
    h0 = heuristic(initial_state, targets)
    counter = 0
    heap = [(h0, 0, counter, initial_state, [initial_state])]
    best_g = {}
    expanded = 0

    while heap:
        if expanded >= max_nodes:
            return _make_result(False, None, expanded, len(heap), [])
        f, g, _, state, path = heapq.heappop(heap)

        if state in best_g and best_g[state] <= g:
            continue
        best_g[state] = g
        expanded += 1

        if is_goal(state, targets):
            return _make_result(True, g, expanded, len(heap), path)

        for s in get_successors(state, walls, targets, grid_size):
            g_new = g + 1
            if s in best_g and best_g[s] <= g_new:
                continue
            h_new = heuristic(s, targets)
            counter += 1
            heapq.heappush(heap, (g_new + h_new, g_new, counter, s,
                                  path + [s]))

    return _make_result(False, None, expanded, 0, [])


# Display

def render_state(state, walls, targets, grid_size):
    """Returns a printable string of the current grid."""
    player, boxes = state
    rows, cols = grid_size
    grid = [[" " for _ in range(cols)] for _ in range(rows)]

    for r, c in walls:    grid[r][c] = "#"
    for r, c in targets:  grid[r][c] = "."
    for r, c in boxes:    grid[r][c] = "*" if (r, c) in targets else "$"
    pr, pc = player
    grid[pr][pc] = "+" if player in targets else "@"

    return "\n".join("".join(row) for row in grid)


def print_result(name, result, walls, targets, grid_size, elapsed,
                 show_path=False):
    sep = "=" * 52
    print(f"\n{sep}")
    print(f"  {name}")
    print(sep)
    if result["success"]:
        print(f"  Result         : SUCCESS")
        print(f"  Solution cost  : {result['cost']} moves")
    else:
        print(f"  Result         : FAILURE (node limit or no solution)")
    print(f"  Nodes expanded : {result['expanded']}")
    print(f"  Frontier size  : {result['frontier']}")
    print(f"  Time           : {elapsed:.4f} s")

    if result["success"] and show_path:
        print(f"\n  Solution path ({len(result['path'])} states):")
        for i, state in enumerate(result["path"]):
            print(f"\n  Step {i}:")
            for line in render_state(state, walls, targets, grid_size).splitlines():
                print(f"    {line}")








if __name__ == "__main__":
    
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
    print(f"  Node limit     : {MAX_NODES:,}")
    print(f"\n  Initial state:")
    for line in render_state(initial_state, walls, targets, grid_size).splitlines():
        print(f"    {line}")

    
    algorithms = [
        ("BFS",
         lambda s: bfs(s, targets, walls, grid_size)),
        ("DFS (max_depth=150)",
         lambda s: dfs(s, targets, walls, grid_size, max_depth=150)),
        ("Greedy + Manhattan",
         lambda s: greedy(s, targets, walls, grid_size, heuristic_manhattan)),
        ("A* + Manhattan",
         lambda s: a_star(s, targets, walls, grid_size, heuristic_manhattan)),
    ]

    for name, algo in algorithms:
        t0 = time.time()
        result = algo(initial_state)
        elapsed = time.time() - t0
        show = SHOW_PATH and name == "A* + Manhattan"
        print_result(name, result, walls, targets, grid_size, elapsed,
                     show_path=show)
