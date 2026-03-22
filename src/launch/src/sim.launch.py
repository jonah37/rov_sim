from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, Command
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Gazebo world
    world_file = PathJoinSubstitution([
        FindPackageShare('gazebo'),
        'worlds',
        'olympic_pool',
        'pool.world'
    ])

    # Launch Gazebo
    gz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ),
        launch_arguments={'gz_args': world_file}.items()
    )

    # Xacro file
    xacro_file = PathJoinSubstitution([
        FindPackageShare('rov_description'),
        'urdf',
        'assembly.xacro'
    ])

    # Convert xacro to XML
    robot_xml = Command(['xacro ', xacro_file])

    # Spawn robot in Gazebo
    spawn_ROV = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', robot_xml,
            '-name', 'rov',
            '-x', '0',
            '-y', '0',
            '-z', '0'
        ],
        output='screen'
    )

    # Environment variable for meshes/models/worlds
    env_var = SetEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        PathJoinSubstitution([
            FindPackageShare('rov_description')
        ])
    )

    # ROS nodes
    joy = Node(package='joy', executable='joy_node')

    vector_conversion = Node(
        package='rov_control',
        executable='vector_conversion'
    )

    ESCs = Node(
        package='rov_control',
        executable='ESCs'
    )

    thrusters = Node(
        package='rov_control',
        executable='thrusters'
    )

    # ros_gz_bridge using YAML config
    bridge_config = PathJoinSubstitution([
        FindPackageShare('rov_description'),
        'config',
        'ros_gz_config.yaml'
    ])

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config}],
        output='screen'
    )

    return LaunchDescription([
        env_var,
        gz_launch,
        spawn_ROV,
        ros_gz_bridge,
        joy,
        vector_conversion,
        ESCs,
        thrusters
    ])
