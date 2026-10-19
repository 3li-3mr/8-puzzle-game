from enum import Enum
from typing import Dict, Set, List, Optional, Tuple
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsObject, QStyleOptionGraphicsItem, QWidget
)
from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QWheelEvent

from core import PuzzleNode, SearchResult


class NodeVisualStatus(Enum):
    FRONTIER = "Frontier"
    EXPANDING = "Currently Expanding"
    VISITED = "Visited (Explored)"
    GOAL_PATH = "On Goal Path"


STATUS_COLORS: Dict[NodeVisualStatus, Tuple[QColor, QColor]] = {
    NodeVisualStatus.FRONTIER: (QColor("#1e3a8a"), QColor("#60a5fa")),
    NodeVisualStatus.EXPANDING: (QColor("#78350f"), QColor("#fbbf24")),
    NodeVisualStatus.VISITED: (QColor("#334155"), QColor("#94a3b8")),
    NodeVisualStatus.GOAL_PATH: (QColor("#065f46"), QColor("#34d399")),
}


class VisualTreeNode(QGraphicsObject):
    """Clickable node item on the QGraphicsScene."""
    node_clicked = Signal(object, str)

    WIDTH = 66
    HEIGHT = 66

    def __init__(self, puzzle_node: PuzzleNode, status: NodeVisualStatus, is_selected: bool = False):
        super().__init__()
        self.puzzle_node = puzzle_node
        self.status = status
        self.is_selected = is_selected
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setCursor(Qt.PointingHandCursor)
        self.setZValue(2)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.WIDTH / 2, -self.HEIGHT / 2, self.WIDTH, self.HEIGHT)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        fill_color, border_color = STATUS_COLORS[self.status]

        pen_width = 3.5 if self.is_selected else 2.0
        pen_color = QColor("#f8fafc") if self.is_selected else border_color

        painter.setPen(QPen(pen_color, pen_width))
        painter.setBrush(QBrush(fill_color))
        rect = self.boundingRect()
        painter.drawRoundedRect(rect, 8, 8)

        painter.setPen(QColor("#f8fafc"))
        font = QFont("Consolas", 8, QFont.Bold)
        painter.setFont(font)

        state = self.puzzle_node.state
        row_1 = f"{state[0]} {state[1]} {state[2]}"
        row_2 = f"{state[3]} {state[4]} {state[5]}"
        row_3 = f"{state[6]} {state[7]} {state[8]}"
        board_text = f"{row_1}\n{row_2}\n{row_3}".replace("0", "·")

        painter.drawText(rect, Qt.AlignCenter, board_text)

    def mousePressEvent(self, event) -> None:
        self.node_clicked.emit(self.puzzle_node, self.status.value)
        super().mousePressEvent(event)


