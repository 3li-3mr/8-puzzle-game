import itertools
from typing import Dict, List, Optional
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
        for depth_limit in itertools.count(0):
            # Start each iteration with a clean tree
            root_node.children.clear()
            goal_node = self._depth_limited_search(root_node, goal_state, depth_limit)
            if goal_node is not None:
                return goal_node
        return None

    def _depth_limited_search(
        self, root_node: PuzzleNode, goal_state: BoardState, depth_limit: int
    ) -> Optional[PuzzleNode]:
        frontier: List[PuzzleNode] = [root_node]
        # Shallowest depth at which each state was seen in this iteration
        best_depth: Dict[BoardState, int] = {root_node.state: 0}

        while frontier:
            current_node = frontier.pop()

            # Skip stale copies: a shallower path to this state was found later
            if current_node.depth > best_depth[current_node.state]:
                continue

            if current_node.state == goal_state:
                return current_node

            generated_children: List[PuzzleNode] = []

            # Only expand if we have not reached the depth limit
            if current_node.depth < depth_limit:
                new_depth = current_node.depth + 1
                for action, next_state in reversed(get_neighbors(current_node.state)):
                    if next_state not in best_depth or new_depth < best_depth[next_state]:
                        best_depth[next_state] = new_depth
                        child_node = self.create_node(
                            state=next_state,
                            parent=current_node,
                            action=action,
                        )
                        frontier.append(child_node)
                        generated_children.append(child_node)

                # Restore Up, Down, Left, Right order for the GUI display
                generated_children.reverse()

            self.record_expansion(current_node, generated_children, iteration=depth_limit)

        return None