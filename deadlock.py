"""
deadlock.py — Corner-deadlock detection to prune unsolvable states early.
Member 3
"""

from grid_utils import is_valid_cell


def is_corner_deadlock(pos, targets, walls, grid_size):
    """
    Return True if a box at pos is irreversibly stuck in a corner.

    A corner deadlock occurs when the box is:
      - NOT on a target (boxes already on targets do not need to move), AND
      - blocked on at least one vertical side (no free cell above OR below), AND
      - blocked on at least one horizontal side (no free cell left OR right).

    Such a box can never be pushed to any target and makes the board
    unsolvable — we prune the branch immediately.

    Note: this is a necessary (not sufficient) condition for deadlock.
    It catches the most common cases cheaply and eliminates a large
    fraction of dead-end branches.
    """
    if pos in targets:
        return False

    r, c = pos
    blocked_v = (not is_valid_cell((r - 1, c), walls, grid_size) or
                 not is_valid_cell((r + 1, c), walls, grid_size))
    blocked_h = (not is_valid_cell((r, c - 1), walls, grid_size) or
                 not is_valid_cell((r, c + 1), walls, grid_size))

    return blocked_v and blocked_h
