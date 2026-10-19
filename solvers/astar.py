import heapq
from typing import Optional, Set, List, Dict
from core.state import BoardState, get_neighbors
from core.node import PuzzleNode
from solvers.base_solver import BaseSolver


class AStarSolver(BaseSolver):
    @property
    def name(self) -> str:
        return f"A* ({self.heuristic_type})"

    def _search(
        self, root_node: PuzzleNode, goal_state: BoardState
    ) -> Optional[PuzzleNode]:
        frontier: List[PuzzleNode] = [root_node]
        explored: Set[BoardState] = set()
        best_g: Dict[BoardState, int] = {root_node.state: 0}

        while frontier:
            current_node = heapq.heappop(frontier)

            if current_node.state in explored:
                continue

            if current_node.state == goal_state:
                return current_node

            explored.add(current_node.state)
            generated_children: List[PuzzleNode] = []
            new_g = current_node.depth + 1

            for action, next_state in get_neighbors(current_node.state):
                if next_state not in explored and (
                    next_state not in best_g or new_g < best_g[next_state]
                ):
                    best_g[next_state] = new_g
                    child_node = self.create_node(
                        state=next_state,
                        parent=current_node,
                        action=action,
                    )
                    heapq.heappush(frontier, child_node)
                    generated_children.append(child_node)

            self.record_expansion(current_node, generated_children)

        return None