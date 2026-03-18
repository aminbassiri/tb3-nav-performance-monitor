import csv
import math
import os

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped
from action_msgs.msg import GoalStatusArray


class MetricsCollector(Node):
    """
    MetricsCollector

    This node monitors navigation performance in real time.
    It computes:
    - execution time
    - final position error
    - actual traveled path length
    - planned path length
    - obstacle avoidance efficiency
    - recovery behavior frequency
    - battery proxy

    It also implements a simple rule-based adaptive behavior system.
    """

    def __init__(self):
        super().__init__('metrics_collector')

        # ----------------------------
        # Subscribers
        # ----------------------------
        self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )
        self.create_subscription(
            PoseStamped, '/goal_pose', self.goal_callback, 10
        )
        self.create_subscription(
            Path, '/plan', self.plan_callback, 10
        )
        self.create_subscription(
            GoalStatusArray,
            '/navigate_to_pose/_action/status',
            self.status_callback,
            10
        )

        # ----------------------------
        # Navigation state
        # ----------------------------
        self.current_position = None
        self.last_position = None
        self.start_position = None
        self.goal_position = None
        self.goal_active = False

        self.goal_start_time = None
        self.path_length = 0.0

        # Store first valid planned path for a goal
        self.planned_path_length = None

        # ----------------------------
        # Recovery / stuck detection
        # ----------------------------
        self.recovery_count = 0
        self.last_move_time = None

        # Robot is considered stuck if there is no meaningful motion
        # for this many seconds during an active goal.
        self.stuck_threshold_time = 3.0

        # Minimum odom movement to count as real progress
        self.min_movement = 0.02

        # Minimum path length before stuck detection becomes active
        self.min_path_before_stuck_check = 0.3

        # ----------------------------
        # Adaptive behavior state
        # ----------------------------
        self.max_velocity_scale = 1.0
        self.goal_tolerance = 0.25
        self.planning_mode = "normal"
        self.costmap_mode = "normal"

        # ----------------------------
        # CSV logging
        # ----------------------------
        self.output_dir = '/root/ws/results'
        os.makedirs(self.output_dir, exist_ok=True)

        self.csv_file = os.path.join(self.output_dir, 'goal_metrics.csv')
        file_exists = os.path.exists(self.csv_file)

        self.file = open(self.csv_file, 'a', newline='')
        self.writer = csv.writer(self.file)

        if not file_exists:
            self.writer.writerow([
                'timestamp',
                'goal_x',
                'goal_y',
                'exec_time_sec',
                'final_error',
                'path_length',
                'planned_path_length',
                'efficiency_ratio',
                'recovery_count',
                'battery_proxy',
                'velocity_scale',
                'goal_tolerance',
                'planning_mode',
                'costmap_mode'
            ])
            self.file.flush()

        # Timer used for periodic stuck detection
        self.create_timer(0.5, self.check_stuck)

        self.get_logger().info('Metrics Collector with Adaptive Behavior started')

    # --------------------------------------------------
    # Odometry callback
    # --------------------------------------------------
    def odom_callback(self, msg):
        """
        Update current position and integrate traveled path length.
        """
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        current = (x, y)

        self.current_position = current

        if self.goal_active and self.last_position is not None:
            dx = current[0] - self.last_position[0]
            dy = current[1] - self.last_position[1]
            dist = math.sqrt(dx * dx + dy * dy)

            self.path_length += dist

            # Update movement timer only if motion is meaningful
            if dist > self.min_movement:
                self.last_move_time = self.get_clock().now()

        self.last_position = current

    # --------------------------------------------------
    # Goal callback
    # --------------------------------------------------
    def goal_callback(self, msg):
        """
        Triggered when a new goal is received.
        Resets metrics for the new run.
        """
        x = msg.pose.position.x
        y = msg.pose.position.y

        self.goal_position = (x, y)
        self.goal_active = True

        self.goal_start_time = self.get_clock().now()
        self.start_position = self.current_position

        self.path_length = 0.0
        self.planned_path_length = None
        self.recovery_count = 0

        self.last_move_time = self.get_clock().now()

        # Reset adaptive state for this run
        self.max_velocity_scale = 1.0
        self.goal_tolerance = 0.25
        self.planning_mode = "normal"
        self.costmap_mode = "normal"

        self.get_logger().info(f'New goal: ({x:.2f},{y:.2f})')

    # --------------------------------------------------
    # Plan callback
    # --------------------------------------------------
    def plan_callback(self, msg):
        """
        Compute planned path length from the planner output.

        To avoid unstable tiny plan values, we only accept a plan if:
        - it has enough points
        - total length is > 0.2 m

        Also, for each goal, we keep the first valid plan only.
        """
        if not self.goal_active:
            return

        if self.planned_path_length is not None:
            return

        if len(msg.poses) < 2:
            return

        total = 0.0
        for i in range(1, len(msg.poses)):
            x1 = msg.poses[i - 1].pose.position.x
            y1 = msg.poses[i - 1].pose.position.y
            x2 = msg.poses[i].pose.position.x
            y2 = msg.poses[i].pose.position.y
            total += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if total > 0.2:
            self.planned_path_length = total

    # --------------------------------------------------
    # Stuck / recovery detection
    # --------------------------------------------------
    def check_stuck(self):
        """
        Detect if the robot is stuck during an active goal.

        To reduce false positives:
        - do nothing if there is no active goal
        - do nothing before the robot has moved enough overall
        - trigger recovery only if there has been no meaningful movement
          for a certain time
        """
        if not self.goal_active:
            return

        if self.last_move_time is None:
            return

        # Avoid declaring 'stuck' too early
        if self.path_length < self.min_path_before_stuck_check:
            return

        now = self.get_clock().now()
        elapsed = (now - self.last_move_time).nanoseconds / 1e9

        if elapsed > self.stuck_threshold_time:
            self.recovery_count += 1
            self.last_move_time = now

            self.get_logger().warn(
                f"REAL STUCK detected → recovery #{self.recovery_count}"
            )

            # Adaptive reaction
            self.max_velocity_scale *= 0.8
            self.planning_mode = "conservative"

            self.get_logger().warn(
                "Adaptive: reducing speed & switching to conservative mode"
            )

    # --------------------------------------------------
    # Status callback
    # --------------------------------------------------
    def status_callback(self, msg):
        """
        Observe navigation status and finish the run when Nav2 reports
        success or terminal failure.
        """
        if not self.goal_active:
            return

        if not msg.status_list:
            return

        latest_status = msg.status_list[-1].status

        # 4 = SUCCEEDED
        if latest_status == 4:
            self.finish_goal(success=True)

        # 5 = CANCELED, 6 = ABORTED
        elif latest_status in [5, 6]:
            self.finish_goal(success=False)

    # --------------------------------------------------
    # Finish goal
    # --------------------------------------------------
    def finish_goal(self, success=True):
        """
        Finalize a run:
        - compute final metrics
        - apply adaptive rules
        - log to CSV
        """
        if not self.goal_active:
            return

        end_time = self.get_clock().now()
        exec_time = (end_time - self.goal_start_time).nanoseconds / 1e9

        final_error = self.distance(self.current_position, self.goal_position)

        # Efficiency:
        # Prefer planned path if valid.
        # Otherwise use straight-line distance as fallback.
        if self.planned_path_length is not None and self.planned_path_length > 1e-6:
            efficiency_ratio = self.path_length / self.planned_path_length
        else:
            direct_distance = self.distance(self.start_position, self.goal_position)
            if direct_distance > 1e-6:
                efficiency_ratio = self.path_length / direct_distance
            else:
                efficiency_ratio = 0.0

        # Simple battery proxy
        battery_proxy = 0.5 * self.path_length + 2.0 * self.recovery_count

        # ----------------------------
        # Adaptive behavior rules
        # ----------------------------

        # Poor accuracy → relax tolerance
        if final_error > 0.3:
            self.goal_tolerance *= 1.5
            self.get_logger().warn(
                "Adaptive: increasing goal tolerance"
            )

        # Inefficient path → conservative planning
        if efficiency_ratio > 2.0:
            self.planning_mode = "conservative"
            self.get_logger().warn(
                "Adaptive: inefficient path → conservative mode"
            )

        # Complex environment → costmap mode change
        if self.path_length > 3.5:
            self.costmap_mode = "complex"
            self.get_logger().warn(
                "Adaptive: complex environment detected → adjusting costmap mode"
            )

        timestamp = self.get_clock().now().nanoseconds / 1e9

        self.writer.writerow([
            timestamp,
            self.goal_position[0],
            self.goal_position[1],
            exec_time,
            final_error,
            self.path_length,
            self.planned_path_length if self.planned_path_length is not None else 0.0,
            efficiency_ratio,
            self.recovery_count,
            battery_proxy,
            self.max_velocity_scale,
            self.goal_tolerance,
            self.planning_mode,
            self.costmap_mode
        ])
        self.file.flush()

        self.get_logger().info(
            f"Done | success={success} "
            f"time={exec_time:.2f}s "
            f"error={final_error:.2f} "
            f"path={self.path_length:.2f} "
            f"eff={efficiency_ratio:.2f}"
        )

        self.goal_active = False

    # --------------------------------------------------
    # Distance helper
    # --------------------------------------------------
    def distance(self, a, b):
        """
        Euclidean distance between two 2D points.
        """
        if a is None or b is None:
            return 0.0
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    # --------------------------------------------------
    # Clean shutdown
    # --------------------------------------------------
    def destroy_node(self):
        if hasattr(self, 'file') and self.file:
            self.file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MetricsCollector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()