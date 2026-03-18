from setuptools import find_packages, setup

# Name of the ROS2 Python package
package_name = 'tbot3_nav_monitor'

setup(
    # Package name used by ROS2 / Python packaging
    name=package_name,

    # Package version
    version='0.0.0',

    # Automatically find Python modules inside the package
    # Exclude test folder from installation
    packages=find_packages(exclude=['test']),

    # Files that must be installed together with the package
    data_files=[
        # Register this package in the ROS2 ament index
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),

        # Install package.xml so ROS2 can read package metadata
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],

    # Python dependencies required for installation
    install_requires=['setuptools'],

    # Allows package to be installed as a zip archive
    zip_safe=True,

    # Maintainer information
    maintainer='root',
    maintainer_email='root@todo.todo',

    # Short package description
    description='ROS2 package for TurtleBot3 navigation monitoring and evaluation',

    # License field
    license='TODO: License declaration',

    # Extra dependencies only needed for testing
    extras_require={
        'test': [
            'pytest',
        ],
    },

    # Entry points create executable ROS2 commands
    entry_points={
        'console_scripts': [
            # Run with: ros2 run tbot3_nav_monitor metrics_collector
            'metrics_collector = tbot3_nav_monitor.metrics_collector:main',

            # Run with: ros2 run tbot3_nav_monitor csv_logger
            'csv_logger = tbot3_nav_monitor.csv_logger:main',

            # Run with: ros2 run tbot3_nav_monitor goal_bridge
            'goal_bridge = tbot3_nav_monitor.goal_bridge:main',
        ],
    },
)