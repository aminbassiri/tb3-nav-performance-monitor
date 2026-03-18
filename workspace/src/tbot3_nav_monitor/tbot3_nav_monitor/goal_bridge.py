import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class GoalBridge(Node):

    def __init__(self):
        super().__init__('goal_bridge')

        self.action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')

        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )

        self.get_logger().info('Goal bridge started')

    def goal_callback(self, msg):

        self.get_logger().info('Received goal_pose')

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = msg

        self.action_client.wait_for_server()

        send_goal_future = self.action_client.send_goal_async(goal_msg)

        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):

        self.get_logger().info('Navigation finished')


def main(args=None):

    rclpy.init(args=args)

    node = GoalBridge()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()