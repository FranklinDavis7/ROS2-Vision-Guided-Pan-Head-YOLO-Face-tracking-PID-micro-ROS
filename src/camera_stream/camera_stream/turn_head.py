import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
import time
class Turn_head(Node):

    def __init__(self):
        super().__init__('turn_head')

        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        initial = 0.0
        self.pub = self.create_publisher(
            Float64,
            '/neck_joint/cmd_pos',
            10
        )
    
    def joint_state_callback(self, msg):
        if 'neck_joint' not in msg.name:
            return

        index = msg.name.index('neck_joint')
        position = msg.position[index]
        if position == initial:
            position=3.10
            command = Float64()
            command.data = position
            self.pub.publish(command)
            self.get_logger().info(f'Sending initial target: {position:.2f} rad')
        elif position == 3.10:
            position = 0
            command = Float64()
            command.data = position
            self.pub.publish(command)
        else:
            pass
def main(args=None):
    rclpy.init(args=args)
    node = Turn_head()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
