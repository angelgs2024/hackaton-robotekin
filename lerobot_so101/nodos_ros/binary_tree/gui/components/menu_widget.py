"""
MenuWidget — Panel de selección de menú (carta del día).
Emite señales Qt cuando el usuario cambia la selección para que el
TableWidget actualice los platos y bebidas sobre la mesa en tiempo real.
"""
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from binary_tree_gui.styles import (
    MENU_CONTAINER_STYLE,
    MENU_CARD_STYLE,
    MENU_CARD_SELECTED_STYLE,
    MENU_ICON_STYLE,
    MENU_NAME_STYLE,
    MENU_NAME_SELECTED_STYLE,
    MENU_CHECK_STYLE,
    MENU_HEADER_STYLE,
    MENU_BADGE_STYLE,
    MENU_SECTION_STYLE,
    MENU_DIVIDER_STYLE,
)


class MenuItemCard(QFrame):
    """Tarjeta individual compacta para un plato o bebida con estética Frutiger Aero."""
    def __init__(self, item_id: str, icon: str, name: str, category: str, on_select_callback, parent=None):
        super().__init__(parent)
        self.setObjectName('MenuItemCard')
        self.item_id = item_id
        self.name = name
        self.category = category
        self.on_select = on_select_callback
        self.is_selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(6)

        # Icono circular compacto
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedSize(24, 24)
        icon_lbl.setStyleSheet(MENU_ICON_STYLE)
        layout.addWidget(icon_lbl)

        # Nombre del ítem
        self.name_lbl = QLabel(name)
        self.name_lbl.setStyleSheet(MENU_NAME_STYLE)
        layout.addWidget(self.name_lbl)
        layout.addStretch()

        # Indicador de selección compacto
        self.check_lbl = QLabel("")
        self.check_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.check_lbl.setFixedSize(16, 16)
        self.check_lbl.setStyleSheet(MENU_CHECK_STYLE)
        layout.addWidget(self.check_lbl)

        self.set_selected(False)

    def set_selected(self, selected: bool):
        self.is_selected = selected
        if selected:
            self.setStyleSheet(MENU_CARD_SELECTED_STYLE)
            self.check_lbl.setText("✓")
            self.name_lbl.setStyleSheet(MENU_NAME_SELECTED_STYLE)
        else:
            self.setStyleSheet(MENU_CARD_STYLE)
            self.check_lbl.setText("")
            self.name_lbl.setStyleSheet(MENU_NAME_STYLE)

    def mousePressEvent(self, event):
        if self.isEnabled() and event.button() == Qt.MouseButton.LeftButton and self.on_select:
            self.on_select(self)
        super().mousePressEvent(event)


