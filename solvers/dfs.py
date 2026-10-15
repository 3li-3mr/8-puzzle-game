from typing import Optional
from core.state import BoardState, get_neighbors
from core.node import PuzzleNode
from solvers.base_solver import BaseSolver


class DFSSolver(BaseSolver):
    @property
    def name(self) -> str:
        return "DFS"

    def _search(
        self, root_node: PuzzleNode, goal_state: BoardState
    ) -> Optional[PuzzleNode]:
        """
        TODO (Teammate): Implement Depth-First Search (LIFO Stack).

        Implementation Notes:
        1. Use a list as a LIFO stack for the frontier (`frontier.append()`, `frontier.pop()`).
        2. Maintain a Set[BoardState] of reached states (frontier U explored) for O(1) lookups.
        3. Action Ordering Pitfall:
           Because a stack reverses the order of pushed items, if you want the search to
           pop 'Up' first, then 'Down', 'Left', 'Right', iterate over
           `reversed(get_neighbors(current_node.state))` when pushing onto the stack.
        4. When popping `current_node`:
           - First check `if current_node.state == goal_state: return current_node`.
           - Generate valid unreached children using:
             `child = self.create_node(state=next_state, parent=current_node, action=action)`
           - Call `self.record_expansion(current_node, generated_children)` after expanding.
        """
        raise NotImplementedError("DFS algorithm is not implemented yet.")