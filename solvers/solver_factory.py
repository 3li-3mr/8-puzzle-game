from enum import Enum
from core.heuristics import HeuristicType
from solvers.base_solver import BaseSolver


class AlgorithmType(str, Enum):
    BFS = "BFS"
    DFS = "DFS"
    IDDFS = "Iterative DFS"
    ASTAR = "A*"


class SolverFactory:
    @staticmethod
    def create_solver(
        algorithm: AlgorithmType,
        heuristic: HeuristicType = HeuristicType.MANHATTAN,
        record_trace: bool = True,
        max_trace_steps: int = 5000,
    ) -> BaseSolver:
        # Lazy imports so your repo works even while your teammate's files are still stubs
        if algorithm == AlgorithmType.BFS:
            from solvers.bfs import BFSSolver
            return BFSSolver(record_trace=record_trace, max_trace_steps=max_trace_steps)

        elif algorithm == AlgorithmType.DFS:
            from solvers.dfs import DFSSolver
            return DFSSolver(record_trace=record_trace, max_trace_steps=max_trace_steps)

        elif algorithm == AlgorithmType.IDDFS:
            from solvers.iddfs import IDDFSSolver
            return IDDFSSolver(record_trace=record_trace, max_trace_steps=max_trace_steps)

        elif algorithm == AlgorithmType.ASTAR:
            from solvers.astar import AStarSolver
            if heuristic == HeuristicType.NONE:
                heuristic = HeuristicType.MANHATTAN
            return AStarSolver(
                heuristic_type=heuristic,
                record_trace=record_trace,
                max_trace_steps=max_trace_steps,
            )

        raise ValueError(f"Unknown algorithm type: {algorithm}")