# Resumen del Proyecto: Vitoria - Sistema HRI SO101 (Robot Camarero)

**Objetivo:** Desarrollar un sistema de Interacción Persona-Robot (HRI) para un brazo robótico SO101 que actúe como un robot camarero capaz de tomar comandas (plato y bebida) y servirlas. El sistema cuenta con una interfaz gráfica (GUI) estilo "Frutiger Aero" protagonizada por un avatar animado 2D llamado "Vitoria", procesamiento de voz en local (STT/TTS), y control del hardware robótico, todo integrado mediante **ROS 2**.

---

### Arquitectura del Sistema (ROS 2)
El proyecto está estructurado modularmente bajo la carpeta `MAIN/` con integración hacia nodos ROS 2 (`ament_python` / `lerobot_so101`):

1.  **`gui_node.py` / `main_window.py`**: Interfaz de usuario en PyQt6 (estilo Frutiger Aero Glassmorphism).
2.  **`audio_node.py`**: Procesamiento de voz local usando `faster-whisper` (STT) y `piper-tts` (TTS).
3.  **`arm_node.py`**: Control cinemático del brazo SO101 (vía `so101-nexus`) y simulación en MuJoCo.
4.  **`ps4_node.py`**: Control opcional del robot mediante un mando de PS4 (`controlar_ps4.py`).

### Tópicos Principales
*   `/avatar_state` (String): Controla el GIF/estado del avatar (idle, listening, processing, speaking).
*   `/comanda` (String): Transmite la orden final (ej. `{"plato": "sopa", "bebida": "agua"}`) al brazo robótico.
*   `/arm_status` (String): Feedback del estado físico del brazo hacia la GUI.
*   `/tts_say` (String): Texto que el nodo de audio debe vocalizar.

---

### Interfaz Gráfica (GUI - PyQt6)
La GUI se desarrolla de forma modular en `MAIN/src/gui/`. La estética elegida es **Frutiger Aero** (transparencias, brillos, efectos de cristal aqua/celeste, fondo fotorrealista).

*   **Layout:** Pantalla dividida (50/50) sobre un panel flotante de cristal (`#MainContainer`).
    *   **Panel Izquierdo (Hero):** Avatar en gran formato (`AvatarWidget`) centrado en la mitad izquierda utilizando `waiter_no_bg.png` como prueba visual completa de las animaciones, con el globo de diálogo (`speech_bubble`) superpuesto por delante (Fondo -> Avatar -> Globo).
    *   **Panel Derecho (Operaciones - Superior Derecho):** 
        *   Menú sofisticado y compacto (`MenuWidget`): Estética Frutiger Aero (Glassmorphism) en 2 columnas (Comida a la izquierda, Bebida a la derecha) con selector interactivo de cristal.
        *   Indicador de estado de hardware (`StatusWidget`: micrófono y brazo robótico).
        *   Botón táctil de confirmación de comanda (`AERO_BUTTON_STYLE`).

---

### Estado Actual del Desarrollo
1.  **Entorno Base:** Configurado con `Pixi` en Linux. Dependencias: `PyQt6`, `faster-whisper`, `piper-tts`, `sounddevice`, dependencias de ROS 2, `so101-nexus` y `mujoco`.
2.  **Módulo de Estilos y Fondo (Completado):**
    *   `MAIN/src/gui/styles.py`: Creado con soporte de rutas dinámicas mediante `get_background_image_path()`, detectando `restaurant_bg.png` en `MAIN/assets/images/` sin depender del directorio de trabajo actual.
    *   Regla QSS con `border-image` en `QMainWindow` para garantizar un escalado panorámico perfecto del fondo del restaurante sin repeticiones ni deformaciones.
    *   Definidos tokens de diseño Frutiger Aero: `AVATAR_GLASS_FRAME`, `SPEECH_BUBBLE_STYLE`, `STATUS_CARD_STYLE`, `MENU_CARD_STYLE` y `AERO_BUTTON_STYLE`.
    *   `MAIN/src/styles.py`: Configurado como re-exportador para asegurar compatibilidad retroactiva.
3.  **Componentes y Ventana Principal (Completado):**
    *   Corregido el archivo de paquete `__init__.py` en `MAIN/src/gui/components/`.
    *   Integrados `AvatarWidget`, `StatusWidget` y `MenuWidget` en `MainWindow` (`MAIN/src/gui/main_window.py`).
    *   `AvatarWidget` preparado con máquina de estados (`idle`, `listen`, `think`, `habla`), soporte dinámico de GIFs y fallback con emojis visuales (`🤖`, `👂`, `🧠`, `💬`) en caso de no disponer aún de los archivos GIF.
4.  **Mecanismo de Cierre de la Aplicación (Completado):**
    *   Botón superior derecho `✕ Salir` con estilo `CLOSE_BUTTON_STYLE`.
    *   Soporte de atajos de teclado rápidos: tecla `Esc` y combinación `Ctrl + Q`.
    *   Cierre limpio en `closeEvent` garantizando la detención de animaciones o recursos de fondo.
5.  **Suite de Pruebas Automatizadas (Completado):**
    *   `MAIN/tests/test_styles.py`: Valida la existencia del background y la integridad de las reglas QSS.
    *   `MAIN/tests/test_components.py`: Valida `AvatarWidget` (estados y bocadillo), `StatusWidget` y `MenuWidget` en modo *offscreen*.
    *   `MAIN/tests/test_main_window.py`: Comprueba el ciclo de vida de la ventana, la interacción del botón de comanda y los eventos de cierre.
    *   `MAIN/tests/run_tests.py`: Ejecutor de pruebas unificado ejecutable con `pixi run test` o `python MAIN/tests/run_tests.py`.

---

### Siguientes Pasos
1.  **Animaciones del Avatar:** Incorporar o generar los archivos GIF correspondientes (`vitoria_idle.gif`, `vitoria_listen.gif`, `vitoria_think.gif`, `vitoria_habla.gif`) dentro de `MAIN/assets/animations/`.
2.  **Integración ROS 2 / Lógica de Señales:** Conectar las señales de PyQt6 con los publicadores y suscriptores de ROS 2 (`/avatar_state`, `/tts_say`, `/arm_status` y `/comanda`).
3.  **Pruebas del Módulo de Audio:** Verificar el flujo de reconocimiento con `faster-whisper` y sintetizador de voz `piper-tts` integrado con la GUI.
