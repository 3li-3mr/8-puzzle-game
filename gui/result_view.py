from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QSlider, QComboBox, QTabWidget, QListWidget,
    QListWidgetItem, QFrame, QSplitter
)
from PySide6.QtCore import Qt, Signal, QTimer

from core import PuzzleNode, SearchResult
from .tree_canvas import TreeCanvas


class BoardPreviewWidget(QFrame):
    """Reusable 3x3 board widget for the right-side inspector panel."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._labels: list[QLabel] = []
        grid = QGridLayout(self)
        grid.setSpacing(6)
        grid.setContentsMargins(8, 8, 8, 8)
        for i in range(9):
            lbl = QLabel("-")
            lbl.setFixedSize(48, 48)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("""
                background-color: #0f172a;
                color: #f8fafc;
                font-size: 18px;
                font-weight: bold;
                border-radius: 6px;
                border: 1px solid #334155;
            """)
            self._labels.append(lbl)
            r, c = divmod(i, 3)
            grid.addWidget(lbl, r, c)

    def set_state(self, state: tuple[int, ...]) -> None:
        for lbl, val in zip(self._labels, state):
            if val == 0:
                lbl.setText("")
                lbl.setStyleSheet("""
                    background-color: #1e293b;
                    border: 1px dashed #475569;
                    border-radius: 6px;
                """)
            else:
                lbl.setText(str(val))
                lbl.setStyleSheet("""
                    background-color: #0f172a;
                    color: #38bdf8;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 6px;
                    border: 1px solid #475569;
                """)


class ResultView(QWidget):
    back_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._result: Optional[SearchResult] = None
        self._max_slider_steps: int = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance_step)

        self._build_ui()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        # 1. Top Bar: Back Button + Report Deliverables
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155; color: #f8fafc;
                padding: 8px 14px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #475569; }
        """)
        back_btn.clicked.connect(self._on_back)
        top_bar.addWidget(back_btn)

        self.metrics_label = QLabel()
        self.metrics_label.setStyleSheet(
            "background-color: #1e293b; color: #e2e8f0; padding: 8px 16px; "
            "border-radius: 6px; font-size: 13px; border: 1px solid #334155;"
        )
        top_bar.addWidget(self.metrics_label, 1)
        root_layout.addLayout(top_bar)

        # Optional Truncation Notice Banner
        self.banner_label = QLabel()
        self.banner_label.setStyleSheet(
            "background-color: #451a03; color: #fdba74; padding: 6px 12px; "
            "border-radius: 6px; font-size: 12px;"
        )
        self.banner_label.hide()
        root_layout.addWidget(self.banner_label)

        # 2. Center Splitter: Tree Canvas (Left) + Inspector Tabs (Right)
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Legend + TreeCanvas + Playback Controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Color Legend
        legend_bar = QHBoxLayout()
        for label_txt, color_hex in (
            ("● Frontier", "#60a5fa"),
            ("● Currently Expanding", "#fbbf24"),
            ("● Visited (Explored)", "#94a3b8"),
            ("● Goal Path", "#34d399"),
        ):
            lbl = QLabel(label_txt)
            lbl.setStyleSheet(f"color: {color_hex}; font-weight: bold; font-size: 12px;")
            legend_bar.addWidget(lbl)
        legend_bar.addStretch()
        hint_lbl = QLabel("Scroll to Zoom • Drag to Pan • Click Node to Inspect")
        hint_lbl.setStyleSheet("color: #64748b; font-size: 12px;")
        legend_bar.addWidget(hint_lbl)
        left_layout.addLayout(legend_bar)

        # Canvas
        self.canvas = TreeCanvas()
        self.canvas.node_selected.connect(self._populate_inspector)
        left_layout.addWidget(self.canvas, 1)

        # Playback Control Bar
        ctrl_bar = QHBoxLayout()
        self.btn_play = QPushButton("▶ Play")
        self.btn_prev = QPushButton("⏮ Step -")
        self.btn_next = QPushButton("Step + ⏭")
        self.btn_goal = QPushButton("★ Highlight Goal Path")

        for b in (self.btn_play, self.btn_prev, self.btn_next, self.btn_goal):
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b; color: #f8fafc;
                    border: 1px solid #475569; padding: 6px 12px; border-radius: 6px;
                }
                QPushButton:hover { background-color: #334155; }
            """)
            ctrl_bar.addWidget(b)

        self.btn_play.clicked.connect(self._toggle_play)
        self.btn_prev.clicked.connect(lambda: self.step_slider.setValue(self.step_slider.value() - 1))
        self.btn_next.clicked.connect(lambda: self.step_slider.setValue(self.step_slider.value() + 1))
        self.btn_goal.clicked.connect(self._show_final_goal_path)

        self.step_slider = QSlider(Qt.Horizontal)
        self.step_slider.valueChanged.connect(self._on_slider_changed)
        ctrl_bar.addWidget(self.step_slider, 1)

        self.step_counter_lbl = QLabel("Step: 0 / 0")
        self.step_counter_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px; min-width: 95px;")
        ctrl_bar.addWidget(self.step_counter_lbl)

        self.speed_combo = QComboBox()
        self.speed_combo.addItem("0.5x Slow", 700)
        self.speed_combo.addItem("1x Normal", 350)
        self.speed_combo.addItem("2x Fast", 120)
        self.speed_combo.addItem("5x Turbo", 30)
        self.speed_combo.setCurrentIndex(1)
        self.speed_combo.currentIndexChanged.connect(self._update_timer_speed)
        self.speed_combo.setStyleSheet(
            "background-color: #1e293b; color: #f8fafc; padding: 4px 8px; border-radius: 6px;"
        )
        ctrl_bar.addWidget(self.speed_combo)

        left_layout.addLayout(ctrl_bar)
        splitter.addWidget(left_widget)

        # Right side: Inspector & Goal Path Tabs
        self.right_tabs = QTabWidget()
        self.right_tabs.setFixedWidth(310)
        self.right_tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #0f172a;
                color: #94a3b8;
                padding: 8px 14px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #1e293b;
                color: #38bdf8;
                font-weight: bold;
            }
        """)

        # Tab 1: Clicked Node Inspector
        inspector_tab = QWidget()
        insp_layout = QVBoxLayout(inspector_tab)
        insp_layout.setAlignment(Qt.AlignTop)
        insp_layout.setContentsMargins(16, 16, 16, 16)
        insp_layout.setSpacing(12)

        insp_title = QLabel("Clicked Node State")
        insp_title.setAlignment(Qt.AlignCenter)
        insp_title.setStyleSheet("color: #f8fafc; font-size: 15px; font-weight: bold;")
        insp_layout.addWidget(insp_title)

        board_wrap = QHBoxLayout()
        board_wrap.setAlignment(Qt.AlignCenter)
        self.inspector_board = BoardPreviewWidget()
        board_wrap.addWidget(self.inspector_board)
        insp_layout.addLayout(board_wrap)

        self.inspector_details = QLabel("Click any node in the tree to inspect its metrics.")
        self.inspector_details.setWordWrap(True)
        self.inspector_details.setStyleSheet(
            "color: #cbd5e1; font-size: 13px; line-height: 1.5; background-color: #0f172a; "
            "padding: 12px; border-radius: 6px;"
        )
        insp_layout.addWidget(self.inspector_details)
        self.right_tabs.addTab(inspector_tab, "Node Inspector")

        # Tab 2: Solution Path Trace (Initial -> Goal)
        path_tab = QWidget()
        path_layout = QVBoxLayout(path_tab)
        path_layout.setContentsMargins(12, 12, 12, 12)
        path_layout.setSpacing(8)

        path_board_wrap = QHBoxLayout()
        path_board_wrap.setAlignment(Qt.AlignCenter)
        self.path_preview_board = BoardPreviewWidget()
        path_board_wrap.addWidget(self.path_preview_board)
        path_layout.addLayout(path_board_wrap)

        self.path_list = QListWidget()
        self.path_list.setStyleSheet("""
            QListWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: Consolas;
                font-size: 12px;
            }
            QListWidget::item { padding: 6px; }
            QListWidget::item:selected { background-color: #0284c7; color: white; }
        """)
        self.path_list.currentRowChanged.connect(self._on_path_row_selected)
        path_layout.addWidget(self.path_list, 1)
        self.right_tabs.addTab(path_tab, "Goal Path Trace")

        splitter.addWidget(self.right_tabs)
        splitter.setStretchFactor(0, 1)
        root_layout.addWidget(splitter, 1)

    def display_result(self, result: SearchResult) -> None:
        self._timer.stop()
        self.btn_play.setText("▶ Play")
        self._result = result

        # Populate top deliverables bar
        self.metrics_label.setText(
            f"<b>Algorithm:</b> {result.algorithm_name} &nbsp;|&nbsp; "
            f"<b>Path Cost:</b> {result.cost_of_path} &nbsp;|&nbsp; "
            f"<b>Nodes Expanded:</b> {result.nodes_expanded} &nbsp;|&nbsp; "
            f"<b>Search Depth:</b> {result.search_depth} (Max: {result.max_search_depth}) &nbsp;|&nbsp; "
            f"<b>Running Time:</b> {result.running_time * 1000:.2f} ms"
        )

        # Load tree into canvas
        self._max_slider_steps = self.canvas.load_result(result)
        self.step_slider.blockSignals(True)
        self.step_slider.setRange(0, self._max_slider_steps)
        self.step_slider.setValue(0)
        self.step_slider.blockSignals(False)
        self._update_step_label(0)

        # Show banner if visual steps were capped for UI performance
        if len(result.steps) > self.canvas.MAX_VISUAL_STEPS or result.trace_truncated:
            self.banner_label.setText(
                f"Note: Search expanded {result.nodes_expanded} nodes. Visual tree playback is capped at the "
                f"first {self.canvas.MAX_VISUAL_STEPS} expansions to keep rendering smooth. Click 'Highlight Goal Path' "
                f"to view the complete solution branch."
            )
            self.banner_label.show()
        else:
            self.banner_label.hide()

        # Populate Goal Path Trace list
        self.path_list.clear()
        for idx, node in enumerate(result.path_to_goal):
            move_str = "Initial State" if node.action is None else f"Step {idx}: Move {node.action}"
            item = QListWidgetItem(f"{move_str}  ->  {node.state}")
            self.path_list.addItem(item)
        if result.path_to_goal:
            self.path_list.setCurrentRow(0)

        # Inspect root node initially
        if result.root_node:
            self._populate_inspector(result.root_node, "Frontier")
            self.right_tabs.setCurrentIndex(0)

        # If user disabled step recording, jump straight to final goal path
        if not result.steps and result.goal_reached:
            self._show_final_goal_path()

    def _populate_inspector(self, node: PuzzleNode, status_str: str) -> None:
        self.inspector_board.set_state(node.state)
        action_str = node.action if node.action else "None (Root Node)"
        self.inspector_details.setText(
            f"<b>Node ID:</b> #{node.node_id}<br>"
            f"<b>Status:</b> {status_str}<br>"
            f"<b>Action from Parent:</b> {action_str}<br>"
            f"<b>Depth g(n):</b> {node.depth}<br>"
            f"<b>Heuristic h(n):</b> {node.heuristic:.2f}<br>"
            f"<b>Total Cost f(n):</b> {node.total_cost:.2f}"
        )
        self.right_tabs.setCurrentIndex(0)

    def _on_path_row_selected(self, row: int) -> None:
        if not self._result or row < 0 or row >= len(self._result.path_to_goal):
            return
        node = self._result.path_to_goal[row]
        self.path_preview_board.set_state(node.state)

    def _on_slider_changed(self, value: int) -> None:
        is_at_end = value == self._max_slider_steps and self._max_slider_steps > 0
        self.canvas.render_at_step(value, highlight_goal=is_at_end)
        self._update_step_label(value)
        if is_at_end:
            self._timer.stop()
            self.btn_play.setText("▶ Play")
            self.right_tabs.setCurrentIndex(1)  # Open Goal Path Trace tab automatically!

    def _show_final_goal_path(self) -> None:
        self._timer.stop()
        self.btn_play.setText("▶ Play")
        self.step_slider.blockSignals(True)
        self.step_slider.setValue(self._max_slider_steps)
        self.step_slider.blockSignals(False)
        self.canvas.render_at_step(self._max_slider_steps, highlight_goal=True)
        self._update_step_label(self._max_slider_steps)
        self.right_tabs.setCurrentIndex(1)

    def _toggle_play(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
            self.btn_play.setText("▶ Play")
        else:
            if self.step_slider.value() >= self._max_slider_steps:
                self.step_slider.setValue(0)
            self._update_timer_speed()
            self._timer.start()
            self.btn_play.setText("⏸ Pause")

    def _update_timer_speed(self) -> None:
        interval_ms = self.speed_combo.currentData()
        self._timer.setInterval(interval_ms)

    def _advance_step(self) -> None:
        curr = self.step_slider.value()
        if curr < self._max_slider_steps:
            self.step_slider.setValue(curr + 1)
        else:
            self._timer.stop()
            self.btn_play.setText("▶ Play")

    def _update_step_label(self, val: int) -> None:
        self.step_counter_lbl.setText(f"Step: {val} / {self._max_slider_steps}")

    def _on_back(self) -> None:
        self._timer.stop()
        self.back_requested.emit()