class MenuWidget(QWidget):
    """
    Menú sofisticado Frutiger Aero (Glassmorphism) dividido en dos columnas:
    - Columna Izquierda: Elección de Comida (2 platos)
    - Columna Derecha: Elección de Bebida (2 bebidas)

    Emite señales `plato_changed(str)` y `bebida_changed(str)` con el id
    de la opción seleccionada para que otros widgets reaccionen.
    """

    # Señales Qt
    plato_changed = pyqtSignal(str)   # emite el dish_id
    bebida_changed = pyqtSignal(str)  # emite el drink_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = {}
        self.selected_plato = "vacio"
        self.selected_bebida = "vacio"
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Caja de cristal contenedora con estética Frutiger Aero
        menu_box = QFrame()
        menu_box.setObjectName("MenuBox")
        menu_box.setStyleSheet(MENU_CONTAINER_STYLE)

        box_layout = QVBoxLayout(menu_box)
        box_layout.setContentsMargins(10, 8, 10, 10)
        box_layout.setSpacing(6)

        # Encabezado superior
        header_layout = QHBoxLayout()
        title_lbl = QLabel("CARTA DEL DÍA")
        title_lbl.setStyleSheet(MENU_HEADER_STYLE)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        subtitle_badge = QLabel("1 + 1")
        subtitle_badge.setStyleSheet(MENU_BADGE_STYLE)
        header_layout.addWidget(subtitle_badge)
        box_layout.addLayout(header_layout)

        # Separador tenue de cristal
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(MENU_DIVIDER_STYLE)
        box_layout.addWidget(divider)

        # Layout horizontal de 2 columnas: Izquierda (Comida) | Derecha (Bebida)
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(8)

        # ----------------- COLUMNA IZQUIERDA: COMIDA -----------------
        col_comida = QVBoxLayout()
        col_comida.setSpacing(6)
        
        lbl_comida = QLabel("🍽️ COMIDA")
        lbl_comida.setStyleSheet(MENU_SECTION_STYLE)
        col_comida.addWidget(lbl_comida)

        platos = [
            ("vacio", "🍽️", "Plato vacío"),
            ("sopa", "🍲", "Sopa del Día"),
            ("chuleton", "🥩", "Chuletón de vaca"),
        ]
        for item_id, icon, name in platos:
            card = MenuItemCard(item_id, icon, name, "plato", self._on_item_clicked, self)
            self.cards[f"plato_{item_id}" if item_id == "vacio" else item_id] = card
            col_comida.addWidget(card)

        columns_layout.addLayout(col_comida, stretch=1)

        # ----------------- COLUMNA DERECHA: BEBIDA -----------------
        col_bebida = QVBoxLayout()
        col_bebida.setSpacing(6)

        lbl_bebida = QLabel("🥤 BEBIDA")
        lbl_bebida.setStyleSheet(MENU_SECTION_STYLE)
        col_bebida.addWidget(lbl_bebida)

        bebidas = [
            ("vacio", "🥛", "Vaso vacío"),
            ("agua", "🧊", "Agua Mineral"),
            ("cocacola", "🥤", "Coca-Cola"),
        ]
        for item_id, icon, name in bebidas:
            card = MenuItemCard(item_id, icon, name, "bebida", self._on_item_clicked, self)
            self.cards[f"bebida_{item_id}" if item_id == "vacio" else item_id] = card
            col_bebida.addWidget(card)

        columns_layout.addLayout(col_bebida, stretch=1)

        box_layout.addLayout(columns_layout)
        root_layout.addWidget(menu_box)
        root_layout.activate()
        self.setFixedSize(max(410, root_layout.sizeHint().width()), root_layout.sizeHint().height())

        # La mesa comienza sin comida ni bebida servidas.
        self.cards["plato_vacio"].set_selected(True)
        self.cards["bebida_vacio"].set_selected(True)

    def _on_item_clicked(self, clicked_card: MenuItemCard):
        """Maneja la selección exclusiva por categoría (1 comida y 1 bebida)."""
        if not self.isEnabled():
            return
        self._select_card(clicked_card)

    def set_selection(self, comida: str, bebida: str):
        """Refleja el estado de HRI incluso cuando el menú no admite clics."""
        self._select_card(self.cards.get(comida, self.cards['plato_vacio']))
        self._select_card(self.cards.get(bebida, self.cards['bebida_vacio']))

    def _select_card(self, clicked_card: MenuItemCard):
        category = clicked_card.category
        if category == "plato":
            self.selected_plato = clicked_card.item_id
            for card in self.cards.values():
                if card.category == "plato":
                    card.set_selected(card.item_id == clicked_card.item_id)
            # Emitir señal para que la mesa cambie el plato
            self.plato_changed.emit(clicked_card.item_id)
        elif category == "bebida":
            self.selected_bebida = clicked_card.item_id
            for card in self.cards.values():
                if card.category == "bebida":
                    card.set_selected(card.item_id == clicked_card.item_id)
            # Emitir señal para que la mesa cambie la bebida
            self.bebida_changed.emit(clicked_card.item_id)

    def get_selected_order(self) -> dict:
        """Devuelve la orden seleccionada en formato amigable para ROS 2 / tópicos."""
        selected_plato_card = next(
            card for card in self.cards.values()
            if card.category == "plato" and card.item_id == self.selected_plato
        )
        selected_bebida_card = next(
            card for card in self.cards.values()
            if card.category == "bebida" and card.item_id == self.selected_bebida
        )
        return {
            "plato": selected_plato_card.name,
            "bebida": selected_bebida_card.name,
            "plato_id": self.selected_plato,
            "bebida_id": self.selected_bebida,
        }
