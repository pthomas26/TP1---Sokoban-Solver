# Sokoban Solver — TP1

## Project Overview

A Python solver for the classic **Sokoban** puzzle game that implements and compares four search algorithms:

| Algorithm | Complete | Optimal | Strategy |
|-----------|----------|---------|----------|
| BFS | Yes | Yes | Explores states level by level (FIFO queue) |
| DFS | Yes* | No | Explores depth-first (LIFO stack), depth-limited to 150 |
| Greedy Best-First | No | No | Prioritises states closest to goal by heuristic only |
| A\* | Yes | Yes | Combines actual cost `g` and heuristic estimate `h` |

*Complete within the depth limit.

---

## Module Structure

```
TP1_Sokoban/
├── config.py          Global constants (board path, index, node limit)
├── board_loader.py    Read board.txt and split it into named boards
├── board_parser.py    Convert raw grid lines into typed game elements
├── grid_utils.py      Movement directions and cell-validity check
├── deadlock.py        Corner-deadlock pruning
├── successors.py      Successor generation and goal test
├── heuristic.py       Manhattan-distance admissible heuristic
├── search.py          BFS, DFS, Greedy, A* algorithms
├── display.py         ASCII renderer and result printer
├── main.py            Entry point
└── steps/             Incremental build history 
```

### Dependency chain

```
config.py
board_loader.py
board_parser.py
grid_utils.py  ──►  deadlock.py  ──►  successors.py
                                            │
config.py ─────────────────────────►  search.py  ◄── heuristic.py
successors.py ─────────────────────►  search.py
display.py  (standalone)
main.py  ◄── all of the above
```

---

## Board Format (`board.txt`)

Boards are stored in a plain text file using standard Sokoban notation.
Several boards can be placed in the same file, separated by blank lines or
a label line (any non-grid line that is not blank becomes the board's name).

```
#   wall              .   target (empty)    (space)  empty floor
@   player            +   player on target
$   box               *   box on target
```

`board_loader.py` detects grid lines with `_is_grid_line()` and groups them
into `(name, lines)` tuples via `load_boards()`.

---

## Board Parsing (`board_parser.py`)

`parse_board(lines)` converts a list of raw grid lines into five elements:

| Variable | Type | Description |
|----------|------|-------------|
| `player_start` | `(row, col)` | Initial player position |
| `boxes` | `frozenset[(row, col)]` | Initial box positions |
| `targets` | `frozenset[(row, col)]` | All target cells |
| `walls` | `frozenset[(row, col)]` | All wall cells |
| `grid_size` | `(rows, cols)` | Bounding box of the board |

Before scanning characters, the parser strips the common leading whitespace
from all rows and pads every row to the same width so that `(row, col)`
coordinates are consistent and zero-based.

All sets are `frozenset` — immutable and hashable — enabling O(1) membership
tests and allowing states to be stored in `set` or used as `dict` keys.

---

## State Representation (`successors.py`)

A **state** is a plain Python tuple:

```python
state = (player_pos, boxes)
# player_pos : (row, col)
# boxes      : frozenset of (row, col)
```

The player's position is part of the state because it determines which
boxes can be reached and pushed. Walls and targets are static and stored
separately — they never change.

---

## Grid Utilities (`grid_utils.py`)

- `DIRECTIONS` — list of `(dr, dc)` offsets for the four cardinal directions.
- `is_valid_cell(pos, walls, grid_size)` — returns `True` if `pos` is inside
  the grid bounds **and** is not a wall. Called thousands of times per second
  during search, so it is kept as minimal as possible.

---

## Deadlock Detection (`deadlock.py`)

`is_corner_deadlock(pos, targets, walls, grid_size)` returns `True` when
placing a box at `pos` creates an irreversible situation:

- The box is **not** on a target, **and**
- It is blocked on at least one **vertical** side (no free cell above or below), **and**
- It is blocked on at least one **horizontal** side (no free cell left or right).

A box in such a corner can never be pushed out, making the board unsolvable.
The check is applied inside `get_successors()` before a pushed state is added
to the frontier, pruning large portions of the search tree cheaply.

---

## Successor Generation (`successors.py`)

`get_successors(state, walls, targets, grid_size)` returns all states
reachable in exactly one player move. For each of the four directions:

1. **Walk** — destination is free: player moves, boxes unchanged.
2. **Push** — destination holds a box: player moves, box slides one step further.
   The push is discarded if the box's new cell is:
   - a wall or out-of-bounds,
   - occupied by another box, or
   - a corner deadlock (pruned immediately).

`is_goal(state, targets)` checks whether `boxes == targets` (all boxes on targets).

---

## Heuristic (`heuristic.py`)

`heuristic_manhattan(state, targets)` computes:

```
h = Σ  min{ Manhattan(box, t)  for t in targets }
   box
```

Each push moves a box exactly one cell, so the Manhattan distance to the
nearest target is a lower bound on the remaining pushes for that box.
Summing over all boxes is optimistic (ignores box interactions), so the
heuristic is **admissible** — A\* remains guaranteed optimal.

---

## Search Algorithms (`search.py`)

All four functions return the same result dictionary:

```python
{
    "success":  bool,   # True if a solution was found
    "cost":     int,    # number of moves (None on failure)
    "expanded": int,    # nodes popped from the frontier
    "frontier": int,    # nodes remaining at termination
    "path":     list,   # state sequence from initial to goal
}
```

| Function | Frontier | Priority |
|----------|----------|----------|
| `bfs` | `deque` (FIFO) | insertion order |
| `dfs` | `list` (LIFO stack) | insertion order, depth-limited |
| `greedy` | `heapq` | `h(state)` |
| `a_star` | `heapq` | `g + h(state)`, with `best_g` dict to skip outdated entries |

A global `MAX_NODES` cap (default 500 000) aborts the search on boards that
are too hard, returning `success=False`.

---

## Display (`display.py`)

- `render_state(state, walls, targets, grid_size)` — builds a printable ASCII
  grid using the same character legend as the board file.
- `print_result(name, result, walls, targets, grid_size, elapsed, show_path)` —
  prints a formatted summary (status, cost, expanded nodes, frontier size,
  elapsed time). If `show_path=True` and the search succeeded, it also prints
  every board state from the initial position to the goal.

---

## Usage

```bash
# Run from inside the TP1_Sokoban/ folder
python main.py
```

To select a different board or toggle the solution path, edit `config.py`:

```python
BOARD_INDEX = 0     # 0-based index of the board in board.txt
SHOW_PATH   = True  # print the step-by-step A* solution
MAX_NODES   = 500_000
```