"""
successors.py — Successor generation and goal test.
Member 3
"""

from grid_utils import DIRECTIONS, is_valid_cell
from deadlock   import is_corner_deadlock


def is_goal(state, targets):
    """Return True when every target cell is covered by a box."""
    _, boxes = state
    return boxes == targets


def get_successors(state, walls, targets, grid_size):
    """
    Return all states reachable from state in exactly one player move.

    For each of the four directions:
      - If the destination cell is free, the player walks there.
      - If the destination cell holds a box, the player pushes it one
        step further — unless the push is illegal:
          (a) the box's new cell is a wall or out-of-bounds,
          (b) the box's new cell is occupied by another box, or
          (c) the box's new cell is a corner deadlock.

    State representation: (player_pos, boxes)
      player_pos  (row, col)
      boxes       frozenset of (row, col)  — immutable & hashable
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
