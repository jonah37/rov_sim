import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node, DeclareLaunchArgument
from launch.actions import SetEnvironmentVariable, IncludeLaunchDescription, LaunchConfiguration, TextSubstitution 
from launch.launch_description_sources import PythonLaunchDescriptionSource 
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare 

def generate_launch_description():
    gazebo_package = get_package_share_directory('gazebo')
    rov_description_package = get_package_share_directory('rov_description')


    '''
    ros_gz_sim_pkg_path = get_package_share_directory('ros_gz_sim')
    pkg_path = FindPackageShare('gazebo')
    gz_launch_path = PathJoinSubstitution([ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py'])
    '''


    world_file_path = os.path.join(gazebo_package, 'worlds', 'olympic_pool', 'pool.world')
    rov_xacro_path = os.path.join(rov_description_package, 'urdf', 'assembly.xacro')

    world = DeclareLaunchARgument(
            'world_file',
            default_value=world_file_path
    )

    gazebo_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(



    ld = LaunchDescription([
        # Environment Variables
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            PathJoinSubstitution([pkg_path, 'src', 'models'])
            ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={
                'gz_args': PathJoinSubstitution([pkg_path, 'worlds/olympic_pool/pool.world']),
                'on_exit_shutdown': 'True'
                }.items(),
            ),
        # Bridging and remapping Gazebo topics to ROS2
         '''
        RosGzBridge(
            bridge_name=LaunchConfiguration('bridge_name'),
            config_file=LaunchConfiguration('ros-gz_config'),
        ),
        '''
 
        '''
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/...',],
            remappings=[('/topic',
                         '/remapped_topic'),],
            output='screen'

        ),
        '''
    ])

    return ld
