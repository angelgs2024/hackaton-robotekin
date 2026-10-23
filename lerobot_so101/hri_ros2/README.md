# HRI – SO-101 camarero (ROS2 Jazzy + pixi)

Tres nodos que se hablan con texto:

```
/hri/empezar ─▶ PREGUNTA ─/hri/escuchar─▶ ESCUCHA ─/hri/oido─▶ CONFIRMA ─▶ /hri/pedido
                   ▲                                              │
                   └──────────── /hri/preguntar · /hri/decir ─────┘
```

| Nodo | Qué hace |
|---|---|
| `pregunta` | Habla: saluda con la carta y dice lo que le manden |
| `escucha` | Escucha una frase (micrófono o teclado) y la publica |
| `confirma` | Entiende comida y bebida, repregunta lo que falte y confirma |

Resultado: `/hri/pedido` (`std_msgs/String`) = `"chuleton,agua"`.
Carta en `src/hri/hri/menu.py`. Para empezar una conversación (por ejemplo, desde el BT): publicar en `/hri/empezar`.

## Uso

HRI comparte el entorno de `main`, definido en `../lerobot_so101/pixi.toml`
y fijado en `../lerobot_so101/pixi.lock`: Python 3.12, ROS 2 Jazzy Desktop
y Linux x86_64. No hay un segundo entorno PIXI para HRI.

Desde la raíz del repositorio:

```bash
cd lerobot_so101
pixi install --locked
pixi run modelo    # una vez: modelos de oído (Vosk) y voz (Piper) en español
pixi run probar    # escribiendo
pixi run hri       # con micrófono y altavoz
```

Las tareas compilan y ejecutan HRI desde `hri_ros2`; los modelos siguen en
`hri_ros2/models`. También puedes ejecutar desde esta carpeta:
`pixi run --manifest-path ../lerobot_so101/pixi.toml probar`.

Si ya compilaste con el entorno antiguo, elimina solo los artefactos generados
`hri_ros2/build`, `hri_ros2/install` y `hri_ros2/log` antes de recompilar,
para evitar referencias al Python anterior. El antiguo `hri_ros2/.pixi`
ya no se utiliza y se puede eliminar para recuperar espacio.

Las dependencias se instalan con PIXI; el modo voz necesita micrófono,
altavoz y acceso al audio del escritorio.

## Voz
`pregunta` habla con Piper (`es_ES-davefx-medium`) y le añade un timbre metálico de robot.
Parámetro `robot`: `0` = voz humana, `0.8` por defecto, `1.5` muy metálica.
Si Piper falla, usa pyttsx3 (espeak).
