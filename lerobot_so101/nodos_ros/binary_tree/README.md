# Behavior tree con HRI y modelos LeRobot

Este paquete toma el pedido mediante HRI o la interfaz y ejecuta después los
modelos LeRobot correspondientes, en secuencia. Para llevarlo
a otro workspace, copia **toda la carpeta `binary_tree`** a su directorio `src`.
No necesita el paquete ROS `hri` ni `hri_example` para compilar o ejecutar.

```text
binary_tree/
  hri/                       # pregunta.py, escucha.py, confirma.py, menu.py
  manipulation/              # validación y ejecución de políticas LeRobot
  gui/                       # interfaz PyQt6: ventana, componentes, estilos y rutas
  assets/images/             # fondo, platos, bebidas y cubiertos
  test/gui/                  # pruebas de la interfaz
  scripts/hri_node.in         # genera los tres ejecutables ROS al compilar
  include/binary_tree/waiter_bt_nodes/tomar_pedido.hpp
  src/waiter_bt_nodes/tomar_pedido.cpp
  config/waiter_behavior_tree.xml # secuencia HRI → vaso → cubiertos
  config/lerobot_models.xml       # nombres/rutas de modelos y comando LeRobot
  launch/hri.launch.py
  launch/waiter_behavior.py
```

## Interfaz gráfica y modos de pedido

La ventana PyQt6 se abre primero y directamente a pantalla completa, antes de
cargar los modelos e iniciar HRI y el árbol. Desde la raíz del repositorio:

```bash
pixi run pedido                # voz + visualización del pedido
pixi run pedido --interface    # selección y confirmación mediante botones
```

En modo voz, di «chuletón de vaca y agua»: se iluminan esas opciones y aparecen
sus imágenes. También puedes decir primero la comida y después la bebida.
El pedido solo se confirma al responder «sí»; si respondes «no», se limpia
la selección para empezar de nuevo. Los botones no admiten cambios en modo voz.

Con `--interface`, selecciona una comida (chuletón o sopa) y una bebida (agua
o Coca-Cola). **Confirmar Comanda** se habilita únicamente cuando están ambas
seleccionadas. Elegir «Plato vacío» o «Vaso vacío» vuelve a deshabilitarlo.
Al confirmar se publica un único pedido y se guarda en la misma blackboard
que en modo voz. El robot saluda, pregunta por la comida o bebida que falta
y confirma en voz alta mediante Piper. Este modo no carga Vosk ni usa el micrófono;
las respuestas y la confirmación se hacen con los botones.
El antiguo argumento de teclado se ha eliminado.

`pixi run gui` también abre el programa completo en modo botones. La ventana
permanece visible al acabar el pedido; **Salir**, Esc o Ctrl+C cierran el programa
y sus nodos. Para otro pedido, vuelve a ejecutar el comando.

El módulo `binary_tree_gui` usa las imágenes de `binary_tree/assets/images`
en desarrollo y `share/binary_tree/assets/images` al instalar. No depende de
`MAIN` ni del directorio actual. La copia original de `MAIN` se conserva.

Pruebas de interfaz y de integración ROS sin abrir ventanas ni usar audio:

```bash
pixi run test
```

La interfaz recibe `/hri/seleccion` para mostrar el pedido provisional y
`/hri/pedido` para mostrar el confirmado. En modo botones publica directamente
`/hri/pedido`. Tras confirmar, el árbol ejecuta la manipulación; la ventana
muestra su progreso en el estado del brazo mediante `/manipulacion/estado`.

`hri/` se instala como módulo Python `binary_tree_hri` dentro del mismo paquete
ROS `binary_tree`. `TomarPedido` guarda el pedido confirmado en la blackboard
y la secuencia continúa con los modelos de vasos y cubiertos.

## Configurar y ejecutar los modelos

Edita **`config/lerobot_models.xml`**. En cada `<model>`, `policy` es el nombre
`usuario/modelo` de Hugging Face o la ruta local de la política (`pretrained_model`).
Las rutas relativas deben empezar por `./` o `../`; se resuelven desde el XML.

La secuencia actual requiere las políticas de vaso amarillo, tenedor y cuchara,
que están vacías para que pongas sus nombres reales. La entrada de cuchillo
se conserva en el catálogo, pero no se valida ni ejecuta en los pedidos.
Por ejemplo:

```xml
<model id="coger_tenedor" policy="/ruta/al/modelo_tenedor"
       task="Pick up the fork and place it next to the plate" duration="60"/>
```

El bloque `<command>` conserva los parámetros de vuestro `lerobot-rollout`:
SO101 en `/dev/ttyACM1`, ID `follower_robotekin`, calibración bajo `/home/daviluud`,
cámara `top` en `/dev/video6`, `wrist` en `/dev/video4`, ambas a 640×480 y 30 FPS,
`n_action_steps=1`, `temporal_ensemble_coeff=0.01` y `display_data=false`.
Se ejecuta con el mismo Python del paquete mediante `-m lerobot.scripts.lerobot_rollout`.
Cada `<arg>` contiene un argumento completo; no pongas comillas de shell alrededor
del mapa de cámaras. Ajusta estas rutas si lo ejecutas en otra máquina.

