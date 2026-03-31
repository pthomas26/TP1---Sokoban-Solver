"""
heuristic.py — Admissible heuristic for informed search (Greedy, A*).
Member 4
"""


def _manhattan(p1, p2):
    """Manhattan distance between two (row, col) positions."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def heuristic_manhattan(state, targets):
    """
    Sum of minimum Manhattan distances from each box to its nearest target.

    Admissibility:
      Each push moves a box exactly one cell, so the Manhattan distance from
      a box to its nearest target is a lower bound on the pushes required for
      that box alone.  Summing over all boxes is optimistic (assumes boxes do
      not interfere), so the heuristic never overestimates — A* remains optimal.
    """
    _, boxes = state
    return sum(min(_manhattan(box, t) for t in targets) for box in boxes)

def heuristic_misplaced_boxes(state, targets):
    # Explanation for TA: Every box not on a target needs at least 1 push.
    _, boxes = state
    return len(boxes - targets)
