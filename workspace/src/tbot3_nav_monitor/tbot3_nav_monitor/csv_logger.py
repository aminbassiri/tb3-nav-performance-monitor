import csv
import math
import os

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class CSVLogger(Node):
    """
    CSVLogger continuously logs robot position and path length based on odometry.

    It computes the total traveled distance and stores:
    - timestamp
    - position (x, y)
    - cumulative path length
    """

    def __init__(self):
        super().__init__('csv_logger')

        # Subscribe to odometry topic
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Store last position to compute distance incrementally
        self.last_position = None
        self.total_path_length = 0.0

        # Ensure output directory exists
        self.output_dir = '/root/ws/results'
        os.makedirs(self.output_dir, exist_ok=True)

        # CSV file path
        self.csv_file = os.path.join(self.output_dir, 'nav_metrics.csv')

        file_exists = os.path.exists(self.csv_file)

        # Open CSV file in append mode
        self.file = open(self.csv_file, 'a', newline='')
        self.writer = csv.writer(self.file)

        # Write header if file is new
        if not file_exists:
            self.writer.writerow(['time_sec', 'x', 'y', 'path_length'])

        self.get_logger().info(f'CSV Logger started. Writing to {self.csv_file}')

    def odom_callback(self, msg):
        """
        Called whenever new odometry data arrives.
        Computes incremental distance and logs it.
        """

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        current = (x, y)

        # Compute distance from last position
        if self.last_position is not None:
            dx = current[0] - self.last_position[0]
            dy = current[1] - self.last_position[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)
            self.total_path_length += distance

        self.last_position = current

        # Convert ROS time to seconds
        time_sec = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9

        # Write to CSV
        self.writer.writerow([time_sec, x, y, self.total_path_length])
        self.file.flush()

        self.get_logger().info(
            f'Logged: t={time_sec:.2f}, x={x:.2f}, y={y:.2f}, path={self.total_path_length:.2f}'
        )

    def destroy_node(self):
        """
        Close file properly when node shuts down.
        """
        if hasattr(self, 'file') and self.file:
            self.file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CSVLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
