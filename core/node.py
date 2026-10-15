from dataclasses import dataclass, field
from typing import Optional, List
from .state import BoardState


@dataclass
class PuzzleNode:
    state: BoardState
    parent: Optional["PuzzleNode"] = None
    action: Optional[str] = None          # 'Up', 'Down', 'Left', 'Right' (None for root)
    depth: int = 0                        # g(n): cost from root to current node
    heuristic: float = 0.0                # h(n): estimated cost to goal (0.0 for uninformed)
    node_id: int = 0                      # Unique sequential ID for GUI tree mapping & tie-breaking
    children: List["PuzzleNode"] = field(default_factory=list, repr=False)

    @property
    def total_cost(self) -> float:
        """f(n) = g(n) + h(n)"""
        return self.depth + self.heuristic

    def reconstruct_path(self) -> List["PuzzleNode"]:
        """Walks backward via parent pointers to return [root_node, ..., self]."""
        path: List[PuzzleNode] = []
        current: Optional[PuzzleNode] = self
        while current is not None:
            path.append(current)
            current = current.parent
        path.reverse()
        return path

    def __lt__(self, other: "PuzzleNode") -> bool:
        """
        Deterministic tie-breaker for A* priority queue (heapq):
        1. Lowest f(n) = g(n) + h(n)
        2. Lowest h(n) (prefers nodes closer to goal)
        3. Lowest node_id (FIFO creation order)
        """
        if self.total_cost != other.total_cost:
            return self.total_cost < other.total_cost
        if self.heuristic != other.heuristic:
            return self.heuristic < other.heuristic
        return self.node_id < other.node_id

    def __hash__(self) -> int:
        return hash(self.node_id)