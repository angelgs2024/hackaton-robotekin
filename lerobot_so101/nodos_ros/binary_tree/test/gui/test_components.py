import unittest
import os
import sys

# Habilitar plataforma offscreen si no hay display gráfico para tests desatendidos
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


from PyQt6.QtWidgets import QApplication
from binary_tree_gui.components import AvatarWidget, StatusWidget, MenuWidget, PlateWidget, DrinkWidget

# Garantizar que existe una única instancia de QApplication para la suite de pruebas
app = QApplication.instance()
if app is None:
    app = QApplication(["vitoria_test", "-platform", "offscreen"])

class TestComponents(unittest.TestCase):
    def test_table_widget_initial_state_and_speech(self):
        """Verifica el estado inicial de la mesa y su bocadillo de texto."""
        table = AvatarWidget()

        self.assertEqual(table.plate.dish_id, "vacio")
        self.assertEqual(table.drink.drink_id, "vacio")
        self.assertIn("¡Elige tu comida y bebida!", table.speech_bubble.text())

        nuevo_texto = "Preparando café solo."
        table.set_speech_text(nuevo_texto)
        self.assertIn(nuevo_texto, table.speech_bubble.text())

    def test_status_widget_updates(self):
        """Verifica que el widget de estado actualiza las etiquetas del micro y brazo."""
        status = StatusWidget()

        # Micrófono
        status.set_mic_status(True)
        self.assertIn("ESCUCHANDO", status.lbl_mic.text())
        status.set_mic_status(False)
        self.assertIn("MUTE", status.lbl_mic.text())

        # Brazo robótico SO101
        status.set_arm_status(True, "EJECUTANDO TAREA")
        self.assertIn("EJECUTANDO TAREA", status.lbl_arm.text())
        status.set_arm_status(False)
        self.assertIn("DESCONECTADO", status.lbl_arm.text())

    def test_menu_widget_cards(self):
        """Comprueba que MenuWidget inicializa platos y bebidas, incluidos los vacíos."""
        menu = MenuWidget()
        self.assertEqual(len(menu.cards), 6)
        self.assertIn("sopa", menu.cards)
        self.assertIn("chuleton", menu.cards)
        self.assertIn("plato_vacio", menu.cards)
        self.assertIn("agua", menu.cards)
        self.assertIn("cocacola", menu.cards)
        self.assertIn("bebida_vacio", menu.cards)

        # Probar selección de comanda
        order = menu.get_selected_order()
        self.assertIn("plato", order)
        self.assertIn("bebida", order)
        self.assertEqual(order["plato"], "Plato vacío")
        self.assertEqual(order["bebida"], "Vaso vacío")

    def test_plate_starts_empty_and_changes_with_selection(self):
        """El plato vacío se sustituye al seleccionar cada opción del menú."""
        plate = PlateWidget()
        menu = MenuWidget()
        menu.plato_changed.connect(plate.set_dish)

        self.assertEqual(plate.SIZE, 360)
        self.assertEqual(plate.dish_id, "vacio")
        self.assertIsNotNone(plate.image_label.pixmap())
        self.assertFalse(plate.image_label.pixmap().isNull())

        menu._on_item_clicked(menu.cards["sopa"])
        self.assertEqual(plate.dish_id, "sopa")
        menu._on_item_clicked(menu.cards["chuleton"])
        self.assertEqual(plate.dish_id, "chuleton")

    def test_soup_plate_is_25_pixels_higher(self):
        """La sopa se coloca 25 píxeles por encima de la posición normal."""
        table = AvatarWidget()
        table.resize(1000, 700)
        table.show()
        app.processEvents()

        normal_y = table.plate.y()
        table.set_plato("sopa")
        self.assertEqual(table.plate.y(), normal_y - 25)

        table.set_plato("chuleton")
        self.assertEqual(table.plate.y(), normal_y)

    def test_cutlery_follows_dish(self):
        """Solo muestra cuchara con sopa y tenedor con chuletón."""
        table = AvatarWidget()
        self.assertEqual(table.cutlery._labels["cuchillo"].width(), 240)
        self.assertEqual(table.cutlery._labels["cuchillo"].height(), 160)

        table.set_plato("sopa")
        self.assertFalse(table.cutlery._labels["cuchara"].isHidden())
        self.assertTrue(table.cutlery._labels["cuchillo"].isHidden())
        self.assertTrue(table.cutlery._labels["tenedor"].isHidden())

        table.set_plato("chuleton")
        self.assertTrue(table.cutlery._labels["cuchara"].isHidden())
        self.assertTrue(table.cutlery._labels["cuchillo"].isHidden())
        self.assertFalse(table.cutlery._labels["tenedor"].isHidden())

    def test_drink_catalog_loads_new_assets(self):
        """Comprueba que las bebidas usan las imágenes de la nueva carpeta."""
        drink = DrinkWidget()

        self.assertEqual(drink.WIDTH, 310)
        self.assertEqual(drink.HEIGHT, 410)
        self.assertEqual(drink.drink_id, "vacio")
        self.assertIsNotNone(drink.image_label.pixmap())
        self.assertFalse(drink.image_label.pixmap().isNull())

        drink.set_drink("agua")
        self.assertEqual(drink.drink_id, "agua")
        self.assertFalse(drink.image_label.pixmap().isNull())

        drink.set_drink("cocacola")
        self.assertEqual(drink.drink_id, "cocacola")
        self.assertFalse(drink.image_label.pixmap().isNull())

if __name__ == '__main__':
    unittest.main()
