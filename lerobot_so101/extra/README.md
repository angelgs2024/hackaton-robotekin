# Robot Camarero - Sistema HRI (LeRobot SO101)

Sistema de **Interacción Persona-Robot (HRI)** desarrollado para un brazo robótico SO101 en rol de camarero, capaz de atender clientes, tomar comandas (comida y bebida) y servirlas. Dispone de una interfaz gráfica (GUI) con estética **Frutiger Aero** (Glassmorphism), síntesis y reconocimiento de voz en local (STT/TTS) y control cinemático tanto físico como simulado sobre **ROS 2**.

---

## 🛠️ Herramientas y Stack Tecnológico

El proyecto integra las siguientes herramientas y dependencias, gestionadas de forma reproducible mediante **Pixi**:

| Herramienta / Librería | Versión / Tipo | Propósito |
| :--- | :--- | :--- |
| **Pixi** | Entorno conda/pypi | Gestor de dependencias y tareas del proyecto multiplataforma. |
| **Python** | 3.12 | Lenguaje base del proyecto. |
| **PyQt6** | GUI Framework | Interfaz gráfica de usuario con renderizado acelerado y QSS adaptativo. |
| **ROS 2 (Humble)** | Middleware Robótico | Comunicación modular por nodos, tópicos y servicios (`ament_python`). |
| **LeRobot** | `v0.6.1+` (Hugging Face)| Librería de robótica y aprendizaje por imitación para manipuladores. |
| **so101-nexus** | Driver hardware | Control cinemático, teleoperación y comunicación con servomotores Feetech del brazo SO101. |
| **MuJoCo** | `>=3.13.0` | Motor de simulación física para emular el brazo en entorno 3D antes del despliegue real. |
| **faster-whisper** | STT Local | Reconocimiento de voz del cliente en tiempo real sin conexión a internet. |
| **piper-tts** | TTS Local | Síntesis de voz neural ultrarrápida en español para respuestas del robot. |
| **sounddevice & portaudio**| Audio I/O | Captura de micrófono y reproducción de voz. |
| **evdev** | Driver de entrada | Lectura de gamepad para control manual opcional con mando de PS4 (`controlar_ps4.py`). |
| **unittest** | Testing | Suite de pruebas unitarias automatizadas ejecutables en modo *headless* (*offscreen*). |

---

## 🎨 Diseño de la Interfaz Gráfica (Frutiger Aero)

La interfaz se inspira en el estilo **Frutiger Aero** de mediados de los 2000 (cristal translúcido, reflejos sutiles, degradados de cielo y agua, fondos fotorrealistas):

1. **Fondo Panorámico:**
   - Carga la escena del local ([MAIN/assets/images/restaurant_bg.png](MAIN/assets/images/restaurant_bg.png)) mediante `border-image`, escalando de forma fluida a cualquier resolución sin repetición ni recortes.
2. **Contenedor Flotante Sutil:**
   - El contenedor principal `#MainContainer` es prácticamente transparente (5%–10% de opacidad) con un borde fino de 1 px que aporta un destello vítreo sin ocultar el fondo.
3. **Panel Izquierdo (Avatar y Globo de Voz):**
   - El avatar se renderiza en **gran formato en el centro de la mitad izquierda**, utilizando la imagen [waiter_no_bg.png](MAIN/assets/images/waiter_no_bg.png) como base visual completa para todos los estados a la espera de las animaciones GIF.
   - El globo de diálogo translúcido (`speech_bubble`) flota en la parte inferior **superpuesto por delante del avatar**, creando una estructura multicapa armónica (Fondo -> Avatar -> Globo).
4. **Panel Derecho (Menú Sofisticado Arriba a la Derecha):**
   - Diseñado como una cápsula compacta de cristal translúcido con estética **Frutiger Aero (Glassmorphism)**.
   - **Distribución en 2 columnas:**
     - **Izquierda (Comida):** 2 platos seleccionables (🍲 Sopa del Día, 🥩 Plato Principal).
     - **Derecha (Bebida):** 2 bebidas seleccionables (🧊 Agua Mineral, 🥤 Refresco).
   - Selector interactivo con destello cian translúcido y marca de selección `✓` en azul profundo.
   - Botón interactivo *"✨ Confirmar Comanda"* que anuncia los productos seleccionados y actualiza el estado del brazo.
   - Indicadores de estado de periféricos (Micrófono y Brazo).
5. **Cierre de la Aplicación:**
   - Botón superior derecho `✕ Salir` con iluminación hover.
   - Atajos de teclado: tecla <kbd>Esc</kbd> o combinación <kbd>Ctrl</kbd> + <kbd>Q</kbd>.
   - Limpieza en `closeEvent` para asegurar la finalización segura de hilos y animaciones.

