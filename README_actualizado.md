<div align="center">

# Robot Camarero SO-101

**Sistema HRI para un robot camarero con GUI, voz local, ROS 2 y BehaviorTree.CPP**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![ROS 2](https://img.shields.io/badge/ROS_2-Jazzy-22314E?logo=ros&logoColor=white)](https://docs.ros.org/en/jazzy/) [![Pixi](https://img.shields.io/badge/environment-Pixi-6B4FBB?logo=conda-forge&logoColor=white)](https://pixi.sh/) [![Platform](https://img.shields.io/badge/platform-Linux%20x86__64-2EA44F?logo=linux&logoColor=white)](https://ubuntu.com/) [![GUI](https://img.shields.io/badge/GUI-PyQt6-41CD52?logo=qt&logoColor=white)](https://www.qt.io/qt-for-python) [![License](https://img.shields.io/badge/license-package--specific-informational)](#licencia)

</div>

> Proyecto de demostración desarrollado para el hackathon de Robotekin.

Sistema de interacción persona-robot (HRI) para un brazo SO-101 que representa
el flujo de un camarero: recibe una comanda de comida y bebida, la confirma
por voz o teclado y la deja disponible para un árbol de comportamiento ROS 2.
El repositorio también incluye una interfaz gráfica de demostración en PyQt6
con una mesa, una carta visual y estados del micrófono y del brazo.

El entorno completo se gestiona con [Pixi](https://pixi.sh/) y está fijado por
[`pixi.lock`](lerobot_so101/pixi.lock). La plataforma declarada actualmente es
Linux x86_64.

## Índice

- [Qué contiene el proyecto](#qué-contiene-el-proyecto)
- [Estado y alcance](#estado-y-alcance)
- [Requisitos](#requisitos)
- [Instalación en Ubuntu/Linux](#instalación-en-ubuntulinux)
- [Ejecución rápida](#ejecución-rápida)
- [Arquitectura del flujo HRI](#arquitectura-del-flujo-hri)
- [Árbol de comportamiento](#árbol-de-comportamiento)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Pruebas](#pruebas)
- [Desarrollo y mantenimiento](#desarrollo-y-mantenimiento)
- [Solución de problemas](#solución-de-problemas)
- [Licencia](#licencia)

## Qué contiene el proyecto

El sistema está compuesto por dos superficies principales:

1. **GUI de demostración** (`lerobot_so101/MAIN/`): aplicación PyQt6 para seleccionar plato y
   bebida, confirmar una comanda y mostrar el estado visual del sistema.
2. **Flujo ROS 2** (`lerobot_so101/nodos_ros/binary_tree/`): paquete ROS 2 Jazzy que integra
   los nodos HRI en Python con un árbol de comportamiento C++ basado en
   BehaviorTree.CPP. La acción `TomarPedido` espera una comanda confirmada y
   escribe sus partes en la blackboard.

El flujo ejecutable utiliza el HRI integrado en
[`lerobot_so101/nodos_ros/binary_tree/hri/`](lerobot_so101/nodos_ros/binary_tree/hri/).

## Estado y alcance

| Área | Estado | Descripción |
| --- | --- | --- |
| Entorno | ✅ Listo | Pixi con dependencias bloqueadas en `lerobot_so101/pixi.lock` |
| GUI | ✅ Lista | Selección visual de plato y bebida con PyQt6 |
| HRI por teclado | ✅ Lista | Conversación completa sin micrófono |
| HRI por voz | ✅ Lista | Vosk para STT y Piper para TTS local |
| Árbol ROS 2 | ✅ Lista | Acción `TomarPedido` con blackboard y timeout |
| Control físico del SO-101 | ⚙️ Extensible | El flujo deja el pedido preparado para la siguiente capa de manipulación |

> **Nota:** la GUI y el flujo HRI son superficies de ejecución relacionadas,
> pero actualmente se lanzan por separado. La GUI no publica automáticamente
> los pedidos en `/hri/pedido`.

### Principios del proyecto

- **Reproducibilidad:** dependencias y tareas centralizadas en Pixi.
- **Privacidad:** reconocimiento y síntesis de voz ejecutados localmente.
- **Modularidad:** nodos ROS 2 desacoplados mediante tópicos.
- **Seguridad operacional:** validación del formato del pedido, timeout y
  descarte de mensajes retenidos de conversaciones anteriores.
- **Desarrollo incremental:** modo teclado disponible para probar el flujo sin
  depender de un micrófono.

## Requisitos

- Ubuntu/Linux de 64 bits.
- Internet durante la instalación de dependencias y la primera descarga de
  modelos.
- Micrófono y altavoces para el modo de voz.
- Una pantalla con servidor gráfico para la GUI.
- Para el modo teclado no hace falta micrófono, pero el robot puede seguir
  usando Piper para responder por los altavoces.

Pixi instala en el entorno:

- Python 3.12.
- ROS 2 Jazzy Desktop y `colcon`.
- BehaviorTree.CPP 4.
- PyQt6, NumPy, MuJoCo, LeRobot y `so101-nexus`.
- Audio (`sounddevice`, PortAudio), reconocimiento Vosk y síntesis Piper.

Las versiones exactas resueltas están en
[`lerobot_so101/pixi.lock`](lerobot_so101/pixi.lock); las restricciones y tareas
declaradas están en [`lerobot_so101/pixi.toml`](lerobot_so101/pixi.toml).

## Instalación en Ubuntu/Linux

### 1. Instalar Pixi

El instalador oficial para Linux se puede descargar y ejecutar con `curl`:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

El instalador normalmente añade Pixi a `~/.pixi/bin`. Si el comando `pixi` no
se encuentra después de abrir una terminal nueva, añade esa ruta a la sesión:

```bash
export PATH="$HOME/.pixi/bin:$PATH"
pixi --version
```

Para dejarlo permanente en Bash:

```bash
echo 'export PATH="$HOME/.pixi/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Obtener el repositorio

```bash
git clone https://github.com/angelgs2024/hackaton-robotekin.git
cd hackaton-robotekin/lerobot_so101
```

Si el repositorio ya está descargado, entra en la carpeta
`hackaton-robotekin/lerobot_so101`, que contiene el workspace Pixi.

### 3. Crear el entorno reproducible

```bash
pixi install --locked
```

`--locked` obliga a respetar [`pixi.lock`](lerobot_so101/pixi.lock). Para actualizar
dependencias de forma deliberada, puede usarse `pixi install` sin esa opción y
revisar los cambios del lockfile.

Comprobar que el entorno responde:

```bash
pixi run python --version
pixi run ros2 --help
```

No es necesario crear un `venv`, instalar ROS 2 desde `/opt/ros` ni ejecutar
`pip install` manualmente para los flujos descritos en este README.

## Ejecución rápida

Todos los comandos siguientes se ejecutan desde
`hackaton-robotekin/lerobot_so101/`.

### GUI de demostración

```bash
pixi run gui
```

La ventana muestra:

- Fondo del restaurante desde `lerobot_so101/MAIN/assets/images/restaurant_bg.png`.
- Carta con tres estados de plato: vacío, sopa y plato principal.
- Carta con tres estados de bebida: vacío, agua y refresco.
- Plato, bebida y cubiertos posicionados sobre la mesa.
- Bocadillo de diálogo.
- Indicadores de micrófono y brazo.
- Botón **Confirmar Comanda**.

La comanda comienza vacía. Al confirmarla, el bocadillo muestra el pedido
seleccionado y el estado del brazo pasa a `SIRVIENDO COMANDA`. Esta GUI es una
demostración local: no publica por sí sola la comanda en un tópico ROS 2.

Atajos:

- `Esc`: cerrar.
- `Ctrl+Q`: cerrar.
- `✕ Salir`: cerrar desde la ventana.

### Tomar un pedido por voz

Primero descarga los modelos y después prepara y ejecuta el paquete:

```bash
pixi run pedido-modelos
pixi run pedido
```

`pedido` compila `binary_tree` y arranca el árbol de comportamiento junto con
los nodos `pregunta`, `escucha` y `confirma`. El script configura ALSA para
usar los plugins de audio del escritorio cuando están disponibles.

Habla cuando aparezca `🎤 escuchando...`. Por ejemplo:

```text
Quiero sopa y agua
sí
```

El modelo de reconocimiento completo en español ocupa aproximadamente 1,4 GB.
La descarga se reanuda si se interrumpe y los modelos quedan en
`nodos_ros/binary_tree/models/`.

Para listar los micrófonos:

```bash
pixi run pedido-microfonos
```

Para seleccionar un dispositivo concreto, usa su índice:

```bash
pixi run pedido microfono:=4
```

El índice `-1` usa el dispositivo de entrada predeterminado del escritorio.

### Tomar un pedido por teclado

El robot continúa hablando, pero la entrada se escribe en la terminal:

```bash
pixi run pedido --keyboard
```

Cuando aparezca `🧑`, escribe, por ejemplo, `sopa y agua`, pulsa Enter y
responde `sí` cuando se solicite la confirmación. Este modo solo descarga la
voz de Piper y no carga el modelo Vosk.

### Preparar y compilar por separado

```bash
pixi run pedido-modelos
pixi run pedido-build
```

El segundo comando ejecuta:

```bash
colcon build --packages-select binary_tree --symlink-install \
  --cmake-args -DPython3_EXECUTABLE=$CONDA_PREFIX/bin/python \
  -DBUILD_TESTING=ON
```

Los artefactos de compilación se generan en `nodos_ros/build`,
`nodos_ros/install` y `nodos_ros/log`. Son temporales y no deben versionarse.

## Arquitectura del flujo HRI

El flujo actual usa cuatro procesos ROS 2:

```text
TomarPedido (árbol C++) -- /hri/empezar --> pregunta
                                      pregunta -- /hri/escuchar --> escucha
                                      escucha -- /hri/oido --> confirma
                                      confirma -- /hri/preguntar --> pregunta
                                      confirma -- /hri/decir --> pregunta
                                      confirma -- /hri/pedido --> TomarPedido
```

### Nodos

- **`pregunta`**: saluda, verbaliza las preguntas y solicita una nueva escucha.
  Usa Piper con `es_ES-davefx-medium`; si no puede cargar Piper, intenta
  `pyttsx3` y, finalmente, muestra el texto.
- **`escucha`**: captura una frase con Vosk y `sounddevice`, o lee una línea
  desde teclado cuando `modo` es `teclado`.
- **`confirma`**: normaliza texto, reconoce las opciones de
  [`menu.py`](lerobot_so101/nodos_ros/binary_tree/hri/menu.py), pregunta por los datos
  faltantes y publica la comanda cuando el usuario confirma.
- **`waiter_behavior_bt`**: ejecuta el árbol XML, espera a que los nodos HRI
  estén disponibles, publica el inicio de conversación y valida el formato
  `comida,bebida`.

### Tópicos

| Tópico | Tipo | Dirección | Uso |
| --- | --- | --- | --- |
| `/hri/empezar` | `std_msgs/msg/Empty` | árbol → `pregunta` | Inicia una conversación |
| `/hri/escuchar` | `std_msgs/msg/Empty` | `pregunta` → `escucha` | Solicita una frase |
| `/hri/oido` | `std_msgs/msg/String` | `escucha` → `confirma` | Texto reconocido o escrito |
| `/hri/preguntar` | `std_msgs/msg/String` | `confirma` → `pregunta` | Pregunta que debe verbalizarse |
| `/hri/decir` | `std_msgs/msg/String` | `confirma` → `pregunta` | Mensaje verbal sin nueva escucha |
| `/hri/pedido` | `std_msgs/msg/String` | `confirma` → árbol | Pedido confirmado, por ejemplo `chuleton,agua` |

La acción C++ escribe en la blackboard estas salidas:

| Puerto | Ejemplo |
| --- | --- |
| `comida` | `chuleton` |
| `bebida` | `agua` |
| `pedido` | `chuleton,agua` |

El pedido se considera inválido si no contiene exactamente una coma con un
valor no vacío a cada lado. El tiempo de espera predeterminado es de 120
segundos.

Para cambiar la carta, edita
[`menu.py`](lerobot_so101/nodos_ros/binary_tree/hri/menu.py), donde
cada opción tiene un identificador, el nombre hablado y las palabras que se
reconocen.

## Árbol de comportamiento

### Diagrama del árbol

![Diagrama del árbol de comportamiento del robot camarero, sin los nodos Delay](behavior_tree.png)

El árbol predeterminado está en
[`waiter_behavior_tree.xml`](lerobot_so101/nodos_ros/binary_tree/config/waiter_behavior_tree.xml)
y contiene una única acción:

```xml
<TomarPedido comida="{food_order}" bebida="{drink_order}"
             pedido="{order}" timeout="120"/>
```

El nodo personalizado está implementado en
[`tomar_pedido.cpp`](lerobot_so101/nodos_ros/binary_tree/src/waiter_bt_nodes/tomar_pedido.cpp)
y registrado mediante
[`bt_node_registration.cpp`](lerobot_so101/nodos_ros/binary_tree/src/waiter_bt_nodes/bt_node_registration.cpp).
Para ampliar el comportamiento, modifica el XML y añade acciones siguiendo los
patrones de BehaviorTree.CPP y ROS 2 del paquete.

## Estructura del repositorio

```text
hackaton-robotekin/
└── lerobot_so101/
    ├── pixi.toml                 # Dependencias, constraints y tareas Pixi
    ├── pixi.lock                 # Resolución reproducible de versiones
    ├── MAIN/
    │   ├── main.py               # Entrada de la GUI
    │   ├── assets/images/        # Fondo, platos, bebidas y cubiertos
    │   ├── src/gui/              # Ventana, estilos y componentes
    │   └── tests/                # Pruebas PyQt6 headless
    └── nodos_ros/binary_tree/
        ├── hri/                  # pregunta, escucha, confirma y menú
        ├── src/                  # Ejecutable BT y acción TomarPedido
        ├── include/              # Cabeceras C++
        ├── config/               # Árbol XML
        ├── launch/               # Lanzamientos ROS 2
        ├── scripts/              # Modelos, audio y wrappers HRI
        └── test/                 # Pruebas GTest de la acción
```

## Pruebas

### GUI

Las pruebas fuerzan `QT_QPA_PLATFORM=offscreen`, por lo que no necesitan una
ventana visible:

```bash
pixi run test
```

Esto ejecuta [`run_tests.py`](lerobot_so101/MAIN/tests/run_tests.py), que descubre
las pruebas de estilos, componentes y ventana principal.

También se puede ejecutar directamente:

```bash
pixi run python MAIN/tests/run_tests.py
```

### Paquete ROS 2

`pedido-build` compila con las pruebas CMake activadas. Para ejecutar los tests
del workspace tras compilar:

```bash
pixi run bash -c 'cd nodos_ros && colcon test --packages-select binary_tree'
pixi run bash -c 'cd nodos_ros && colcon test-result --verbose'
```

Las pruebas de
[`test_tomar_pedido.cpp`](lerobot_so101/nodos_ros/binary_tree/test/test_tomar_pedido.cpp)
comprueban pedidos válidos, pedidos mal formados, timeouts, limpieza de la
blackboard y descarte de mensajes pendientes de una conversación anterior.

## Desarrollo y mantenimiento

- Añade o modifica dependencias en
  [`pixi.toml`](lerobot_so101/pixi.toml) y actualiza
  [`pixi.lock`](lerobot_so101/pixi.lock) de forma intencionada.
- Mantén el uso de `pixi run` para que Python, ROS 2 y CMake provengan del
  mismo entorno.
- Después de modificar código C++ o archivos ROS 2, vuelve a ejecutar
  `pixi run pedido-build`.
- Si una compilación antigua apunta a otro Python, elimina únicamente
  `nodos_ros/build`, `nodos_ros/install` y `nodos_ros/log`, y recompila.
- Los modelos descargados y los directorios `.pixi`, `build`, `install` y
  `log` son artefactos locales; no deben añadirse al control de versiones.

## Solución de problemas

### pixi: command not found

Abre una terminal nueva o ejecuta:

```bash
export PATH="$HOME/.pixi/bin:$PATH"
```

### No se oye el robot o no se detecta el micrófono

Comprueba los dispositivos con `pixi run pedido-microfonos`. Verifica los
permisos de audio del escritorio y prueba un índice explícito con
`pixi run pedido microfono:=N`. El script intenta usar la configuración ALSA
del sistema (`/usr/share/alsa/alsa.conf`) y sus plugins disponibles.

### Fallo al cargar los modelos

Ejecuta de nuevo `pixi run pedido-modelos`. La descarga del modelo Vosk usa un
archivo parcial y puede reanudarse; comprueba que haya espacio libre para el
modelo de aproximadamente 1,4 GB y para la voz de Piper.

### La GUI no arranca en una sesión sin pantalla

La GUI necesita un servidor gráfico. En servidores o CI, ejecuta solo
`pixi run test`, que ya configura Qt en modo `offscreen`.

## Licencia

Este proyecto se distribuye bajo la
[Apache License 2.0](LICENSE). Consulta el archivo [`LICENSE`](LICENSE) para
conocer los términos completos.

La licencia permite usar, estudiar, modificar y redistribuir el software,
incluido su uso comercial, siempre que se cumplan sus condiciones de
redistribución, avisos de copyright, licencia y cambios realizados.



---

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/Davilood">
        <img src="https://github.com/Davilood.png" width="72" height="72" alt="David Martín Fortea">
      </a><br>
      <sub><b>David Martín Fortea</b></sub><br>
      <a href="https://github.com/Davilood">GitHub</a> ·
      <a href="https://www.linkedin.com/in/david-mart%C3%ADn-fortea-249a631b4/">LinkedIn</a>
    </td>
    <td align="center">
      <a href="https://github.com/angelgs2024">
        <img src="https://github.com/angelgs2024.png" width="72" height="72" alt="Ángel García Sánchez">
      </a><br>
      <sub><b>Ángel García Sánchez</b></sub><br>
      <a href="https://github.com/angelgs2024">GitHub</a> ·
      <a href="https://www.linkedin.com/in/%C3%A1ngel-garc%C3%ADa-s%C3%A1nchez-6566312b7/">LinkedIn</a>
    </td>
    <td align="center">
      <a href="https://github.com/Alcrox">
        <img src="https://github.com/Alcrox.png" width="72" height="72" alt="Álex Montecino Puerto">
      </a><br>
      <sub><b>Álex Montecino Puerto</b></sub><br>
      <a href="https://github.com/Alcrox">GitHub</a> ·
      <a href="https://linkedin.com/in/%C3%A1lex-montecino-puerto-848959354/">LinkedIn</a>
    </td>
  </tr>
</table>