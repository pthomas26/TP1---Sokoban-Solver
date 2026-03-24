def parse_board(lines):
    """
    Convert a list of grid lines into game elements.

    Pre-processing:
      1. Strip the common leading whitespace so coordinates start at column 0.
      2. Pad all rows to the same width with spaces.

    Character mapping:
      '#'  wall        '.'  target (empty)    ' '  empty floor
      '@'  player      '+'  player on target
      '$'  box         '*'  box on target

    Returns:
        player_start  (row, col)
        boxes         frozenset of (row, col)
        targets       frozenset of (row, col)
        walls         frozenset of (row, col)
        grid_size     (rows, cols)

    Raises:
        ValueError if no player, no boxes, or no targets are found.
    """
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        raise ValueError("Empty board")

    min_indent = min(len(l) - len(l.lstrip(" ")) for l in non_empty)
    lines = [l[min_indent:] for l in lines]

    max_width = max(len(l) for l in lines)
    lines = [l.ljust(max_width) for l in lines]

    grid_size    = (len(lines), max_width)
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

    return (player_start,
            frozenset(boxes),
            frozenset(targets),
            frozenset(walls),
            grid_size)
