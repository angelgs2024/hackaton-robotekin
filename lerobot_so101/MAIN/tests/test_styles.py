import unittest
import os
import sys

# Asegurar que MAIN esté en sys.path para importar src
MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if MAIN_DIR not in sys.path:
    sys.path.insert(0, MAIN_DIR)

from src.gui import styles

class TestStyles(unittest.TestCase):
    def test_background_image_found(self):
        """Verifica que la función localiza una imagen de fondo real existente en el disco."""
        bg_path = styles.get_background_image_path()
        self.assertIsInstance(bg_path, str)
        self.assertTrue(len(bg_path) > 0, "No se encontró ninguna ruta de imagen de fondo")
        self.assertTrue(os.path.exists(bg_path), f"El archivo de imagen {bg_path} no existe en disco")

    def test_main_window_style_generation(self):
        """Comprueba que el estilo de la ventana principal incluye el fondo y el contenedor de cristal."""
        qss = styles.get_main_window_style()
        self.assertIsInstance(qss, str)
        self.assertIn("QMainWindow", qss)
        self.assertIn("#MainContainer", qss)
        self.assertIn("border-image", qss)
        self.assertIn("border-radius", styles.SPEECH_BUBBLE_STYLE)

    def test_all_component_styles_defined(self):
        """Verifica que todos los estilos necesarios para los componentes estén definidos y no vacíos."""
        estilos = [
            ("AVATAR_GLASS_FRAME", styles.AVATAR_GLASS_FRAME),
            ("SPEECH_BUBBLE_STYLE", styles.SPEECH_BUBBLE_STYLE),
            ("STATUS_CARD_STYLE", styles.STATUS_CARD_STYLE),
            ("MENU_CARD_STYLE", styles.MENU_CARD_STYLE),
            ("AERO_BUTTON_STYLE", styles.AERO_BUTTON_STYLE),
            ("CLOSE_BUTTON_STYLE", styles.CLOSE_BUTTON_STYLE),
        ]
        for nombre, valor in estilos:
            self.assertIsInstance(valor, str, f"{nombre} no es un string")
            self.assertTrue(len(valor.strip()) > 0, f"{nombre} está vacío")

if __name__ == '__main__':
    unittest.main()
