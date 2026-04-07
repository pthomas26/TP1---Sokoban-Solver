"""
board_loader.py — Read board.txt and split it into named board groups.

"""

def _is_grid_line(line):
    """Return True if the line contains at least one Sokoban character."""
    return any(c in line for c in '#$@.+*')


def load_boards(filepath):
    """
    Parse a board file and return a list of (name, lines) tuples.

    Boards are groups of consecutive grid lines separated by blank or
    label lines.  A non-blank separator line becomes the name of the
    following board.
    """
    with open(filepath, encoding="utf-8") as f:
        raw = f.readlines()

    boards = []
    current_name  = "Board"
    current_lines = []

    for raw_line in raw:
        line = raw_line.rstrip("\n")
        if _is_grid_line(line):
            current_lines.append(line)
        else:
            if current_lines:
                boards.append((current_name, current_lines))
                current_lines = []
                current_name  = "Board"
            label = line.strip()
            if label:
                current_name = label

    if current_lines:
        boards.append((current_name, current_lines))

    return boards
