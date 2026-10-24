import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QCloseEvent

# Importar estilos Frutiger Aero y componentes
from binary_tree_gui.styles import (
    get_main_window_style,
    get_background_image_path,
    AERO_BUTTON_STYLE,
    CLOSE_BUTTON_STYLE,
)
from binary_tree_gui.components import TableWidget, MenuWidget, StatusWidget
from binary_tree_hri.menu import COMIDAS, BEBIDAS

class MainWindow(QMainWindow):
    order_confirmed = pyqtSignal(str, str)

    def __init__(self, interface_mode=False):
        super().__init__()
        self.interface_mode = interface_mode
        self.order_active = False
        self.init_ui()
        self.menu_widget.plato_changed.connect(self._update_confirmation)
        self.menu_widget.bebida_changed.connect(self._update_confirmation)
        self.menu_widget.setEnabled(False)
        self._update_confirmation()
        self.table_widget.set_speech_text("Preparando el pedido…")

    def start_order(self):
        self.order_active = True
        self.menu_widget.set_selection('', '')
        self.menu_widget.setEnabled(self.interface_mode)
        self._update_confirmation()
        self.table_widget.set_speech_text(
            "Elige una comida y una bebida y pulsa Confirmar Comanda."
            if self.interface_mode else "Escucha al robot y di qué quieres comer y beber."
        )

    def _update_confirmation(self, *_):
        order = self.menu_widget.get_selected_order()
        self.btn_order.setEnabled(
            self.interface_mode and self.order_active
            and order['plato_id'] in COMIDAS and order['bebida_id'] in BEBIDAS
        )
        self.btn_order.setText(
            "✨ Confirmar Comanda" if self.interface_mode else "Confirma diciendo «sí»"
        )

    def show_confirmed_order(self, comida, bebida):
        self.order_active = False
        self.menu_widget.set_selection(comida, bebida)
        self.menu_widget.setEnabled(False)
        self._update_confirmation()
        self.table_widget.set_speech_text(
            f"Pedido confirmado: {COMIDAS[comida][0]} y {BEBIDAS[bebida][0]}."
        )
        self.status_widget.set_mic_status(False)

    def init_ui(self):
        self.setWindowTitle("Robot Camarero - Sistema HRI")
        # Dimensiones estándar para pantalla táctil / tablet
        self.resize(1280, 800)
        self.setMinimumSize(1024, 680)
        
        # Aplicar el estilo Frutiger Aero que renderiza el fondo
        self.setStyleSheet(get_main_window_style())

        # Widget central (contenedor transparente — el fondo es la mesa)
        central_widget = QWidget()
        central_widget.setObjectName("MainContainer")
        self.setCentralWidget(central_widget)

        # Layout vertical principal
        container_layout = QVBoxLayout(central_widget)
        container_layout.setContentsMargins(0, 10, 0, 0)
        container_layout.setSpacing(0)

        # ---------------------------------------------------------
        # BARRA SUPERIOR: Identificador y Botón de Cierre
        # ---------------------------------------------------------
        top_bar_widget = QWidget()
        top_bar_widget.setStyleSheet("background: transparent;")
        top_bar_layout = QVBoxLayout(top_bar_widget)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)

        from PyQt6.QtWidgets import QHBoxLayout
        hbox = QHBoxLayout()
        hbox.addStretch()

        # Botón para cerrar la aplicación
        self.btn_close = QPushButton("✕ Salir")
        self.btn_close.setObjectName("BtnClose")
        self.btn_close.setToolTip("Cerrar aplicación (Tecla Esc)")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(CLOSE_BUTTON_STYLE)
        self.btn_close.clicked.connect(self.close)
        hbox.addWidget(self.btn_close)
        top_bar_layout.addLayout(hbox)

        container_layout.addWidget(top_bar_widget)

        # ---------------------------------------------------------
        # CUERPO PRINCIPAL: Mesa visual (ocupa todo el espacio)
        # ---------------------------------------------------------
        self.table_surface = QWidget()
        self.table_surface.setStyleSheet("background: transparent;")
        surface_layout = QVBoxLayout(self.table_surface)
        surface_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.table_surface, stretch=1)

        self.table_widget = TableWidget(parent=self.table_surface)
        self.table_widget.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        surface_layout.addWidget(self.table_widget)

        # El menú controla los elementos que se muestran sobre la mesa.
        self.menu_widget = MenuWidget(parent=self.table_surface)
        self.menu_widget.plato_changed.connect(self.table_widget.set_plato)
        self.menu_widget.bebida_changed.connect(self.table_widget.set_bebida)

        self.status_widget = StatusWidget()
        container_layout.addWidget(self.status_widget)

        self.btn_order = QPushButton("✨ Confirmar Comanda")
        self.btn_order.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_order.setStyleSheet(AERO_BUTTON_STYLE)
        self.btn_order.clicked.connect(self._confirm_order)
        container_layout.addWidget(self.btn_order, alignment=Qt.AlignmentFlag.AlignCenter)

        # Alias de compatibilidad con la API anterior del avatar.
        self.avatar_widget = self.table_widget
        self.table_widget.raise_()
        self.table_widget.speech_bubble.raise_()
        self.menu_widget.raise_()
        QTimer.singleShot(0, self._position_menu)

    def resizeEvent(self, event):
        """Mantiene la mesa a pantalla completa y la carta como overlay."""
        super().resizeEvent(event)
        self.table_surface.layout().activate()
        QTimer.singleShot(0, self._position_menu)
        self.menu_widget.raise_()
        self.table_widget.speech_bubble.raise_()

    def _position_menu(self):
        self.menu_widget.move(
            self.table_surface.width() - self.menu_widget.width() - 20,
            20,
        )

    def _confirm_order(self):
        if not self.btn_order.isEnabled():
            return
        order = self.menu_widget.get_selected_order()
        comida, bebida = order['plato_id'], order['bebida_id']
        self.show_confirmed_order(comida, bebida)
        self.order_confirmed.emit(comida, bebida)

    def keyPressEvent(self, event: QKeyEvent):
        """Permite cerrar el programa con la tecla ESC o Ctrl+Q."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Q and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent):
        """Realiza un cierre limpio."""
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    import signal
    from PyQt6.QtCore import QTimer

    signal.signal(signal.SIGINT, lambda _signal, _frame: app.quit())
    signal_timer = QTimer(app)
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(100)
    
    # Verificación amigable de la imagen de fondo
    bg_found = get_background_image_path()
    if bg_found:
        print(f"✅ Fondo de restaurante detectado: {bg_found}")
    else:
        print("⚠️ ADVERTENCIA: No se encontró la imagen en 'assets/images/restaurant_bg.png'. Se usará degradado Frutiger Aero de respaldo.")

    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec())
