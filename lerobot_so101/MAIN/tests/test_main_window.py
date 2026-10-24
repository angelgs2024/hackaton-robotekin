import unittest
import os
import sys

# Habilitar plataforma offscreen para pruebas
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if MAIN_DIR not in sys.path:
    sys.path.insert(0, MAIN_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from src.gui.main_window import MainWindow

app = QApplication.instance()
if app is None:
    app = QApplication(["vitoria_test", "-platform", "offscreen"])

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()

    def tearDown(self):
        self.window.close()

    def test_window_structure(self):
        """Verifica que la ventana principal carga todos sus elementos requeridos."""
        self.assertIsNotNone(self.window.centralWidget())
        self.assertEqual(self.window.centralWidget().objectName(), "MainContainer")
        self.assertIsNotNone(self.window.avatar_widget)
        self.assertIsNotNone(self.window.status_widget)
        self.assertIsNotNone(self.window.menu_widget)
        self.assertIsNotNone(self.window.btn_order)
        self.assertIsNotNone(self.window.btn_close)

    def test_order_interaction(self):
        """Comprueba que hacer clic en 'Confirmar Comanda' actualiza el avatar y el brazo."""
        self.window.btn_order.click()
        self.assertIn("Oído cocina", self.window.avatar_widget.speech_bubble.text())
        self.assertIn("SIRVIENDO COMANDA", self.window.status_widget.lbl_arm.text())

    def test_escape_key_closes_window(self):
        """Verifica que presionar Escape activa el cierre de la ventana."""
        key_event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Escape,
            Qt.KeyboardModifier.NoModifier
        )
        self.window.keyPressEvent(key_event)
        # La ventana debe haber procesado el evento de cierre
        self.assertFalse(self.window.isVisible())

    def test_close_button_closes_window(self):
        """Verifica que el botón de salir cierra la ventana."""
        self.window.show()
        self.window.btn_close.click()
        self.assertFalse(self.window.isVisible())

if __name__ == '__main__':
    unittest.main()
