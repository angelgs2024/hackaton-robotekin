#!/usr/bin/env python3
"""Abre la ventana antes de preparar HRI y arrancar el árbol de pedidos."""
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, EmitEvent, ExecuteProcess, IncludeLaunchDescription,
    OpaqueFunction, RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit, OnProcessIO
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    mode = LaunchConfiguration('interface')
    models = PathJoinSubstitution([FindPackageShare('binary_tree'), 'models'])
    gui = Node(
        package='binary_tree', executable='interfaz', output='screen',
        parameters=[{'interface_mode': ParameterValue(mode, value_type=bool)}],
    )
    waiter = Node(
        package='binary_tree', executable='waiter_behavior_bt', output='screen',
        parameters=[{'interface_mode': ParameterValue(mode, value_type=bool),
                     'modelos_xml': LaunchConfiguration('modelos_xml'),
                     'simular_modelos': ParameterValue(LaunchConfiguration('simular_modelos'), value_type=bool),
                     'model_timeout': ParameterValue(LaunchConfiguration('model_timeout'), value_type=float)}],
    )
    hri = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        PathJoinSubstitution([FindPackageShare('binary_tree'), 'launch', 'hri.launch.py'])
    ))

    def start(context):
        script = LaunchConfiguration('preparar_modelos').perform(context)
        if not script:
            return [hri, waiter]
        args = ['--tts-only'] if mode.perform(context).lower() == 'true' else []
        prepare = ExecuteProcess(cmd=['bash', script, *args], output='screen')

        def prepared(event, _context):
            if event.returncode != 0:
                return [EmitEvent(event=Shutdown(reason='No se pudieron preparar los modelos de voz'))]
            return [hri, waiter]

        return [RegisterEventHandler(OnProcessExit(target_action=prepare, on_exit=prepared)), prepare]

    output = bytearray()
    started = False

    def ready(event):
        nonlocal started
        if started:
            return []
        output.extend(event.text)
        if b'BINARY_TREE_GUI_READY' in output:
            started = True
            return [OpaqueFunction(function=start)]
        del output[:-64]
        return []

    return LaunchDescription([
        DeclareLaunchArgument('interface', default_value='false', choices=['true', 'false'],
                              description='Elegir y confirmar el pedido con botones'),
        DeclareLaunchArgument('modelos_xml', default_value=PathJoinSubstitution([
            FindPackageShare('binary_tree'), 'config', 'lerobot_models.xml'])),
        DeclareLaunchArgument('simular_modelos', default_value='false', choices=['true', 'false'],
                              description='Mostrar la secuencia sin conectar al robot ni cargar políticas'),
        DeclareLaunchArgument('model_timeout', default_value='300.0',
                              description='Tiempo máximo por proceso, incluida la carga del modelo'),
        DeclareLaunchArgument('preparar_modelos', default_value='',
                              description='Script opcional para preparar modelos tras abrir la ventana'),
        DeclareLaunchArgument('microfono', default_value='-1',
                              description='Índice de entrada PortAudio; -1 usa la predeterminada'),
        DeclareLaunchArgument('modelo', default_value=PathJoinSubstitution([
            models, 'vosk-model-es-0.42'])),
        DeclareLaunchArgument('voz', default_value=PathJoinSubstitution([
            models, 'es_ES-davefx-medium.onnx'])),
        RegisterEventHandler(OnProcessIO(target_action=gui, on_stdout=ready)),
        RegisterEventHandler(OnProcessExit(
            target_action=gui,
            on_exit=[EmitEvent(event=Shutdown(reason='Interfaz cerrada'))],
        )),
        gui,
    ])
