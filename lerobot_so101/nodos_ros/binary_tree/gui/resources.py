"""Rutas de imágenes para el árbol de fuentes y el paquete ROS instalado."""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory


def get_images_directory() -> Path:
    # En desarrollo y con --symlink-install, __file__ apunta a las fuentes.
    source_images = Path(__file__).resolve().parent.parent / 'assets' / 'images'
    if source_images.is_dir():
        return source_images
    # Una instalación normal lleva las imágenes a share/binary_tree/assets.
    return Path(get_package_share_directory('binary_tree')) / 'assets' / 'images'


ASSETS_DIR = get_images_directory()
