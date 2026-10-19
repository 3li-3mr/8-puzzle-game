from abc import ABC, abstractmethod
import time
from typing import List, Optional
from core.state import BoardState, GOAL_STATE, is_solvable
from core.node import PuzzleNode
from core.result import SearchResult, SearchStep
from core.heuristics import HeuristicType, get_heuristic_fn


class BaseSolver(ABC):
    """
    Abstract base class for all 8-puzzle search algorithms (BFS, DFS, IDDFS, A*).
    Subclasses only need to implement `_search()`.
    """

    def __init__(
        self,
        heuristic_type: HeuristicType = HeuristicType.NONE,
        record_trace: bool = True,
        max_trace_steps: int = 5000,
    ):
        self.heuristic_type = heuristic_type
        self.heuristic_fn = get_heuristic_fn(heuristic_type)
        self.record_trace = record_trace
        self.max_trace_steps = max_trace_steps

        self._node_counter: int = 0
        self._nodes_expanded: int = 0
        self._max_search_depth: int = 0
        self._steps: List[SearchStep] = []
        self._trace_truncated: bool = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the algorithm"""
        pass

    def _reset_metrics(self) -> None:
        self._node_counter = 0
        self._nodes_expanded = 0
        self._max_search_depth = 0
        self._steps = []
        self._trace_truncated = False

    def create_node(
        self,
        state: BoardState,
        parent: Optional[PuzzleNode] = None,
        action: Optional[str] = None,
    ) -> PuzzleNode:
        """Creates a PuzzleNode, assigns a unique ID, updates max_search_depth, and links to parent."""
        depth = 0 if parent is None else parent.depth + 1
        if depth > self._max_search_depth:
            self._max_search_depth = depth

        node = PuzzleNode(
            state=state,
            parent=parent,
            action=action,
            depth=depth,
            heuristic=self.heuristic_fn(state),
            node_id=self._node_counter,
        )
        self._node_counter += 1

        if parent is not None and self.record_trace and not self._trace_truncated:
            parent.children.append(node)

        return node

    def record_expansion(
        self,
        expanded_node: PuzzleNode,
        generated_children: List[PuzzleNode],
        iteration: int = 0,
    ) -> None:
        """Increments nodes_expanded and logs the step for the GUI if trace is enabled."""
        self._nodes_expanded += 1
        if self.record_trace:
            if len(self._steps) < self.max_trace_steps:
                self._steps.append(
                    SearchStep(
                        step_index=len(self._steps),
                        expanded_node=expanded_node,
                        generated_children=generated_children,
                        iteration=iteration,
                    )
                )
            else:
                self._trace_truncated = True

    def solve(self, initial_state: BoardState) -> SearchResult:
        """
        Validates solvability, runs the algorithm timer, and packages the SearchResult.
        """
        self._reset_metrics()

        if not is_solvable(initial_state):
            return SearchResult(
                algorithm_name=self.name,
                solvable=False,
                goal_reached=False,
            )

        root_node = self.create_node(initial_state)

        start_time = time.perf_counter()
        goal_node = self._search(root_node, GOAL_STATE)
        elapsed_time = time.perf_counter() - start_time

        if goal_node is None:
            return SearchResult(
                algorithm_name=self.name,
                solvable=True,
                goal_reached=False,
                nodes_expanded=self._nodes_expanded,
                max_search_depth=self._max_search_depth,
                running_time=elapsed_time,
                root_node=root_node,
                steps=self._steps,
                trace_truncated=self._trace_truncated,
            )

        path = goal_node.reconstruct_path()
        return SearchResult(
            algorithm_name=self.name,
            solvable=True,
            goal_reached=True,
            path_to_goal=path,
            cost_of_path=len(path) - 1,
            nodes_expanded=self._nodes_expanded,
            search_depth=goal_node.depth,
            max_search_depth=self._max_search_depth,
            running_time=elapsed_time,
            root_node=root_node,
            steps=self._steps,
            trace_truncated=self._trace_truncated,
        )

    @abstractmethod
    def _search(
        self, root_node: PuzzleNode, goal_state: BoardState
    ) -> Optional[PuzzleNode]:
        """
        Implemented by subclasses (BFS, DFS, IDDFS, A*).
        Must return the goal PuzzleNode when found, or None.
        """
        pass