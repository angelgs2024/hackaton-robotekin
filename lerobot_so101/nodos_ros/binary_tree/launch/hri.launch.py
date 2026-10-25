from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    models = PathJoinSubstitution([FindPackageShare('binary_tree'), 'models'])
    return LaunchDescription([
        DeclareLaunchArgument('interface', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('microfono', default_value='-1',
                              description='Índice de entrada PortAudio; -1 usa la predeterminada'),
        DeclareLaunchArgument('modelo', default_value=PathJoinSubstitution([
            models, 'vosk-model-es-0.42'])),
        DeclareLaunchArgument('voz', default_value=PathJoinSubstitution([
            models, 'es_ES-davefx-medium.onnx'])),
        Node(package='binary_tree', executable='pregunta', output='screen',
             parameters=[{'voz': LaunchConfiguration('voz'),
                          'interface_mode': ParameterValue(LaunchConfiguration('interface'), value_type=bool)}]),
        Node(package='binary_tree', executable='escucha', output='screen',
             condition=UnlessCondition(LaunchConfiguration('interface')),
             parameters=[{'modelo': LaunchConfiguration('modelo'),
                          'microfono': ParameterValue(LaunchConfiguration('microfono'), value_type=int)}]),
        Node(package='binary_tree', executable='confirma', output='screen',
             condition=UnlessCondition(LaunchConfiguration('interface'))),
    ])
