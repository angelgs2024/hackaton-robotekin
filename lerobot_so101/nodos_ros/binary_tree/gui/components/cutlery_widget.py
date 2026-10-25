"""
CutleryWidget — cubiertos independientes posicionables sobre la mesa.
"""
import os

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from binary_tree_gui.resources import ASSETS_DIR

CUBIERTOS = (
    ("cuchillo", "knife.png"),
    ("tenedor", "fork.png"),
    ("cuchara", "spoon.png"),
)

ITEM_W = 240
ITEM_H = 160


class CutleryWidget(QWidget):
    """Contenedor transparente con tres imágenes que se mueven por separado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._labels: dict[str, QLabel] = {}
        self._init_ui()

    def _init_ui(self):
        for name, filename in CUBIERTOS:
            label = QLabel(self)
            label.setFixedSize(ITEM_W, ITEM_H)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setToolTip(name.capitalize())

            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                pixmap = QPixmap(path).scaled(
                    ITEM_W - 8,
                    ITEM_H - 8,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                label.setPixmap(pixmap)
            else:
                label.clear()
            label.setStyleSheet("background: transparent; border: none;")

            self._labels[name] = label

    def position_items(self, width: int, height: int, offsets: dict[str, tuple[int, int]]):
        """Posiciona cada cubierto con un offset respecto al centro del contenedor."""
        center_x = width // 2
        center_y = height // 2
        for name, label in self._labels.items():
            offset_x, offset_y = offsets[name]
            label.move(
                center_x + offset_x - label.width() // 2,
                center_y + offset_y - label.height() // 2,
            )

    def set_for_dish(self, dish_id: str):
        """Muestra los cubiertos adecuados para el plato seleccionado."""
        visible_items = {
            "sopa": {"cuchara"},
            "chuleton": {"tenedor"},
        }.get(dish_id, set())
        for name, label in self._labels.items():
            label.setVisible(name in visible_items)

    def set_image(self, cubierto: str, path: str):
        """Asigna una imagen a un cubierto concreto."""
        label = self._labels.get(cubierto)
        if label and os.path.exists(path):
            pixmap = QPixmap(path).scaled(
                ITEM_W - 8,
                ITEM_H - 8,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            label.setPixmap(pixmap)
