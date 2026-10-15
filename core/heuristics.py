import math
from enum import Enum
from typing import Callable
from .state import BoardState


class HeuristicType(str, Enum):
    NONE = "None"
    MANHATTAN = "Manhattan"
    EUCLIDEAN = "Euclidean"


HeuristicFn = Callable[[BoardState], float]


def zero_heuristic(state: BoardState) -> float:
    return 0.0


def manhattan_distance(state: BoardState) -> float:
    """
    Sum of |current_x - goal_x| + |current_y - goal_y| for all tiles 1..8.
    The blank space (0) is excluded so the heuristic remains strictly admissible.
    """
    distance = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        curr_row, curr_col = divmod(idx, 3)
        goal_row, goal_col = divmod(tile, 3)
        distance += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return float(distance)


def euclidean_distance(state: BoardState) -> float:
    """
    Sum of sqrt((current_x - goal_x)^2 + (current_y - goal_y)^2) for all tiles 1..8.
    The blank space (0) is excluded.
    """
    distance = 0.0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        curr_row, curr_col = divmod(idx, 3)
        goal_row, goal_col = divmod(tile, 3)
        distance += math.hypot(curr_row - goal_row, curr_col - goal_col)
    return distance


def get_heuristic_fn(heuristic_type: HeuristicType) -> HeuristicFn:
    mapping = {
        HeuristicType.NONE: zero_heuristic,
        HeuristicType.MANHATTAN: manhattan_distance,
        HeuristicType.EUCLIDEAN: euclidean_distance,
    }
    return mapping[heuristic_type]