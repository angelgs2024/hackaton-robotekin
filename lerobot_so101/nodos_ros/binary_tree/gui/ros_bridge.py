"""Comunicación HRI/Qt; los callbacks se procesan en el hilo de la ventana."""
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import Empty, String

from binary_tree_hri.menu import COMIDAS, BEBIDAS
from .main_window import MainWindow


class HriBridge(Node):
    def __init__(self, interface_mode=False):
        super().__init__('interfaz_hri')
        self.interface_mode = self.declare_parameter('interface_mode', interface_mode).value
        self.window = MainWindow(interface_mode=self.interface_mode)
        self.active = False
        self.create_subscription(Empty, '/hri/empezar', self.start_order, 10)
        if self.interface_mode:
            latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
            self.order_publisher = self.create_publisher(String, '/hri/pedido', latched)
            self.window.order_confirmed.connect(self.confirm_order)
        else:
            self.create_subscription(String, '/hri/seleccion', self.selection, 10)
            self.create_subscription(String, '/hri/pedido', self.confirmed, 10)
            self.create_subscription(String, '/hri/preguntar', self.question, 10)
            self.create_subscription(Empty, '/hri/escuchar', self.listening, 10)
            self.create_subscription(String, '/hri/oido', self.heard, 10)

    def start_order(self, _):
        self.active = True
        self.window.start_order()

    def selection(self, message):
        parts = message.data.split(',')
        if (self.active and len(parts) == 2
                and parts[0] in ('', *COMIDAS) and parts[1] in ('', *BEBIDAS)):
            self.window.menu_widget.set_selection(*parts)

    def confirm_order(self, comida, bebida):
        if self.interface_mode and self.active and comida in COMIDAS and bebida in BEBIDAS:
            self.active = False
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
