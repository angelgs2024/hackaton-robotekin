import os
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from binary_tree_gui.styles import PLATE_DRINK_LABEL_STYLE

# Catálogo: dish_id → (ruta relativa a images, nombre)
PLATOS = {
    "vacio": ("dishes/empty_dish.png", "Plato vacío"),
    "sopa": ("dishes/soup.png", "Sopa del Día"),
    "chuleton": ("dishes/meat.png", "Chuletón de vaca"),
}

from binary_tree_gui.resources import ASSETS_DIR

class PlateWidget(QWidget):
    """Plato circular que muestra una imagen. Sin imagen → placeholder."""

    SIZE = 360  # diámetro del plato en px

    def __init__(self, dish_id: str = "vacio", parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE + 30)
        self._dish_id = dish_id
        self._init_ui()
        self.set_dish(dish_id)

    def _init_ui(self):
        # Permite que el fondo de este widget sea transparente respecto a su contenedor
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setFixedSize(self.SIZE, self.SIZE)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_placeholder()
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet(PLATE_DRINK_LABEL_STYLE)
        self.name_label.hide()
        layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignCenter)


    def _set_placeholder(self):
        """Muestra un borde punteado como placeholder."""
        self.image_label.clear()
        self.image_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
                border-radius: {self.SIZE // 2}px;
            }}
        """)

    def _set_pixmap(self, path: str):
        """Carga y muestra la imagen escalada al círculo."""
        if os.path.exists(path):
            pix = QPixmap(path).scaled(
                self.SIZE - 10, self.SIZE - 10,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(pix)
            self.image_label.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    border: none;
                    border-radius: {self.SIZE // 2}px;
                }}
            """)
        else:
            print(f"⚠️ Imagen no encontrada en: {path}")
            self._set_placeholder()

    def set_dish(self, dish_id: str):
        """Cambia el plato por id del catálogo."""
        self._dish_id = dish_id
        filename, name = PLATOS.get(dish_id, (None, dish_id))
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
    def dish_id(self) -> str:
        return self._dish_id


# ==============================================================================
# Bloque de ejecución para pruebas
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crear un contenedor temporal para visualizar el plato
    ventana_prueba = QWidget()
    ventana_prueba.setWindowTitle("Visor de Plato")
    ventana_prueba.setFixedSize(300, 300)
    # Fondo azul oscuro para contrastar con el texto blanco y el borde transparente
    ventana_prueba.setStyleSheet("background-color: #1e3a5f;") 
    
    layout_prueba = QVBoxLayout(ventana_prueba)
    
    # Instanciar el widget que queremos ver
    plato = PlateWidget()
    layout_prueba.addWidget(plato, alignment=Qt.AlignmentFlag.AlignCenter)
    
    ventana_prueba.show()
    sys.exit(app.exec())
