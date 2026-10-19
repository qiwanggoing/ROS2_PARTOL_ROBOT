"""Start the existing FishBot world and Nav2 without patrol application services."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    description = get_package_share_directory('fishbot_description')
    navigation = get_package_share_directory('fishbot_navigation2')
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('map', default_value=os.path.join(navigation, 'maps', 'room.yaml')),
        DeclareLaunchArgument('params_file', default_value=os.path.join(
            navigation, 'config', 'nav2_params.yaml')),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                description, 'launch', 'gazebo_sim.launch.py')),
            launch_arguments={'gui': LaunchConfiguration('gui'), 'use_sim_time': 'true'}.items()),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                navigation, 'launch', 'navigation2.launch.py')),
            launch_arguments={
                'use_sim_time': 'true',
                'use_rviz': LaunchConfiguration('use_rviz'),
                'map': LaunchConfiguration('map'),
                'params_file': LaunchConfiguration('params_file'),
            }.items()),
    ])
