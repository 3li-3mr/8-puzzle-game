from dataclasses import dataclass, field
from typing import List, Optional
from .node import PuzzleNode


@dataclass
class SearchStep:
    """Represents one expansion event for the GUI timeline playback."""
    step_index: int
    expanded_node: PuzzleNode
    generated_children: List[PuzzleNode]
    iteration: int = 0  # Tracks depth limit iterations in IDDFS


@dataclass
class SearchResult:
    algorithm_name: str
    solvable: bool
    goal_reached: bool
    path_to_goal: List[PuzzleNode] = field(default_factory=list)
    cost_of_path: int = 0
    nodes_expanded: int = 0
    search_depth: int = 0          # Depth of the goal node
    max_search_depth: int = 0      # Maximum depth reached anywhere in the tree
    running_time: float = 0.0      # Execution time in seconds
    root_node: Optional[PuzzleNode] = None
    steps: List[SearchStep] = field(default_factory=list)
    trace_truncated: bool = False  # True if steps exceeded max_trace_steps

    @property
    def actions_to_goal(self) -> List[str]:
        """Returns the sequence of moves ['Up', 'Left', ...] from initial to goal."""
        return [node.action for node in self.path_to_goal if node.action is not None]