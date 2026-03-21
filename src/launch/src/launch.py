from ament_index_python.packages import get_package_share_directory # Python function for retrieving the absolute path to a package's installation "share" directory
from launch import LaunchDescription # Class used to encapsulate and return the entire set of actions to be executed by the launch system
from launch_ros.actions import Node # ROS action used to define and execute a ROS2 node
from launch.actions import SetEnvironmentVariable, IncludeLaunchDescription # (1) Action to modify environment variables visible to subsequent processes in the launch and (2) an action to include and execute another launch file
from launch.launch_description_sources import PythonLaunchDescriptionSource # Helper class that tells system the included launch file is a Python-based script
from launch.substitutions import PathJoinSubstitution # Substitution tool that joins multiple path components together
from launch_ros.substitutions import FindPackageShare # Substitution that resolves a package's "share" directory path at runtime


def generate_launch_description():
    ros_gz_sim_pkg_path = get_package_share_director('ros_gz_sim')
    pkg_path = FindPackageShare('gazebo')
    gz_launch_path = PathJoinSubstitution([ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py'])

    description = LaunchDescription([
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            PathJoinSubstitution([pkg_path, 'src', 'models'])
            ),
        SetEnvironmentVariable(
            'GZ_SIM_PLUGIN_PATH',
            PathJoinSubstitution([pkg_path, 'src', 'plugins'])
            ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={
                'gz_args': PathJoinSubstitution([pkg_path, 'worlds/olympic_swimming_pool/pool.world']),
                'on_exit_shutdown': 'True'
                }.items(),
            ),

        # Bridging and remapping Gazebo topics to ROS2

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/...',],
            remappings=[('/topic',
                         '/remapped_topic'),],
            output='screen'

        ),

    ])

    return description

