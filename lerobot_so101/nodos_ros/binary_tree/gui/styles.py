"""
Estilos QSS con estética Frutiger Aero para la GUI de Vitoria.
Incluye efectos de cristal translúcido (Glassmorphism), degradados aerodinámicos
y soporte adaptativo para la imagen de fondo.
"""
from binary_tree_gui.resources import ASSETS_DIR

ACCENT_COLOR = "#2f6872"
TEXT_COLOR = "#243b4a"
WARM_ACCENT = "#c78336"
PANEL_BACKGROUND = "rgba(255, 255, 255, 225)"
TEXT_TRANSPARENT_STYLE = f"color: {TEXT_COLOR}; background: transparent;"

def get_background_image_path() -> str:
    """Localiza el fondo en los recursos del paquete, sin depender del cwd."""
    for filename in ('restaurant_bg.png', 'restaurante_bg.png',
                     'restaurante_bg.jpg', 'restaurant_bg.jpg'):
        path = ASSETS_DIR / filename
        if path.is_file():
            return path.as_posix()
    return ""

def get_main_window_style() -> str:
    """
    Genera el stylesheet principal de la ventana con la imagen de fondo escalada
    y el contenedor principal con efecto de cristal Frutiger Aero.
    """
    bg_path = get_background_image_path()
    
    bg_rule = ""
    if bg_path:
        # border-image garantiza escalado completo sin repetición ni bordes negros
        bg_rule = f'border-image: url("{bg_path}") 0 0 0 0 stretch stretch;'
    else:
        # Fallback degradado cielo Frutiger Aero si no hay imagen
        bg_rule = "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0a0a0a, stop:1 #050505);"

    return f"""
        QMainWindow {{
            {bg_rule}
        }}
        
        #MainContainer {{
            background: transparent;
            border: none;
        }}
    """

# Estilo transparente para el contenedor del avatar (sin recuadros)
AVATAR_GLASS_FRAME = """
    QFrame {
        background: transparent;
        border: 2px solid #2f6872;
    }
"""

# Bocadillo de diálogo para el texto hablado por Vitoria
SPEECH_BUBBLE_STYLE = """
    QLabel {
        background: rgba(255, 255, 255, 225);
        border: 2px solid #2f6872;
        border-radius: 18px;
        padding: 14px 20px;
        color: #243b4a;
        font-size: 15px;
        font-weight: 500;
    }
"""

PLATE_DRINK_LABEL_STYLE = f"""
    color: {TEXT_COLOR};
    font-size: 13px;
    font-weight: 700;
    background: transparent;
    border: none;
    padding: 3px 10px;
"""

STATUS_TEXT_STYLE = f"color: {TEXT_COLOR};"

MENU_ICON_STYLE = f"""
    QLabel {{
        background: rgba(207, 225, 226, 230);
        border-radius: 12px;
        border: 1px solid {ACCENT_COLOR};
        font-size: 12px;
    }}
"""

MENU_NAME_STYLE = f"""
    color: {TEXT_COLOR};
    font-size: 11px;
    font-weight: 700;
    background: transparent;
"""

MENU_NAME_SELECTED_STYLE = f"""
    color: {TEXT_COLOR};
    font-size: 11px;
    font-weight: 800;
    background: transparent;
"""

MENU_CHECK_STYLE = f"""
    QLabel {{
        color: {TEXT_COLOR};
        font-size: 11px;
        font-weight: 800;
        background: transparent;
    }}
"""

MENU_HEADER_STYLE = f"""
    color: {TEXT_COLOR};
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    background: transparent;
"""

MENU_BADGE_STYLE = f"""
    color: {TEXT_COLOR};
    font-size: 9px;
    font-weight: bold;
    padding: 2px 6px;
    background: rgba(0, 120, 180, 120);
    border: 1px solid {ACCENT_COLOR};
    border-radius: 8px;
"""

MENU_SECTION_STYLE = f"""
    color: {TEXT_COLOR};
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
"""

MENU_DIVIDER_STYLE = f"color: rgba(47, 104, 114, 120); max-height: 1px;"

# Tarjeta de estado de periféricos (micrófono y brazo)
STATUS_CARD_STYLE = """
    QFrame {
        background: rgba(255, 255, 255, 225);
        border: 2px solid #2f6872;
        border-radius: 18px;
        padding: 14px 20px;
        font-weight: bold;
        font-size: 15px;
        color: #243b4a;
    }
"""

# Contenedor sofisticado de cristal translúcido para el Menú (Frutiger Aero)
MENU_CONTAINER_STYLE = """
    #MenuBox {
        background: rgba(255, 255, 255, 225);
        border: 2px solid #2f6872;
        border-radius: 18px;
    }
"""

# Tarjetas individuales de platos/bebidas (estado reposo y hover)
MENU_CARD_STYLE = """
    QFrame#MenuItemCard {
        background: rgba(255, 255, 255, 185);
        border: 1px solid rgba(47, 104, 114, 150);
        border-radius: 10px;
        padding: 3px 8px;
    }
    QFrame#MenuItemCard:hover {
        background: rgba(207, 225, 226, 230);
        border: 1.5px solid #2f6872;
    }
"""

# Tarjeta seleccionada con color cálido y elegante
MENU_CARD_SELECTED_STYLE = """
    QFrame#MenuItemCard {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #e3ad61,
            stop:1 #c78336);
        border: 1.5px solid #9b6125;
        border-radius: 10px;
        padding: 3px 8px;
    }
"""

# Botón interactivo Frutiger Aero (brillante y con reflejo)
AERO_BUTTON_STYLE = """
    QPushButton {
        background: rgba(255, 255, 255, 225);
        border: 2px solid #2f6872;
        border-radius: 18px;
        color: #243b4a;
        font-size: 15px;
        font-weight: bold;
        padding: 14px 20px;
    }
    QPushButton:hover {
        background: #d7e7e6;
        border: 2px solid #2f6872;
    }
    QPushButton:disabled {
        background: rgba(220, 220, 220, 180);
        border-color: #9a9a9a;
        color: #777777;
    }
    QPushButton:pressed {
        background: #c78336;
        color: #ffffff;
    }
"""

# Botón sutil de cierre / salir de la aplicación
CLOSE_BUTTON_STYLE = """
    QPushButton {
        background: rgba(255, 255, 255, 225);
        border: 1px solid #2f6872;
        border-radius: 13px;
        color: #243b4a;
        font-size: 13px;
        font-weight: bold;
        padding: 5px 12px;
    }
    QPushButton:hover {
        background: #d7e7e6;
        border: 1px solid #2f6872;
        color: #243b4a;
    }
    QPushButton:pressed {
        background: #c78336;
        color: #ffffff;
    }
"""