La secuencia definida en `config/waiter_behavior_tree.xml` es:

| Pedido | Modelos ejecutados, en orden |
| --- | --- |
| Chuletón y agua | Vaso amarillo → tenedor |
| Chuletón y Coca-Cola | Vaso amarillo → tenedor |
| Sopa y agua | Vaso amarillo → cuchara |
| Sopa y Coca-Cola | Vaso amarillo → cuchara |

Tras HRI, `PrepararModelos` comprueba la configuración de todos los pasos del
pedido antes de arrancar el primero. Si falta una política o una ruta local,
la secuencia falla sin ejecutar modelos. `EjecutarModelo` permanece en `RUNNING`
hasta que su proceso acaba; solo entonces arranca el siguiente.
Un fallo interrumpe la secuencia, sin saltar a otra bebida ni a otros cubiertos.

Antes de cada vaso o cubierto, el árbol espera **5 segundos** con un nodo
`Delay delay_msec="5000"`, también en modo `test`. Esta espera no bloquea la
interfaz y se cancela al cerrar el programa.

Cada ejecución usa `duration="60"` segundos de control por defecto, como en el
comando proporcionado. Ajusta la duración y la tarea de cada política en el XML.
El final del paso se determina por la salida correcta de LeRobot, **no por una
comprobación visual de que haya cogido el objeto**. La carga del modelo también
cuenta para `model_timeout` (300 segundos por defecto). Cerrar la ventana o
cancelar el árbol detiene el proceso en curso y no ejecuta los siguientes.

Con los modelos configurados, los comandos habituales ejecutan el pedido completo:

```bash
pixi run pedido
pixi run pedido --interface
```

Para comprobar la selección y el orden **sin cargar modelos ni conectar al brazo**,
incluso antes de rellenar los nombres:

```bash
pixi run pedido test               # interfaz + HRI por voz
pixi run pedido test --interface   # elegir el pedido mediante botones
```

En modo `test`, el robot pregunta y confirma por voz normalmente. Al confirmar
«chuletón y agua», la terminal muestra, en orden:

```text
[SIMULACIÓN] Cojo vaso amarillo
[SIMULACIÓN] Cojo tenedor
```

No se ejecutan políticas ni se esperan los 60 segundos de cada movimiento.
Sí se mantienen los 5 segundos de espera antes de imprimir cada acción.
El modo `test` fuerza la simulación aunque se pase `simular_modelos:=false`.
También sigue disponible el argumento ROS `simular_modelos:=true`.

Puedes indicar otro XML y otro tiempo máximo:

```bash
pixi run pedido --interface modelos_xml:=/ruta/lerobot_models.xml model_timeout:=300.0
```

Las pruebas `pixi run test` usan simulación o procesos de prueba; no ejecutan
políticas reales. Cubren las cuatro combinaciones, el orden de finalización,
modelos pendientes, errores, tiempos agotados y cancelación.

## Tomar un pedido por voz

Desde la raíz `lerobot_so101`, en una terminal nueva, ejecuta:

```bash
pixi run pedido
```

El comando usa el entorno Pixi del proyecto, descarga los modelos de Vosk y
Piper si faltan, compila `binary_tree` en `nodos_ros` y arranca el árbol junto
con la interfaz, `pregunta`, `escucha` y `confirma`. No necesitas crear `.venv-hri` ni cargar
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
entonación del modelo y el efecto metálico desactivado.

Al terminar, cierra la ventana o pulsa Ctrl+C antes de iniciar otro pedido.

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

La acción espera a la interfaz y al nodo de voz `pregunta`; en modo voz espera
también a `escucha` y `confirma`;
publica `/hri/empezar` y permanece en
`RUNNING` hasta recibir `/hri/pedido`. Solo el pedido confirmado produce
`SUCCESS` en `TomarPedido`; después se ejecutan los modelos. Un mensaje mal formado o superar `timeout` segundos produce `FAILURE`.
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
BT deja de aceptar resultados y cancela el modelo en curso. Cerrar la ventana
cierra también los nodos HRI.

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

Este lanzamiento abre primero la interfaz y después arranca `pregunta`,
`escucha`, `confirma` y `waiter_behavior_bt`. El árbol inicia la conversación
cuando los nodos están preparados; no ejecutes además el antiguo `hri.sh`.
Para el modo botones desde ROS:

```bash
ros2 launch binary_tree waiter_behavior.py interface:=true
```

El ejecutable `interfaz` es la ventana con su puente ROS; utiliza el lanzamiento
anterior para arrancar también el árbol y completar el pedido en la blackboard.