---

## 📁 Estructura del Directorio

```text
lerobot_so101/
├── pixi.toml                   # Definición de dependencias conda/pypi y tareas
├── pixi.lock                   # Bloqueo de versiones reproducible
├── README.md                   # Documentación general y herramientas
├── Resumen.md                  # Bitácora de desarrollo y contexto
├── controlar_ps4.py            # Nodo/script de teleoperación con mando PS4
├── test_controlar_ps4.py       # Pruebas para el mando
├── MANDO_PS4.md                # Guía de mapeo de controles PS4
├── MAIN/
│   ├── main.py                 # Punto de entrada de la aplicación GUI
│   ├── assets/
│   │   ├── images/
│   │   │   └── restaurant_bg.png # Fondo panorámico del restaurante
│   │   ├── animations/         # GIFs del avatar (idle.gif, listen.gif, etc.)
│   │   └── audio/              # Modelos o sonidos auxiliares
│   ├── src/
│   │   ├── styles.py           # Re-exportador de estilos globales
│   │   └── gui/
│   │       ├── styles.py       # Reglas QSS Frutiger Aero y resolución de rutas
│   │       ├── main_window.py  # Ventana principal y layouts
│   │       └── components/
│   │           ├── __init__.py
│   │           ├── avatar_widget.py # Widget del avatar y bocadillo
│   │           ├── menu_widget.py   # Menú 2 columnas (Comida / Bebida)
│   │           └── status_widget.py # Indicadores de hardware
│   └── tests/
│       ├── run_tests.py        # Ejecutor unificado de pruebas headless
│       ├── test_styles.py      # Tests de rutas de imágenes y QSS
│       ├── test_components.py  # Tests unitarios de widgets
│       └── test_main_window.py # Tests de ventana principal y eventos
```

---

## 🚀 Comandos de Ejecución

Desde la raíz del repositorio, usando Pixi:

### 1. Iniciar la Interfaz Gráfica (GUI)
```bash
pixi run start
```
*(O de forma directa: `python MAIN/main.py`)*

### 2. Ejecutar la Suite de Pruebas Automatizadas
```bash
pixi run test
```
*(O de forma directa: `python MAIN/tests/run_tests.py`)*

### 3. Probar el Control con Mando PS4
```bash
# Modo de prueba de botones y sticks
pixi run mando-test

# Ejecutar teleoperación del brazo
pixi run mando
```

---

## 📡 Arquitectura de Comunicación (ROS 2)

El sistema interconecta la interfaz gráfica, el procesador de voz y el brazo mediante tópicos de ROS 2:

*   `/avatar_state` (`std_msgs/String`): Modifica el estado del avatar (`idle`, `listen`, `think`, `habla`).
*   `/comanda` (`std_msgs/String`): Envía el pedido seleccionado en formato JSON (ej. `{"plato": "Sopa del Día", "bebida": "Agua Mineral"}`).
*   `/arm_status` (`std_msgs/String`): Notifica a la interfaz el estado del manipulador robótico (`DESCONECTADO`, `EN REPOSO`, `SIRVIENDO COMANDA`).
*   `/tts_say` (`std_msgs/String`): Texto que el motor de voz `piper-tts` debe sintetizar hacia los altavoces.

---

## 📋 Estado Actual y Próximos Pasos

- [x] Entorno base configurado con `Pixi` y soporte para `PyQt6`, `ROS 2`, `LeRobot` y `MuJoCo`.
- [x] Fondo panorámico fotorrealista con resolución de ruta dinámica y escalado QSS.
- [x] Contenedor de cristal sutil y translúcido.
- [x] Avatar sin recuadros preparado para animaciones limpias sobre el fondo.
- [x] Bocadillo de diálogo posicionado en la parte inferior.
- [x] Menú compacto arriba a la derecha con 2 columnas (Comida a la izquierda y Bebida a la derecha).
- [x] Selector interactivo de comanda que alimenta la respuesta de servicio.
- [x] Sistema de cierre con botón en pantalla y atajos <kbd>Esc</kbd> / <kbd>Ctrl+Q</kbd>.
- [x] Suite de tests automatizados *headless* con `run_tests.py`.
- [ ] **Siguiente paso:** Añadir archivos GIF en `MAIN/assets/animations/` (`idle.gif`, `listen.gif`, `think.gif`, `habla.gif`).
- [ ] **Siguiente paso:** Conectar los suscriptores y publicadores de ROS 2 a las señales de PyQt6.
- [ ] **Siguiente paso:** Integrar el pipeline de audio local con `faster-whisper` y `piper-tts`.
