# Control del SO101 simulado con PS4

Desde esta carpeta, conecta el mando por USB o empareja el DualShock 4 por
Bluetooth y ejecuta:

```bash
pixi run mando
```

El menú permite **abrir el simulador**, **probar el mando**, **listar mandos**,
**consultar los controles** y **salir**. El simulador empieza en pausa:
pulsa OPTIONS para moverlo. La tabla de controles también aparece en la terminal.

| Control | Movimiento |
| --- | --- |
| L2 | Abrir / destensar la pinza progresivamente |
| R2 | Cerrar / apretar la pinza progresivamente |
| Joystick izquierdo arriba / abajo | Alargar / recoger el brazo |
| Joystick derecho izquierda / derecha | Girar la base |
| X / círculo | Subir / bajar la pinza |
| Cuadrado / triángulo | Inclinar la muñeca en sentidos opuestos |
| Joystick derecho arriba / abajo | Rotar la muñeca en sentidos opuestos |
| L1 mantenido | Reducir la velocidad al 25 % |
| OPTIONS | Pausar / continuar |
| SHARE, estando en pausa | Reiniciar la escena |
| PS | Volver al menú (o salir en modo directo) |
| Ctrl+C | Cerrar el programa |

Mantén cada control para mover; al soltarlo se mantiene el objetivo articular.
Los gatillos regulan la apertura, no una fuerza medida. La simulación puede
presentar pequeños desplazamientos por gravedad o contacto. El alcance se mide
respecto a la base del robot, independientemente de la cámara. Hombro, codo y
muñeca se coordinan para cambiar alcance/altura; por eso la inclinación de la
pinza puede variar durante esos movimientos. La geometría, los límites de las
articulaciones y las colisiones restringen el recorrido. No hay planificación
para evitar obstáculos.

La pausa congela la simulación. Si se desconecta el mando, se cierra esa sesión
y se informa del error: reconecta y vuelve a entrar desde el menú. Al completar
la tarea se pausa la escena; SHARE la reinicia. No hay reinicios por tiempo.

## Otros comandos

```bash
# Comprobar ejes y botones sin abrir el simulador
pixi run mando-test

# Abrir directamente, a la mitad de velocidad
pixi run python controlar_ps4.py --iniciar --velocidad 0.5

# Listar mandos accesibles
pixi run python controlar_ps4.py --listar-mandos

# Elegir una ruta mostrada por el listado
pixi run python controlar_ps4.py --dispositivo /dev/input/eventN

# Aumentar la zona muerta si el joystick se mueve solo
pixi run python controlar_ps4.py --zona-muerta 0.2

# Ejecutar pruebas sin ventana ni mando
pixi run python -m unittest -v test_controlar_ps4
```

La velocidad admite valores entre 0.1 y 2.0; la zona muerta, entre 0 y 0.5.
Si hay varios mandos, el programa permite elegir uno. Se usa el mapeo de Linux
para DualShock 4, tanto USB como Bluetooth; los mandos compatibles que anuncien
ejes diferentes pueden necesitar una adaptación. Si no aparece el mando,
comprueba la conexión y el acceso de tu usuario a su `/dev/input/eventN`.
El programa requiere una sesión gráfica para mostrar MuJoCo.

Implementado con la API de estado y eventos de
[python-evdev](https://python-evdev.readthedocs.io/en/latest/apidoc.html).
La dependencia está declarada en `pixi.toml`. Este script controla únicamente
el simulador; `ver_brazo.py` sigue disponible como demostración aleatoria.
