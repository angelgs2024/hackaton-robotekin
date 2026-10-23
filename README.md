# Hackathon Robotekin

El entorno compartido de manipulación e interacción HRI está en
`lerobot_so101/pixi.toml`, con versiones fijadas en `lerobot_so101/pixi.lock`.
Se mantiene la base de `main`: Linux x86_64, Python 3.12 y ROS 2 Jazzy Desktop.

```bash
cd lerobot_so101
pixi install --locked
pixi run mando       # simulación SO-101 y mando PS4
pixi run modelo      # descargar modelos de voz, una vez
pixi run probar      # conversación por teclado
pixi run hri         # conversación por micrófono
```

Las tareas HRI compilan el paquete ROS antes de arrancarlo y usan
`hri_ros2/models` para los modelos. No hace falta activar otro entorno.

- [Uso y nodos HRI](hri_ros2/README.md)
- [Control con PS4](lerobot_so101/MANDO_PS4.md)

Comprobaciones sin mando ni ventana:

```bash
cd lerobot_so101
pixi run build
pixi run python -m unittest -v test_controlar_ps4
```
