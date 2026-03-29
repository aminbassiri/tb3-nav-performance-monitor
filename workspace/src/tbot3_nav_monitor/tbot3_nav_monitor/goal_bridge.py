import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class GoalBridge(Node):
    """
    GoalBridge acts as an interface between a simple ROS topic (/goal_pose)
    and the Nav2 action server (/navigate_to_pose).

    It allows sending navigation goals using topic publishing instead of directly
    interacting with ROS2 action clients.
    """

    def __init__(self):
        super().__init__('goal_bridge')

        # Create an ActionClient to communicate with Nav2 navigation server
        self.action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')

        # Subscribe to goal topic
        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )

        self.get_logger().info('Goal bridge started')

    def goal_callback(self, msg):
        """
        Called whenever a new goal is published on /goal_pose.
        Converts the PoseStamped message into a Nav2 action goal.
        """

        self.get_logger().info('Received goal_pose')

        # Create Nav2 goal message
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = msg

        # Wait until Nav2 action server is ready
        self.action_client.wait_for_server()

        # Send goal asynchronously
        send_goal_future = self.action_client.send_goal_async(goal_msg)

        # Register callback when goal is accepted/rejected
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """
        Called after sending the goal to Nav2.
        Checks whether the goal was accepted.
        """

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        # Wait for navigation result asynchronously
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        """
        Called when navigation finishes (success or failure).
        """
        self.get_logger().info('Navigation finished')


def main(args=None):
    rclpy.init(args=args)

    node = GoalBridge()

    # Keep node running
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
