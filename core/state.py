from typing import Tuple, List

BoardState = Tuple[int, ...]
GOAL_STATE: BoardState = (0, 1, 2, 3, 4, 5, 6, 7, 8)

# Standard action order from the ColumbiaX CSMM.101x specification
ACTION_ORDER: Tuple[str, ...] = ("Up", "Down", "Left", "Right")


def is_valid_state(state: BoardState) -> bool:
    """Checks if the state contains exactly the numbers 0 through 8."""
    return len(state) == 9 and set(state) == set(GOAL_STATE)


def is_solvable(state: BoardState) -> bool:
    """
    Determines if an 8-puzzle state can reach the goal (0, 1, 2, 3, 4, 5, 6, 7, 8).
    Because the goal state has 0 inversions, and legal moves on a 3x3 grid preserve
    inversion parity, a state is solvable iff its number of inversions is even.
    """
    if not is_valid_state(state):
        return False

    tiles = [tile for tile in state if tile != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1

    return inversions % 2 == 0


def get_neighbors(state: BoardState) -> List[Tuple[str, BoardState]]:
    """
    Generates all valid (action, next_state) pairs by moving the blank space (0)
    in the order: Up, Down, Left, Right.
    """
    zero_idx = state.index(0)
    row, col = divmod(zero_idx, 3)

    # Deltas for moving the blank space (0)
    moves = (
        ("Up", -1, 0),
        ("Down", 1, 0),
        ("Left", 0, -1),
        ("Right", 0, 1),
    )

    neighbors: List[Tuple[str, BoardState]] = []
    for action, d_row, d_col in moves:
        new_row, new_col = row + d_row, col + d_col
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            target_idx = new_row * 3 + new_col
            state_list = list(state)
            # Swap blank (0) with the adjacent tile
            state_list[zero_idx], state_list[target_idx] = (
                state_list[target_idx],
                state_list[zero_idx],
            )
            neighbors.append((action, tuple(state_list)))

    return neighbors


def format_board(state: BoardState) -> str:
    """Returns a printable 3x3 string representation of the board."""
    lines = []
    for r in range(3):
        row_str = " ".join(str(state[r * 3 + c]) for c in range(3))
        lines.append(row_str)
    return "\n".join(lines)