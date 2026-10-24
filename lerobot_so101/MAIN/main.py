import sys
import os
import signal

# Asegurar que el directorio de MAIN esté en sys.path para importar 'src' directamente
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def install_terminal_interrupt_handler(app: QApplication) -> QTimer:
    """Permite cerrar la GUI con Ctrl+C sin dejar el proceso bloqueado."""
    signal.signal(signal.SIGINT, lambda _signal, _frame: app.quit())

    # El temporizador devuelve periódicamente el control al intérprete de Python
    # para que pueda ejecutar el manejador de señales mientras Qt está activo.
    signal_timer = QTimer(app)
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(100)
    return signal_timer


def main():
    app = QApplication(sys.argv)
    install_terminal_interrupt_handler(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()