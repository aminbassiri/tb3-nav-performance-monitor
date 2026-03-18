import csv
import math
import os

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class CSVLogger(Node):
    def __init__(self):
        super().__init__('csv_logger')

        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.last_position = None
        self.total_path_length = 0.0

        self.output_dir = '/root/ws/results'
        os.makedirs(self.output_dir, exist_ok=True)

        self.csv_file = os.path.join(self.output_dir, 'nav_metrics.csv')

        file_exists = os.path.exists(self.csv_file)

        self.file = open(self.csv_file, 'a', newline='')
        self.writer = csv.writer(self.file)

        if not file_exists:
            self.writer.writerow(['time_sec', 'x', 'y', 'path_length'])

        self.get_logger().info(f'CSV Logger started. Writing to {self.csv_file}')

    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        current = (x, y)

        if self.last_position is not None:
            dx = current[0] - self.last_position[0]
            dy = current[1] - self.last_position[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)
            self.total_path_length += distance

        self.last_position = current

        time_sec = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9

        self.writer.writerow([time_sec, x, y, self.total_path_length])
        self.file.flush()

        self.get_logger().info(
            f'Logged: t={time_sec:.2f}, x={x:.2f}, y={y:.2f}, path={self.total_path_length:.2f}'
        )

    def destroy_node(self):
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