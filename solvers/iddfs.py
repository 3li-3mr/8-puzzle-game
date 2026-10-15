from typing import Optional
from core.state import BoardState, get_neighbors
from core.node import PuzzleNode
from solvers.base_solver import BaseSolver


class IDDFSSolver(BaseSolver):
    @property
    def name(self) -> str:
        return "Iterative DFS"

    def _search(
        self, root_node: PuzzleNode, goal_state: BoardState
    ) -> Optional[PuzzleNode]:
        """
        TODO (Teammate): Implement Iterative Deepening Depth-First Search (IDDFS).

        Implementation Notes:
        1. Loop `depth_limit` from 0 upwards (e.g., `itertools.count(0)`).
        2. For each `depth_limit`, run a Depth-Limited Search (DLS) starting from `root_node`.
           Note: Before starting a new iteration > 0, clear `root_node.children.clear()` if you
           want the final tree structure to only reflect the successful iteration, OR keep
           passing `iteration=depth_limit` to `self.record_expansion(node, children, iteration=depth_limit)`.
        3. Optimal Revisiting Pitfall in DLS:
           In Depth-Limited DFS, a state might be visited first via a deep, suboptimal branch
           that hits the depth limit, and later reached via a shallower branch.
           Instead of a simple `visited: Set[BoardState]`, track `best_depth: Dict[BoardState, int]`
           within each iteration and allow expanding/visiting `next_state` if it hasn't been
           seen OR if `new_depth < best_depth[next_state]`.
        4. Use `self.create_node(...)` and `self.record_expansion(..., iteration=depth_limit)`
           so the GUI can track nodes and depth limits properly.
        """
        raise NotImplementedError("Iterative DFS algorithm is not implemented yet.")