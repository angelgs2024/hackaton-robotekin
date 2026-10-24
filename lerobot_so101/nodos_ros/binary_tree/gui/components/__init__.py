# Componentes de la interfaz gráfica de Vitoria
from .avatar_widget import TableWidget
from .status_widget import StatusWidget
from .menu_widget import MenuWidget
from .plate_widget import PlateWidget
from .drink_widget import DrinkWidget
from .cutlery_widget import CutleryWidget

# Alias de compatibilidad (el antiguo AvatarWidget ahora es TableWidget)
AvatarWidget = TableWidget

__all__ = [
    "TableWidget",
    "AvatarWidget",
    "StatusWidget",
    "MenuWidget",
    "PlateWidget",
    "DrinkWidget",
    "CutleryWidget",
]
