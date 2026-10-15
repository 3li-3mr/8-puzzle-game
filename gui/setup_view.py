import random
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QCheckBox, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator

from core import (
    BoardState, GOAL_STATE, HeuristicType,
    is_valid_state, is_solvable
)
from solvers import AlgorithmType, SolverFactory


class SetupView(QWidget):
    # Signal emitted when user clicks "Run Search":
    # (initial_state, algorithm_type, heuristic_type, record_trace)
    start_search_requested = Signal(tuple, object, object, bool)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._cells: list[QLineEdit] = []
        self._build_ui()
        # Load the sample state from the lab PDF by default
        self.set_board_state((1, 2, 5, 3, 4, 0, 6, 7, 8))

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # Card container
        card = QFrame()
        card.setFixedWidth(480)
        card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 12px;
                border: 1px solid #334155;
            }
            QLabel { border: none; color: #f8fafc; }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(18)

        # Title
        title = QLabel("8-Puzzle AI Solver")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #38bdf8;")
        card_layout.addWidget(title)

        subtitle = QLabel("Enter initial board state (use 0 for the blank space)")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #94a3b8;")
        card_layout.addWidget(subtitle)

        # 3x3 Grid
        grid_wrapper = QHBoxLayout()
        grid_wrapper.setAlignment(Qt.AlignCenter)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        validator = QIntValidator(0, 8, self)
        for i in range(9):
            cell = QLineEdit()
            cell.setFixedSize(68, 68)
            cell.setMaxLength(1)
            cell.setValidator(validator)
            cell.setAlignment(Qt.AlignCenter)
            cell.setStyleSheet("""
                QLineEdit {
                    background-color: #0f172a;
                    color: #f8fafc;
                    font-size: 24px;
                    font-weight: bold;
                    border: 2px solid #475569;
                    border-radius: 8px;
                }
                QLineEdit:focus {
                    border: 2px solid #38bdf8;
                }
            """)
            cell.textChanged.connect(self._validate_current_board)
            self._cells.append(cell)
            row, col = divmod(i, 3)
            grid_layout.addWidget(cell, row, col)

        grid_wrapper.addLayout(grid_layout)
        card_layout.addLayout(grid_wrapper)

        # Quick Preset & Randomize Buttons
        preset_layout = QHBoxLayout()
        btn_lab_sample = QPushButton("Lab PDF Sample")
        btn_random = QPushButton("Random Solvable")
        btn_hard = QPushButton("Medium Depth (14)")

        for btn in (btn_lab_sample, btn_random, btn_hard):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #334155;
                    color: #e2e8f0;
                    border: none;
                    padding: 6px 10px;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #475569; }
            """)
            preset_layout.addWidget(btn)

        btn_lab_sample.clicked.connect(lambda: self.set_board_state((1, 2, 5, 3, 4, 0, 6, 7, 8)))
        btn_random.clicked.connect(self._generate_random_solvable)
        btn_hard.clicked.connect(lambda: self.set_board_state((2, 5, 3, 1, 0, 6, 4, 7, 8)))
        card_layout.addLayout(preset_layout)

        # Solvability Status Badge
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 13px; font-weight: bold; padding: 6px; border-radius: 6px;")
        card_layout.addWidget(self.status_label)

        # Algorithm Selector
        algo_row = QHBoxLayout()
        algo_lbl = QLabel("Algorithm:")
        algo_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.algo_combo = QComboBox()
        for algo in AlgorithmType:
            self.algo_combo.addItem(algo.value, algo)
        self.algo_combo.setStyleSheet(self._combo_style())
        self.algo_combo.currentIndexChanged.connect(self._on_algo_changed)
        algo_row.addWidget(algo_lbl)
        algo_row.addWidget(self.algo_combo, 1)
        card_layout.addLayout(algo_row)

        # Heuristic Selector (Only active for A*)
        heur_row = QHBoxLayout()
        self.heur_lbl = QLabel("A* Heuristic:")
        self.heur_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.heur_combo = QComboBox()
        self.heur_combo.addItem(HeuristicType.MANHATTAN.value, HeuristicType.MANHATTAN)
        self.heur_combo.addItem(HeuristicType.EUCLIDEAN.value, HeuristicType.EUCLIDEAN)
        self.heur_combo.setStyleSheet(self._combo_style())
        heur_row.addWidget(self.heur_lbl)
        heur_row.addWidget(self.heur_combo, 1)
        card_layout.addLayout(heur_row)

        # Visualization Toggle
        self.trace_checkbox = QCheckBox("Record step-by-step search tree for interactive playback")
        self.trace_checkbox.setChecked(True)
        self.trace_checkbox.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        card_layout.addWidget(self.trace_checkbox)

        # Run Button
        self.run_btn = QPushButton("Solve & Visualize")
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.setFixedHeight(44)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover { background-color: #0369a1; }
            QPushButton:disabled { background-color: #334155; color: #64748b; }
        """)
        self.run_btn.clicked.connect(self._on_run_clicked)
        card_layout.addWidget(self.run_btn)

        main_layout.addWidget(card)
        self._on_algo_changed()

    def _combo_style(self) -> str:
        return """
            QComboBox {
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }
            QComboBox:disabled {
                background-color: #1e293b;
                color: #64748b;
            }
        """

    def _on_algo_changed(self) -> None:
        algo: AlgorithmType = self.algo_combo.currentData()
        is_astar = algo == AlgorithmType.ASTAR
        self.heur_lbl.setEnabled(is_astar)
        self.heur_combo.setEnabled(is_astar)

    def get_board_state(self) -> Optional[BoardState]:
        values = []
        for cell in self._cells:
            txt = cell.text().strip()
            if not txt.isdigit():
                return None
            values.append(int(txt))
        return tuple(values)

    def set_board_state(self, state: BoardState) -> None:
        for cell, val in zip(self._cells, state):
            cell.blockSignals(True)
            cell.setText(str(val))
            cell.blockSignals(False)
        self._validate_current_board()

    def _generate_random_solvable(self) -> None:
        tiles = list(GOAL_STATE)
        while True:
            random.shuffle(tiles)
            candidate = tuple(tiles)
            if is_solvable(candidate) and candidate != GOAL_STATE:
                self.set_board_state(candidate)
                break

    def _validate_current_board(self) -> None:
        # Style blank cell '0' distinctly
        for cell in self._cells:
            if cell.text().strip() == "0":
                cell.setStyleSheet(cell.styleSheet().replace("color: #f8fafc;", "color: #38bdf8;"))
            else:
                cell.setStyleSheet(cell.styleSheet().replace("color: #38bdf8;", "color: #f8fafc;"))

        state = self.get_board_state()
        if state is None or not is_valid_state(state):
            self.status_label.setText("Invalid Board: Must contain digits 0–8 exactly once")
            self.status_label.setStyleSheet(
                "background-color: #450a0a; color: #fca5a5; font-size: 13px; font-weight: bold; padding: 6px; border-radius: 6px;"
            )
            self.run_btn.setEnabled(False)
            return

        if not is_solvable(state):
            self.status_label.setText("Unsolvable Configuration (Odd Inversion Count)")
            self.status_label.setStyleSheet(
                "background-color: #451a03; color: #fdba74; font-size: 13px; font-weight: bold; padding: 6px; border-radius: 6px;"
            )
            self.run_btn.setEnabled(False)
            return

        self.status_label.setText("Valid & Solvable State")
        self.status_label.setStyleSheet(
            "background-color: #064e3b; color: #6ee7b7; font-size: 13px; font-weight: bold; padding: 6px; border-radius: 6px;"
        )
        self.run_btn.setEnabled(True)

    def _on_run_clicked(self) -> None:
        state = self.get_board_state()
        if state is None:
            return
        algo: AlgorithmType = self.algo_combo.currentData()
        heur: HeuristicType = (
            self.heur_combo.currentData() if algo == AlgorithmType.ASTAR else HeuristicType.NONE
        )
        record_trace = self.trace_checkbox.isChecked()
        self.start_search_requested.emit(state, algo, heur, record_trace)