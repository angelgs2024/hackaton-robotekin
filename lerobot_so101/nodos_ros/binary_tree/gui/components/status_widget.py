from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from binary_tree_gui.styles import STATUS_CARD_STYLE, STATUS_TEXT_STYLE

class StatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Marco contenedor
        frame = QFrame()
        frame.setStyleSheet(STATUS_CARD_STYLE)
        frame_layout = QHBoxLayout(frame)

        self.lbl_mic = QLabel("🎤 Micrófono: INACTIVO")
        self.lbl_mic.setStyleSheet(STATUS_TEXT_STYLE)

        self.lbl_arm = QLabel("🦾 Brazo: DESCONECTADO")
        self.lbl_arm.setStyleSheet(STATUS_TEXT_STYLE)

        frame_layout.addWidget(self.lbl_mic)
        frame_layout.addWidget(self.lbl_arm)

        layout.addWidget(frame)

    def set_mic_status(self, activo: bool):
        if activo:
            self.lbl_mic.setText("🎤 Micrófono: ESCUCHANDO")
            self.lbl_mic.setStyleSheet(STATUS_TEXT_STYLE)
        else:
            self.lbl_mic.setText("🎤 Micrófono: MUTE")
            self.lbl_mic.setStyleSheet(STATUS_TEXT_STYLE)

    def set_arm_status(self, conectado: bool, estado_texto: str = "CONECTADO"):
        if conectado:
            self.lbl_arm.setText(f"🦾 Brazo: {estado_texto}")
            self.lbl_arm.setStyleSheet(STATUS_TEXT_STYLE)
        else:
            self.lbl_arm.setText("🦾 Brazo: DESCONECTADO")
            self.lbl_arm.setStyleSheet(STATUS_TEXT_STYLE)
