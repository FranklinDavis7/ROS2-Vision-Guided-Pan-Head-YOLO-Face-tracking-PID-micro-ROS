import cv2
from ultralytics import YOLO

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState


class FaceWheelTracker(Node):

    def __init__(self):

        super().__init__(
            "face_wheel_tracker"
        )

        self.filtered_cx = 320  
        # -----------------------------
        # YOLO model
        # -----------------------------

        self.model = YOLO(
            "/microros_ws/ros2_ws/src/camera_stream/resource/yolov8n-face.pt"
        )


        # -----------------------------
        # Camera
        # -----------------------------

        self.cap = cv2.VideoCapture(0)


        if not self.cap.isOpened():

            self.get_logger().error(
                "Cannot open camera"
            )

            exit()


        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            640
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            480
        )



        # -----------------------------
        # Face tracking controller
        # -----------------------------

        # -----------------------------
        # Smooth controller
        # -----------------------------

        self.Kp = 0.004
        self.Kd = 0.001

        self.dead_zone = 25


        # current and target angle

        self.joint_angle = 0.0
        self.target_angle = 0.0


        # previous error

        self.prev_error = 0.0


        # smoothing factor
        # smaller = smoother

        self.alpha = 0.15


        # maximum rotation speed

        self.max_step = 0.02


        # limits

        self.max_angle = 1.57



        # -----------------------------
        # Publish joint state
        # -----------------------------

        self.joint_pub = self.create_publisher(
            JointState,
            "/joint_states",
            10
        )


        # Timer

        self.timer = self.create_timer(
            0.03,
            self.process_frame
        )


        self.get_logger().info(
            "Face wheel tracker started"
        )



    def process_frame(self):


        ret, frame = self.cap.read()


        if not ret:

            return



        height, width = frame.shape[:2]


        image_center_x = width // 2
        image_center_y = height // 2



        # -----------------------------
        # YOLO detection
        # -----------------------------

        results = self.model(
            frame,
            conf=0.5,
            verbose=False
        )



        output = frame.copy()



        # default no movement

        error_x = 0



        for r in results:


            for box in r.boxes:


                x1, y1, x2, y2 = (

                    box.xyxy[0]
                    .cpu()
                    .numpy()
                    .astype(int)

                )


                # -----------------------------
                # Face centroid
                # -----------------------------

                cx = int(
                    (x1+x2)/2
                )

                cy = int(
                    (y1+y2)/2
                )


                error_x = (
                    cx -
                    image_center_x
                )



                # -----------------------------
                # Proportional control
                # -----------------------------


                # -----------------------------
                # Filter face position
                # -----------------------------

                self.filtered_cx = (
                    self.alpha * cx +
                    (1-self.alpha)*self.filtered_cx
                )


                error_x = (
                    self.filtered_cx -
                    image_center_x
                )



                # -----------------------------
                # Dead zone
                # -----------------------------

                if abs(error_x) < self.dead_zone:

                    error_x = 0



                # -----------------------------
                # PD controller
                # -----------------------------

                derivative = (
                    error_x -
                    self.prev_error
                )


                control = (
                    self.Kp * error_x +
                    self.Kd * derivative
                )


                self.prev_error = error_x



                # target angle

                self.target_angle -= control



                # limit target

                self.target_angle = max(
                    min(
                        self.target_angle,
                        self.max_angle
                    ),
                    -self.max_angle
                )



                # -----------------------------
                # Smooth motion
                # -----------------------------

                difference = (
                    self.target_angle -
                    self.joint_angle
                )


                if abs(difference) > self.max_step:

                    self.joint_angle += (
                        self.max_step *
                        (1 if difference > 0 else -1)
                    )

                else:

                    self.joint_angle = self.target_angle



                    # limit angle

                    self.joint_angle = max(
                        min(
                            self.joint_angle,
                            self.max_angle
                        ),
                        -self.max_angle
                    )




                # -----------------------------
                # Draw detection
                # -----------------------------

                cv2.rectangle(
                    output,
                    (x1,y1),
                    (x2,y2),
                    (0,255,0),
                    2
                )


                cv2.circle(
                    output,
                    (cx,cy),
                    5,
                    (0,0,255),
                    -1
                )



                cv2.line(
                    output,
                    (image_center_x,0),
                    (image_center_x,height),
                    (255,0,0),
                    2
                )



                cv2.putText(
                    output,
                    f"error: {error_x}",
                    (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0),
                    2
                )


                cv2.putText(
                    output,
                    f"angle: {self.joint_angle:.2f}",
                    (20,80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,255),
                    2
                )




        # -----------------------------
        # Publish joint state
        # -----------------------------


        joint_msg = JointState()


        joint_msg.header.stamp = (
            self.get_clock()
            .now()
            .to_msg()
        )


        joint_msg.name = [

            "top_wheel_joint"

        ]


        joint_msg.position = [

            self.joint_angle

        ]


        self.joint_pub.publish(
            joint_msg
        )



        # Display camera

        cv2.imshow(
            "Face Tracker",
            output
        )


        cv2.waitKey(1)




    def destroy_node(self):


        self.cap.release()

        cv2.destroyAllWindows()

        super().destroy_node()





def main(args=None):


    rclpy.init(args=args)


    node = FaceWheelTracker()



    try:

        rclpy.spin(node)


    except KeyboardInterrupt:

        pass



    node.destroy_node()


    rclpy.shutdown()





if __name__ == "__main__":

    main()