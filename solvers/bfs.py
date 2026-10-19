from collections import deque
from typing import Optional, Set, List
from core.state import BoardState, get_neighbors
from core.node import PuzzleNode
from solvers.base_solver import BaseSolver


class BFSSolver(BaseSolver):
    @property
    def name(self) -> str:
        return "BFS"

    def _search(
        self, root_node: PuzzleNode, goal_state: BoardState
    ) -> Optional[PuzzleNode]:
        frontier: deque[PuzzleNode] = deque([root_node])
        reached: Set[BoardState] = {root_node.state}

        while frontier:
            current_node = frontier.popleft()

            if current_node.state == goal_state:
                return current_node

            generated_children: List[PuzzleNode] = []
            for action, next_state in get_neighbors(current_node.state):
                if next_state not in reached:
                    reached.add(next_state)
                    child_node = self.create_node(
                        state=next_state,
                        parent=current_node,
                        action=action,
                    )
                    frontier.append(child_node)
                    generated_children.append(child_node)

            self.record_expansion(current_node, generated_children)

        return None