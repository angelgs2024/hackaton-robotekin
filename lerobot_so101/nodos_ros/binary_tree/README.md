# Behavior tree con HRI integrado

Este paquete ejecuta únicamente la toma de pedidos: un árbol C++ con la acción
`TomarPedido` y los tres nodos Python de HRI. Para llevarlo
a otro workspace, copia **toda la carpeta `binary_tree`** a su directorio `src`.
No necesita el paquete ROS `hri` ni `hri_example` para compilar o ejecutar.

```text
binary_tree/
  hri/                       # pregunta.py, escucha.py, confirma.py, menu.py
  scripts/hri_node.in         # genera los tres ejecutables ROS al compilar
  include/binary_tree/waiter_bt_nodes/tomar_pedido.hpp
  src/waiter_bt_nodes/tomar_pedido.cpp
  config/waiter_behavior_tree.xml
  launch/hri.launch.py
  launch/waiter_behavior.py
```

`hri/` se instala como módulo Python `binary_tree_hri` dentro del mismo paquete
ROS `binary_tree`. El árbol predeterminado contiene solo `TomarPedido` y termina
cuando el pedido está confirmado y guardado en la blackboard, o si falla la acción.

## Tomar un pedido por voz

Desde la raíz `lerobot_so101`, en una terminal nueva, ejecuta:

```bash
pixi run pedido
```

El comando usa el entorno Pixi del proyecto, descarga los modelos de Vosk y
Piper si faltan, compila `binary_tree` en `nodos_ros` y arranca el árbol junto
con `pregunta`, `escucha` y `confirma`. No necesitas crear `.venv-hri` ni cargar
el ROS de `/opt/ros` para este comando. La primera ejecución necesita internet;
las siguientes reutilizan los modelos locales.

