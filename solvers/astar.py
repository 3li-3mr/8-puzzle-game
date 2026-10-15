import heapq
from typing import Optional
from core.state import BoardState, get_neighbors
from core.node import PuzzleNode
from solvers.base_solver import BaseSolver


class AStarSolver(BaseSolver):
    @property
    def name(self) -> str:
        return f"A* ({self.heuristic_type.value})"

    def _search(
        self, root_node: PuzzleNode, goal_state: BoardState
    ) -> Optional[PuzzleNode]:
        """
        TODO (Teammate): Implement A* Search using a Priority Queue (`heapq`).

        Implementation Notes:
        1. `PuzzleNode` already computes `node.heuristic` automatically inside `self.create_node(...)`
           and already implements `__lt__` comparing `f(n) = g(n) + h(n)`.
           You can push/pop `PuzzleNode` directly with `heapq.heappush(frontier, node)` and
           `heapq.heappop(frontier)`.
        2. Maintain an `explored: Set[BoardState]` (or `best_g: Dict[BoardState, int]`) to
           avoid re-expanding states with higher or equal path cost `g(n)`.
        3. When popping `current_node`:
           - If `current_node.state` was already expanded with a lower cost, `continue`.
           - Check `if current_node.state == goal_state: return current_node`.
           - Generate children via `self.create_node(state=next_state, parent=current_node, action=action)`.
           - Call `self.record_expansion(current_node, generated_children)`.
        """
        raise NotImplementedError("A* algorithm is not implemented yet.")