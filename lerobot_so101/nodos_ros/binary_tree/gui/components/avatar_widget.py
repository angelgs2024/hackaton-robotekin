"""
TableWidget — Widget de la «mesa» visual.
Posicionamiento ABSOLUTO con centrado DINÁMICO: los widgets se reposicionan
automáticamente en cada resizeEvent usando offsets desde el centro
definidos en gui/params.py.
"""
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt

from binary_tree_gui.components.plate_widget import PlateWidget
from binary_tree_gui.components.drink_widget import DrinkWidget
from binary_tree_gui.components.cutlery_widget import CutleryWidget
from binary_tree_gui.styles import SPEECH_BUBBLE_STYLE
from binary_tree_gui.params import (
    PLATO_OFFSET_X, PLATO_OFFSET_Y, PLATO_SOPA_OFFSET_Y,
    BEBIDA_OFFSET_X, BEBIDA_OFFSET_Y,
    CUCHILLO_OFFSET_X, CUCHILLO_OFFSET_Y,
    TENEDOR_OFFSET_X, TENEDOR_OFFSET_Y,
    CUCHARA_OFFSET_X, CUCHARA_OFFSET_Y,
    BOCADILLO_OFFSET_X, BOCADILLO_OFFSET_Y,
)


class TableWidget(QWidget):
    """
    Contenedor transparente que ocupa toda la ventana.
    Los widgets se colocan con move() y se re-centran en cada resize.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._init_widgets()

    def _init_widgets(self):
        """Crea los widgets hijos (sin layout, posicionamiento absoluto)."""
        self.plate = PlateWidget(dish_id="vacio", parent=self)
        self._plate_offset_y = PLATO_OFFSET_Y
        self.drink = DrinkWidget(drink_id="vacio", parent=self)
        self.cutlery = CutleryWidget(parent=self)
        self.cutlery.set_for_dish("vacio")

        self.speech_bubble = QLabel('"¡Elige tu comida y bebida!"', parent=self)
        self.speech_bubble.setWordWrap(True)
        self.speech_bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speech_bubble.setFixedWidth(440)
        self.speech_bubble.setStyleSheet(SPEECH_BUBBLE_STYLE)
        self.speech_bubble.adjustSize()

    def _center_widget(self, widget: QWidget, offset_x: int, offset_y: int):
        """Posiciona un widget centrado en el contenedor + offset."""
        cx = self.width() // 2
        cy = self.height() // 2
        x = cx + offset_x - widget.width() // 2
        y = cy + offset_y - widget.height() // 2
        widget.move(x, y)

    def resizeEvent(self, event):
        """Re-centra todos los widgets cada vez que cambia el tamaño."""
        super().resizeEvent(event)
        self._center_widget(self.plate,         PLATO_OFFSET_X,     self._plate_offset_y)
        self._center_widget(self.drink,         BEBIDA_OFFSET_X,    BEBIDA_OFFSET_Y)
        self.cutlery.setGeometry(0, 0, self.width(), self.height())
        self.cutlery.position_items(
            self.width(),
            self.height(),
            {
                "cuchillo": (CUCHILLO_OFFSET_X, CUCHILLO_OFFSET_Y),
                "tenedor": (TENEDOR_OFFSET_X, TENEDOR_OFFSET_Y),
                "cuchara": (CUCHARA_OFFSET_X, CUCHARA_OFFSET_Y),
            },
        )
        self._center_widget(self.speech_bubble, BOCADILLO_OFFSET_X, BOCADILLO_OFFSET_Y)

    # --------------------------------------------------------- API pública
    def set_plato(self, dish_id: "str"):
        """Cambia el plato mostrado sobre la mesa."""
        self.plate.set_dish(dish_id)
        self._plate_offset_y = (
            PLATO_SOPA_OFFSET_Y if dish_id == "sopa" else PLATO_OFFSET_Y
        )
        self._center_widget(self.plate, PLATO_OFFSET_X, self._plate_offset_y)
        self.cutlery.set_for_dish(dish_id)

    def set_bebida(self, drink_id: str):
        """Cambia la bebida mostrada sobre la mesa."""
        self.drink.set_drink(drink_id)

    def set_speech_text(self, texto: str):
        """Actualiza el texto del bocadillo de diálogo."""
        self.speech_bubble.setText(f'"{texto}"')
        self.speech_bubble.setFixedHeight(max(
            60, self.speech_bubble.heightForWidth(self.speech_bubble.width())
        ))
        self._center_widget(self.speech_bubble, BOCADILLO_OFFSET_X, BOCADILLO_OFFSET_Y)

    def set_estado(self, estado: str):
        """Stub de compatibilidad."""
        pass
