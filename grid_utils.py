# (delta_row, delta_col) for Up, Down, Left, Right
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def is_valid_cell(pos, walls, grid_size):
    """
    Return True if pos is inside the grid AND is not a wall.

    Called thousands of times per second during search — kept minimal.
    """
    r, c = pos
    return (0 <= r < grid_size[0]
            and 0 <= c < grid_size[1]
            and pos not in walls)
