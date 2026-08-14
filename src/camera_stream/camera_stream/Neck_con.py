import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class TurnHead(Node):

    def __init__(self):
        super().__init__('turn_head')

        self.pub = self.create_publisher(
            Float64,
            '/neck_joint/cmd_pos',
            10
        )

        self.target = 3.14

        # Change target every 3 seconds
        self.timer = self.create_timer(
            3.5,
            self.swing
        )

        # Send first command immediately
        self.send_command(3.0)

    def send_command(self, position):
        msg = Float64()
        msg.data = position
        self.pub.publish(msg)

        self.get_logger().info(
            f'Sending target: {position:.2f} rad'
        )

    def swing(self):

        if self.target == 3.0:
            self.target = 0.0
        else:
            self.target = 3.0

        self.send_command(self.target)


def main(args=None):

    rclpy.init(args=args)

    node = TurnHead()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
