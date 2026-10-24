import sys
import signal
import argparse

import rclpy
from rclpy.signals import SignalHandlerOptions
from rclpy.utilities import remove_ros_args

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from binary_tree_gui.ros_bridge import HriBridge


def install_terminal_interrupt_handler(app: QApplication) -> QTimer:
    """Permite cerrar la GUI con Ctrl+C sin dejar el proceso bloqueado."""
    signal.signal(signal.SIGINT, lambda _signal, _frame: app.quit())
    signal.signal(signal.SIGTERM, lambda _signal, _frame: app.quit())

    # El temporizador devuelve periódicamente el control al intérprete de Python
    # para que pueda ejecutar el manejador de señales mientras Qt está activo.
    signal_timer = QTimer(app)
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(100)
    return signal_timer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', action='store_true', help='Seleccionar el pedido con botones')
    args = parser.parse_args(remove_ros_args(sys.argv)[1:])
    app = QApplication([sys.argv[0]])
    install_terminal_interrupt_handler(app)
    # Qt gestiona SIGINT/SIGTERM; no instalar otros manejadores que lo bloqueen.
    rclpy.init(args=sys.argv, signal_handler_options=SignalHandlerOptions.NO)
    bridge = HriBridge(interface_mode=args.interface)
    timer = QTimer(app)

    def spin():
        if rclpy.ok():
            rclpy.spin_once(bridge, timeout_sec=0)
        else:
            app.quit()

    timer.timeout.connect(spin)
    timer.start(20)
    bridge.window.show()
    # Procesa el primer pintado antes de permitir el arranque de HRI y del BT.
    app.processEvents()
    print('BINARY_TREE_GUI_READY', flush=True)
    try:
        result = app.exec()
    finally:
        timer.stop()
        bridge.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    sys.exit(result)

if __name__ == '__main__':
    main()
