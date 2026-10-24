import unittest
import os
import sys

# Habilitar plataforma offscreen para pruebas
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from binary_tree_gui.main_window import MainWindow

app = QApplication.instance()
if app is None:
    app = QApplication(["vitoria_test", "-platform", "offscreen"])

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow(interface_mode=True)
        self.window.start_order()

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
        """Solo permite confirmar una comida y una bebida reales una vez."""
        orders = []
        self.window.order_confirmed.connect(lambda *order: orders.append(order))
        self.assertFalse(self.window.btn_order.isEnabled())
        self.window.btn_order.click()
        self.assertEqual(orders, [])
        self.window.menu_widget._on_item_clicked(self.window.menu_widget.cards['chuleton'])
        self.assertFalse(self.window.btn_order.isEnabled())
        self.window.menu_widget._on_item_clicked(self.window.menu_widget.cards['agua'])
        self.assertTrue(self.window.btn_order.isEnabled())
        self.window.btn_order.click()
        self.window.btn_order.click()
        self.assertEqual(orders, [('chuleton', 'agua')])
        self.assertIn("Pedido confirmado", self.window.avatar_widget.speech_bubble.text())
        self.assertFalse(self.window.menu_widget.isEnabled())

    def test_empty_option_disables_confirmation(self):
        self.window.menu_widget.set_selection('sopa', 'cocacola')
        self.assertTrue(self.window.btn_order.isEnabled())
        self.window.menu_widget._on_item_clicked(self.window.menu_widget.cards['bebida_vacio'])
        self.assertFalse(self.window.btn_order.isEnabled())

    def test_menu_names_fit_and_question_is_not_clipped(self):
        self.window.show()
        app.processEvents()
        for card in self.window.menu_widget.cards.values():
            label = card.name_lbl
            self.assertGreaterEqual(label.width(), label.fontMetrics().horizontalAdvance(card.name))
        bubble = self.window.table_widget.speech_bubble
        self.assertGreaterEqual(bubble.height(), bubble.heightForWidth(bubble.width()))

    def test_voice_selection_updates_cards_and_images_without_enabling_clicks(self):
        window = MainWindow(interface_mode=False)
        try:
            window.start_order()
            window.menu_widget.set_selection('chuleton', 'agua')
            self.assertTrue(window.menu_widget.cards['chuleton'].is_selected)
            self.assertTrue(window.menu_widget.cards['agua'].is_selected)
            self.assertEqual(window.table_widget.plate.dish_id, 'chuleton')
            self.assertEqual(window.table_widget.drink.drink_id, 'agua')
            self.assertFalse(window.table_widget.plate.image_label.pixmap().isNull())
            self.assertFalse(window.btn_order.isEnabled())
            window.menu_widget._on_item_clicked(window.menu_widget.cards['sopa'])
            self.assertEqual(window.table_widget.plate.dish_id, 'chuleton')
        finally:
            window.close()

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
