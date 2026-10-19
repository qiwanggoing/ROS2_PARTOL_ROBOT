"""Exercise localization and a real NavigateToPose action in the running simulation."""
import argparse
import json
import math
from pathlib import Path
import time

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseWithCovarianceStamped, Twist
from lifecycle_msgs.srv import GetState
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Odometry
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformException, TransformListener


class NavigationCheck(Node):
    def __init__(self):
        super().__init__('navigation_check', parameter_overrides=[
            Parameter('use_sim_time', value=True)])
        self.scan_count = 0
        self.clock_seconds = 0.0
        self.localized = False
        self.odom_start = None
        self.odom_last = None
        self.motion_commands = 0
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.initial_pose = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.create_subscription(LaserScan, '/scan', self.scan, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/odom', self.odom, qos_profile_sensor_data)
        self.create_subscription(Clock, '/clock', self.clock, qos_profile_sensor_data)
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.amcl, 10)
        self.create_subscription(Twist, '/cmd_vel', self.velocity, 10)
        self.navigator = ActionClient(self, NavigateToPose, '/navigate_to_pose')

    def scan(self, msg):
        if any(math.isfinite(v) and msg.range_min <= v <= msg.range_max for v in msg.ranges):
            self.scan_count += 1

    def odom(self, msg):
        self.odom_last = (msg.pose.pose.position.x, msg.pose.pose.position.y)
        if self.odom_start is None:
            self.odom_start = self.odom_last

    def clock(self, msg):
        self.clock_seconds = msg.clock.sec + msg.clock.nanosec / 1e9

    def amcl(self, _msg):
        self.localized = True

    def velocity(self, msg):
        if abs(msg.linear.x) + abs(msg.angular.z) > 0.001:
            self.motion_commands += 1

    def position(self):
        try:
            tf = self.buffer.lookup_transform('map', 'base_footprint', rclpy.time.Time())
            return (tf.transform.translation.x, tf.transform.translation.y)
        except TransformException:
            return None

    def wait(self, condition, seconds, message):
        deadline = time.monotonic() + seconds
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
            if condition():
                return
        raise RuntimeError(message)

    def require_active(self, node_name, timeout):
        client = self.create_client(GetState, node_name + '/get_state')
        deadline = time.monotonic() + timeout
        try:
            while time.monotonic() < deadline:
                if not client.wait_for_service(timeout_sec=0.5):
                    rclpy.spin_once(self, timeout_sec=0.1)
                    continue
                future = client.call_async(GetState.Request())
                self.wait(future.done, min(5, max(0, deadline - time.monotonic())),
                          node_name + ' lifecycle request timed out')
                if future.result().current_state.id == 3:
                    self.get_logger().info(node_name + ' is active')
                    return
                rclpy.spin_once(self, timeout_sec=0.2)
            raise RuntimeError(node_name + ' did not become active')
        finally:
            self.destroy_client(client)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--x', type=float, default=2.0)
    parser.add_argument('--y', type=float, default=1.0)
    parser.add_argument('--yaw', type=float, default=0.0, help='Goal yaw in radians')
    parser.add_argument('--initial-x', type=float, default=0.0)
    parser.add_argument('--initial-y', type=float, default=0.0)
    parser.add_argument('--initial-yaw', type=float, default=0.0)
    parser.add_argument('--timeout', type=float, default=180.0)
    parser.add_argument('--output', default='log/navigation_check.json')
    args = parser.parse_args()
    rclpy.init(args=[])
    node = NavigationCheck()
    report = {'goal': [args.x, args.y, args.yaw], 'success': False}
    goal_handle = None
    started = time.monotonic()
    try:
        node.wait(lambda: node.clock_seconds > 0 and node.scan_count > 0
                  and node.odom_last is not None, 90,
                  'Simulation is missing /clock, valid /scan, or /odom')
        node.require_active('amcl', 60)
        pose = PoseWithCovarianceStamped()
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x = args.initial_x
        pose.pose.pose.position.y = args.initial_y
        pose.pose.pose.orientation.z = math.sin(args.initial_yaw / 2)
        pose.pose.pose.orientation.w = math.cos(args.initial_yaw / 2)
        pose.pose.covariance[0] = 0.05
        pose.pose.covariance[7] = 0.05
        pose.pose.covariance[35] = 0.02
        deadline = time.monotonic() + 30
        while not node.localized or node.position() is None:
            if time.monotonic() > deadline:
                raise RuntimeError('AMCL did not establish map -> base_footprint')
            pose.header.stamp = node.get_clock().now().to_msg()
            node.initial_pose.publish(pose)
            for _ in range(10):
                rclpy.spin_once(node, timeout_sec=0.1)
        report['start_position'] = node.position()
        # The global costmap needs map -> odom before planner activation can finish.
        for name in ['controller_server', 'planner_server', 'bt_navigator']:
            node.require_active(name, 60)
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = node.get_clock().now().to_msg()
        goal.pose.pose.position.x = args.x
        goal.pose.pose.position.y = args.y
        goal.pose.pose.orientation.z = math.sin(args.yaw / 2)
        goal.pose.pose.orientation.w = math.cos(args.yaw / 2)
        if not node.navigator.wait_for_server(timeout_sec=10):
            raise RuntimeError('NavigateToPose action server unavailable')
        sent = node.navigator.send_goal_async(goal)
        node.wait(sent.done, 10, 'Goal acknowledgement timed out')
        goal_handle = sent.result()
        if not goal_handle.accepted:
            raise RuntimeError('Navigation goal was rejected')
        node.get_logger().info(f'Navigating to ({args.x}, {args.y})')
        result = goal_handle.get_result_async()
        node.wait(result.done, args.timeout, 'Navigation timed out')
        report['action_status'] = result.result().status
        for _ in range(10):
            rclpy.spin_once(node, timeout_sec=0.1)
        report['final_position'] = node.position()
        if report['final_position'] is None:
            raise RuntimeError('Final map transform unavailable')
        report['position_error_m'] = math.dist(report['final_position'], (args.x, args.y))
        report['odom_displacement_m'] = math.dist(node.odom_start, node.odom_last)
        report['success'] = (report['action_status'] == GoalStatus.STATUS_SUCCEEDED
                             and report['position_error_m'] <= 0.25
                             and node.scan_count > 0 and node.motion_commands > 0)
    except (RuntimeError, KeyboardInterrupt) as exc:
        report['error'] = str(exc) or 'Interrupted'
        if goal_handle is not None and rclpy.ok():
            cancel = goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(node, cancel, timeout_sec=5)
    finally:
        report.update(elapsed_s=round(time.monotonic() - started, 2),
                      valid_scan_messages=node.scan_count,
                      nonzero_velocity_commands=node.motion_commands,
                      simulation_time_s=node.clock_seconds)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0 if report['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
