from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QApplication
from PySide6.QtCore import Qt

from core import BoardState, HeuristicType
from solvers import AlgorithmType, SolverFactory
from .setup_view import SetupView
from .result_view import ResultView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-Puzzle AI Search Visualizer — Alexandria University CSE")
        self.resize(1200, 780)
        self.setStyleSheet("QMainWindow { background-color: #0f172a; }")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.setup_view = SetupView()
        self.result_view = ResultView()

        self.stack.addWidget(self.setup_view)
        self.stack.addWidget(self.result_view)

        self.setup_view.start_search_requested.connect(self._run_search)
        self.result_view.back_requested.connect(lambda: self.stack.setCurrentWidget(self.setup_view))

    def _run_search(
        self,
        initial_state: BoardState,
        algorithm: AlgorithmType,
        heuristic: HeuristicType,
        record_trace: bool,
    ) -> None:
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            solver = SolverFactory.create_solver(
                algorithm=algorithm,
                heuristic=heuristic,
                record_trace=record_trace,
            )
            result = solver.solve(initial_state)
        except NotImplementedError as exc:
            QApplication.restoreOverrideCursor()
            QMessageBox.information(
                self,
                "Algorithm Pending",
                f"{exc}\n\n(Your teammate can implement this solver in the solvers/ folder.)",
            )
            return
        except Exception as exc:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Search Error", f"An unexpected error occurred:\n{exc}")
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.result_view.display_result(result)
        self.stack.setCurrentWidget(self.result_view)