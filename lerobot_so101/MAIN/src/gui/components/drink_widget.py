"""
DrinkWidget — Hueco rectangular para la imagen de la bebida.
Acepta una ruta de imagen vía set_drink() o set_image().
Sin imagen, muestra un borde punteado como placeholder.
"""
import os
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.gui.styles import PLATE_DRINK_LABEL_STYLE

# Catálogo: drink_id → (ruta relativa a images, nombre)
BEBIDAS = {
    "vacio":     ("dishes/empty_glass.png", "Vaso vacío"),
    "agua":     ("dishes/water.png", "Agua Mineral"),
    "refresco": ("dishes/coke.png", "Refresco"),
}

ASSETS_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "..", "assets", "images",
    )
)


class DrinkWidget(QWidget):
    """Vaso / copa que muestra una imagen. Sin imagen → placeholder."""

    WIDTH = 310
    HEIGHT = 410

    def __init__(self, drink_id: str = "vacio", parent=None):
        super().__init__(parent)
        self.setFixedSize(self.WIDTH, self.HEIGHT + 30)
        self._drink_id = drink_id
        self._init_ui()
        self.set_drink(drink_id)

    def _init_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setFixedSize(self.WIDTH, self.HEIGHT)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_placeholder()
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet(PLATE_DRINK_LABEL_STYLE)
        self.name_label.hide()
        layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def _set_placeholder(self):
        self.image_label.clear()
        self.image_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                border-radius: 20px;
            }
        """)

    def _set_pixmap(self, path: str):
        if os.path.exists(path):
            pix = QPixmap(path).scaled(
                self.WIDTH - 10, self.HEIGHT - 10,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(pix)
            self.image_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    border: none;
                    border-radius: 20px;
                }
            """)
        else:
            self._set_placeholder()

    def set_drink(self, drink_id: str):
        """Cambia la bebida por id del catálogo."""
        self._drink_id = drink_id
        filename, name = BEBIDAS.get(drink_id, (None, drink_id))
        self.name_label.setText(name)
        if filename:
            self._set_pixmap(os.path.join(ASSETS_DIR, filename))
        else:
            self._set_placeholder()

    def set_image(self, path: str, name: str = ""):
        """Asigna una imagen arbitraria (ruta absoluta)."""
        self._set_pixmap(path)
        if name:
            self.name_label.setText(name)

    @property
    def drink_id(self) -> str:
        return self._drink_id
