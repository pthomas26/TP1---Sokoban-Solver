"""
display.py — ASCII renderer and formatted result printer.

"""


def render_state(state, walls, targets, grid_size):
    """
    Return a printable ASCII string of the current game state.

    Rendering rules:
      wall              → '#'
      empty target      → '.'
      box on target     → '*'
      box off target    → '$'
      player on target  → '+'
      player off target → '@'
      empty floor       → ' '
    """
    player, boxes = state
    rows, cols = grid_size
    grid = [[" " for _ in range(cols)] for _ in range(rows)]

    for r, c in walls:   grid[r][c] = "#"
    for r, c in targets: grid[r][c] = "."
    for r, c in boxes:   grid[r][c] = "*" if (r, c) in targets else "$"
    pr, pc = player
    grid[pr][pc] = "+" if player in targets else "@"

    return "\n".join("".join(row) for row in grid)


def print_result(name, result, walls, targets, grid_size, elapsed,
                 show_path=False):
    """
    Print a formatted summary of a search result.

    If show_path is True and the search succeeded, also prints the
    step-by-step board states from the initial state to the goal.
    """
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