class TreeCanvas(QGraphicsView):
    """
    Renders the search tree up to a chosen playback step index.
    Supports mouse-drag panning and wheel zooming.
    """
    node_selected = Signal(object, str)

    MAX_VISUAL_STEPS = 400
    H_SPACING = 90
    V_SPACING = 110

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setStyleSheet("background-color: #0f172a; border: 1px solid #334155; border-radius: 8px;")

        self._result: Optional[SearchResult] = None
        self._selected_node_id: Optional[int] = None
        self._current_step: int = 0
        self._highlight_goal: bool = False

    def load_result(self, result: SearchResult) -> int:
        """
        Loads a SearchResult and returns the maximum slider step index available
        for visual playback.
        """
        self._result = result
        self._selected_node_id = result.root_node.node_id if result.root_node else None
        self._highlight_goal = False
        max_steps = min(len(result.steps), self.MAX_VISUAL_STEPS)
        self.render_at_step(0, highlight_goal=False)
        self.resetTransform()
        return max_steps

    def wheelEvent(self, event: QWheelEvent) -> None:
        zoom_factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(zoom_factor, zoom_factor)

    def render_at_step(self, step_k: int, highlight_goal: bool = False) -> None:
        """
        Reconstructs and draws the visible search tree at step `step_k` (0 .. max_steps).
        """
        self._current_step = step_k
        self._highlight_goal = highlight_goal
        self._scene.clear()

        if not self._result or not self._result.root_node:
            return

        root = self._result.root_node
        steps = self._result.steps[: min(step_k, self.MAX_VISUAL_STEPS)]

        active_iteration = steps[-1].iteration if steps else 0

        visible_children: Dict[int, List[PuzzleNode]] = {root.node_id: []}
        node_map: Dict[int, PuzzleNode] = {root.node_id: root}
        expanded_ids: Set[int] = set()
        expanding_id: Optional[int] = None

        for idx, step in enumerate(steps):
            if step.iteration != active_iteration:
                continue
            exp_node = step.expanded_node
            node_map[exp_node.node_id] = exp_node
            expanded_ids.add(exp_node.node_id)
            if idx == len(steps) - 1:
                expanding_id = exp_node.node_id

            visible_children.setdefault(exp_node.node_id, [])
            for child in step.generated_children:
                node_map[child.node_id] = child
                visible_children[exp_node.node_id].append(child)
                visible_children.setdefault(child.node_id, [])

        goal_path_ids: Set[int] = set()
        if highlight_goal and self._result.goal_reached:
            for p_node in self._result.path_to_goal:
                goal_path_ids.add(p_node.node_id)
                node_map[p_node.node_id] = p_node
                visible_children.setdefault(p_node.node_id, [])
                if p_node.parent is not None:
                    parent_list = visible_children.setdefault(p_node.parent.node_id, [])
                    if all(c.node_id != p_node.node_id for c in parent_list):
                        parent_list.append(p_node)

        positions: Dict[int, QPointF] = {}
        subtree_widths: Dict[int, float] = {}

        def compute_width(n_id: int) -> float:
            children = visible_children.get(n_id, [])
            if not children:
                subtree_widths[n_id] = self.H_SPACING
                return self.H_SPACING
            total_w = sum(compute_width(c.node_id) for c in children)
            subtree_widths[n_id] = max(self.H_SPACING, total_w)
            return subtree_widths[n_id]

        def assign_coords(n_id: int, x_center: float, depth: int) -> None:
            positions[n_id] = QPointF(x_center, depth * self.V_SPACING)
            children = visible_children.get(n_id, [])
            if not children:
                return
            total_w = sum(subtree_widths[c.node_id] for c in children)
            curr_x = x_center - total_w / 2.0
            for child in children:
                c_w = subtree_widths[child.node_id]
                assign_coords(child.node_id, curr_x + c_w / 2.0, depth + 1)
                curr_x += c_w

        compute_width(root.node_id)
        assign_coords(root.node_id, 0.0, 0)

        for parent_id, children in visible_children.items():
            if parent_id not in positions:
                continue
            p_pos = positions[parent_id]
            for child in children:
                if child.node_id not in positions:
                    continue
                c_pos = positions[child.node_id]
                is_goal_edge = (
                    highlight_goal
                    and parent_id in goal_path_ids
                    and child.node_id in goal_path_ids
                )
                edge_color = QColor("#10b981") if is_goal_edge else QColor("#475569")
                edge_width = 3.0 if is_goal_edge else 1.5

                line = self._scene.addLine(
                    p_pos.x(), p_pos.y(), c_pos.x(), c_pos.y(),
                    QPen(edge_color, edge_width)
                )
                line.setZValue(1)

                if child.action:
                    mid_x = (p_pos.x() + c_pos.x()) / 2.0
                    mid_y = (p_pos.y() + c_pos.y()) / 2.0
                    lbl = self._scene.addText(child.action[0], QFont("Segoe UI", 8, QFont.Bold))
                    lbl.setDefaultTextColor(QColor("#34d399") if is_goal_edge else QColor("#94a3b8"))
                    lbl.setPos(mid_x - 8, mid_y - 10)
                    lbl.setZValue(3)

        for n_id, pos in positions.items():
            p_node = node_map[n_id]
            if highlight_goal and n_id in goal_path_ids:
                status = NodeVisualStatus.GOAL_PATH
            elif n_id == expanding_id and not highlight_goal:
                status = NodeVisualStatus.EXPANDING
            elif n_id in expanded_ids:
                status = NodeVisualStatus.VISITED
            else:
                status = NodeVisualStatus.FRONTIER

            is_sel = n_id == self._selected_node_id
            item = VisualTreeNode(p_node, status, is_selected=is_sel)
            item.setPos(pos)
            item.node_clicked.connect(self._on_item_clicked)
            self._scene.addItem(item)

        rect = self._scene.itemsBoundingRect()
        self._scene.setSceneRect(rect.adjusted(-150, -100, 150, 150))

    def _on_item_clicked(self, puzzle_node: PuzzleNode, status_str: str) -> None:
        self._selected_node_id = puzzle_node.node_id
        self.render_at_step(self._current_step, self._highlight_goal)
        self.node_selected.emit(puzzle_node, status_str)