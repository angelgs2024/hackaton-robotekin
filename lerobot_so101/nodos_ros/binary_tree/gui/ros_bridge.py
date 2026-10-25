"""Comunicación HRI/Qt; los callbacks se procesan en el hilo de la ventana."""
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import Empty, String

from binary_tree_hri.menu import COMIDAS, BEBIDAS, opciones
from .main_window import MainWindow


class HriBridge(Node):
    def __init__(self, interface_mode=False):
        super().__init__('interfaz_hri')
        self.interface_mode = self.declare_parameter('interface_mode', interface_mode).value
        self.window = MainWindow(interface_mode=self.interface_mode)
        self.active = False
        self.create_subscription(String, '/manipulacion/estado', self.execution_status, 10)
        self.create_subscription(Empty, '/hri/empezar', self.start_order, 10)
        if self.interface_mode:
            latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
            self.order_publisher = self.create_publisher(String, '/hri/pedido', latched)
            self.speech_publisher = self.create_publisher(String, '/hri/decir', 10)
            self._last_selection = ('vacio', 'vacio')
            self.window.menu_widget.plato_changed.connect(self.interface_selection)
            self.window.menu_widget.bebida_changed.connect(self.interface_selection)
            self.window.order_confirmed.connect(self.confirm_order)
        else:
            self.create_subscription(String, '/hri/seleccion', self.selection, 10)
            self.create_subscription(String, '/hri/pedido', self.confirmed, 10)
            self.create_subscription(String, '/hri/preguntar', self.question, 10)
            self.create_subscription(Empty, '/hri/escuchar', self.listening, 10)
            self.create_subscription(String, '/hri/oido', self.heard, 10)

    def start_order(self, _):
        self.active = False
        self.window.start_order()
        self._last_selection = ('vacio', 'vacio')
        self.active = True

    def interface_selection(self, *_):
        if not self.interface_mode or not self.active:
            return
        menu = self.window.menu_widget
        selection = (menu.selected_plato, menu.selected_bebida)
        if selection == self._last_selection:
            return
        self._last_selection = selection
        comida, bebida = selection
        if comida in COMIDAS and bebida in BEBIDAS:
            text = (f"Entonces, {COMIDAS[comida][0]} y {BEBIDAS[bebida][0]}. "
                    "Si es correcto, pulsa Confirmar Comanda.")
        elif comida in COMIDAS:
            text = f"¿Y para beber? ¿{opciones(BEBIDAS)}?"
        elif bebida in BEBIDAS:
            text = f"¿Y para comer? ¿{opciones(COMIDAS)}?"
        else:
            text = "Elige una comida y una bebida en la pantalla."
        self.window.table_widget.set_speech_text(text)
        self.speech_publisher.publish(String(data=text))

    def selection(self, message):
        parts = message.data.split(',')
        if (self.active and len(parts) == 2
                and parts[0] in ('', *COMIDAS) and parts[1] in ('', *BEBIDAS)):
            self.window.menu_widget.set_selection(*parts)

    def confirm_order(self, comida, bebida):
        if self.interface_mode and self.active and comida in COMIDAS and bebida in BEBIDAS:
            self.active = False
            self.speech_publisher.publish(String(
                data="¡Perfecto! Ahora mismo le preparo la mesa."))
            self.order_publisher.publish(String(data=f'{comida},{bebida}'))

    def confirmed(self, message):
        parts = message.data.split(',')
        if self.active and len(parts) == 2 and parts[0] in COMIDAS and parts[1] in BEBIDAS:
            self.active = False
            self.window.show_confirmed_order(*parts)

    def question(self, message):
        if self.active:
            self.window.table_widget.set_speech_text(message.data)
            self.window.status_widget.set_mic_status(False)

    def listening(self, _):
        if self.active:
            self.window.status_widget.set_mic_status(True)

    def heard(self, _):
        self.window.status_widget.set_mic_status(False)

    def execution_status(self, message):
        self.window.status_widget.lbl_arm.setText(f'🦾 Brazo: {message.data}')
