"""
search.py — BFS, DFS, Greedy Best-First and A* search algorithms.
Member 4
"""

import heapq
from collections import deque

from config     import MAX_NODES
from successors import get_successors, is_goal


# =============================================================================
# RESULT DICTIONARY
# =============================================================================

def _make_result(success, cost, expanded, frontier_size, path):
    """
    Standardised result returned by every search function.

    Fields:
        success   bool — True if a solution was found
        cost      int  — solution length in moves (None on failure)
        expanded  int  — nodes popped from the frontier
        frontier  int  — nodes remaining in the frontier at termination
        path      list — state sequence from initial to goal ([] on failure)
    """
    return {
        "success":  success,
        "cost":     cost,
        "expanded": expanded,
        "frontier": frontier_size,
        "path":     path,
    }


# =============================================================================
# BFS
# =============================================================================

def bfs(initial_state, targets, walls, grid_size, max_nodes=MAX_NODES):
    """
    Breadth-First Search.

    Uses a FIFO queue.  States are marked visited on insertion to avoid
    duplicate entries in the queue.

    Properties: complete, optimal (minimum number of moves).
    """
    queue    = deque([(initial_state, [initial_state])])
    visited  = {initial_state}
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


# =============================================================================
# DFS
# =============================================================================

def dfs(initial_state, targets, walls, grid_size,
        max_depth=150, max_nodes=MAX_NODES):
    """
    Depth-First Search with a depth limit.

    Uses an explicit stack.  The depth limit prevents infinite loops in
    cyclic state spaces and keeps memory usage manageable.

    Properties: complete within max_depth, NOT optimal.
    """
    stack    = [(initial_state, [initial_state])]
    visited  = set()
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


# =============================================================================
# GREEDY BEST-FIRST
# =============================================================================

def greedy(initial_state, targets, walls, grid_size,
           heuristic, max_nodes=MAX_NODES):
    """
    Greedy Best-First Search.

    Priority = h(state) only (heuristic estimate to goal).
    Fast in practice but not guaranteed to find the optimal solution.

    Properties: NOT complete (may loop), NOT optimal.
    """
    counter = 0
    heap    = [(heuristic(initial_state, targets), counter,
                initial_state, [initial_state])]
    visited  = set()
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
                heapq.heappush(heap,
                               (heuristic(s, targets), counter, s, path + [s]))

    return _make_result(False, None, expanded, 0, [])


# =============================================================================
# A*
# =============================================================================

def a_star(initial_state, targets, walls, grid_size,
           heuristic, max_nodes=MAX_NODES):
    """
    A* Search.

    Priority = f(state) = g(state) + h(state)
      g  actual cost from the initial state (number of moves)
      h  heuristic estimate to the goal

    With an admissible heuristic, A* is both complete and optimal.
    A tie-breaking counter ensures a consistent heap ordering when f values
    are equal.

    Properties: complete, optimal (with admissible heuristic).
    """
    h0      = heuristic(initial_state, targets)
    counter = 0
    heap    = [(h0, 0, counter, initial_state, [initial_state])]
    best_g  = {}
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
            h_new   = heuristic(s, targets)
            counter += 1
            heapq.heappush(heap,
                           (g_new + h_new, g_new, counter, s, path + [s]))

    return _make_result(False, None, expanded, 0, [])