El reconocimiento usa `vosk-model-es-0.42`, el modelo completo de español
(descarga de unos 1,4 GB). Tiene menor error publicado que el modelo pequeño
en los conjuntos de evaluación de [Vosk](https://alphacephei.com/vosk/models).
Necesita más memoria y tarda más en cargar; espera al mensaje «Modelo de voz
preparado» y después al aviso de escucha. Esa comparación no garantiza el mismo
resultado en el ruido de tu sala.

Escucha la pregunta del robot. Cuando aparezca `🎤 escuchando...`, di
«quiero sopa y agua». Cuando te pida confirmación y vuelva a escuchar,
di «sí». El pedido confirmado se guarda en la blackboard y se muestra en la
terminal. Los dispositivos de entrada y salida son los predeterminados del
escritorio; el arranque configura ALSA para usar los plugins de audio del sistema.

Las preguntas usan la voz natural en español de Piper, con el ritmo y la
entonación del modelo y el efecto metálico desactivado, también con `--keyboard`.

Al terminar, pulsa Ctrl+C para cerrar los nodos antes de iniciar otro pedido.

Si el ruido son otras personas hablando, el modelo también puede transcribirlas.
Acerca el micrófono a tu boca; un micrófono de auriculares o direccional ayuda
a que tu voz predomine. Para elegir una entrada concreta:

```bash
pixi run pedido-microfonos
pixi run pedido microfono:=4
```

Sustituye `4` por el índice de tu micrófono en la lista (debe tener canales
de entrada, `in`). El valor `-1` conserva la entrada predeterminada del escritorio.
En cada escucha se muestra el nombre del dispositivo que se está utilizando.

También puedes preparar los pasos por separado:

```bash
pixi run pedido-modelos
pixi run pedido-build
```

## Blackboard

```xml
<TomarPedido comida="{food_order}" bebida="{drink_order}"
             pedido="{order}" timeout="120"/>
```

La acción espera a los tres nodos HRI, publica `/hri/empezar` y permanece en
`RUNNING` hasta recibir `/hri/pedido`. Solo el pedido confirmado produce
`SUCCESS`. Un mensaje mal formado o superar `timeout` segundos produce `FAILURE`.
El plazo incluye la espera al arranque de HRI.

Para `chuleton,agua`, escribe estas cadenas en la blackboard compartida del árbol:

| Clave | Valor |
| --- | --- |
| `food_order` | `chuleton` |
| `drink_order` | `agua` |
| `order` | `chuleton,agua` |

Las siguientes acciones pueden declarar puertos de entrada y usar
`comida="{food_order}"` o `bebida="{drink_order}"` en el XML. En C++ leen esos
puertos con `getInput<std::string>("comida")` y `getInput<std::string>("bebida")`.
Los nombres entre llaves se pueden cambiar sin modificar HRI.

Los nodos Python se comunican por tópicos; la acción C++ es quien escribe en la
blackboard. Estar en el mismo paquete no comparte memoria entre procesos.
La suscripción al pedido es volátil para no recuperar pedidos retenidos de una
ejecución anterior. Se vacían las salidas al comenzar y `confirma` reinicia sus
datos al recibir `/hri/empezar`.

Usar una sola conversación a la vez: los tópicos son globales. Detener la acción
BT deja de aceptar resultados, pero no interrumpe audio que ya está en curso.

## Compilar y ejecutar

Necesitas ROS 2 Jazzy y BehaviorTree.CPP 4.

Desde `nodos_ros`, con ROS cargado:

```bash
colcon build --packages-select binary_tree --symlink-install
source install/setup.bash
```

Para voz, el Python usado al compilar necesita `numpy`, `sounddevice`, `vosk` y
`piper-tts` (`pyttsx3` es la alternativa de voz). Estas dependencias ya figuran
en el `pixi.toml` del proyecto, pero también deben estar disponibles si compilas
con el Python de otro entorno.

La tarea `pedido-modelos` descarga los modelos dentro de `binary_tree/models/`.
Si trasladas el paquete, puedes llevar también esa carpeta:

```text
models/
  vosk-model-es-0.42/
  es_ES-davefx-medium.onnx
  es_ES-davefx-medium.onnx.json
```

También puedes indicar sus rutas absolutas al lanzar:

```bash
ros2 launch binary_tree waiter_behavior.py \
  modelo:=/ruta/vosk-model-es-0.42 \
  voz:=/ruta/es_ES-davefx-medium.onnx
```

Este lanzamiento arranca `pregunta`, `escucha`, `confirma` y `waiter_behavior_bt`.
El árbol inicia la conversación en cuanto HRI está preparado; no ejecutes además
el antiguo `hri.sh`, porque arrancaría otra copia de los nodos.

## Tomar el pedido por teclado, con preguntas habladas

```bash
pixi run pedido --keyboard
```

El robot saluda, pregunta y confirma en voz alta exactamente como en modo voz.
Cuando aparezca `🧑`, escribe el pedido, pulsa Enter y después responde `sí`
cuando pida confirmación. Solo cambia la entrada: usa la terminal en lugar del
micrófono. El pedido termina en la misma blackboard.

Este modo prepara Piper para hablar, pero no descarga ni carga Vosk. Pulsa
Ctrl+C para cerrar los nodos al terminar. Sin `--keyboard` se usa el micrófono.

### Arranque manual en terminales separadas

Después de cargar `install/setup.bash` en cada terminal, ejecuta cada línea en
una terminal distinta. El modo teclado necesita una terminal con entrada:

```bash
ros2 run binary_tree pregunta
ros2 run binary_tree escucha --ros-args -p modo:=teclado
ros2 run binary_tree confirma
ros2 run binary_tree waiter_behavior_bt
```

En la terminal de `escucha`, escribe `chuleton y agua` y después `sí`.
El árbol mostrará `Order saved to blackboard: chuleton,agua` y terminará con éxito.
`pregunta` usa la voz disponible o muestra el texto si no hay motor de voz.
