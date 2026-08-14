from ultralytics import YOLO
from huggingface_hub import hf_hub_download

import cv2
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class ServoPublisher(Node):
    def __init__(self):

        super().__init__("servo_publisher")

        self.pub = self.create_publisher(
            Float64,
            "/servo_angle",
            10
        )
    def publish_angle(self, angle):

        msg = Float64()

        msg.data = float(angle)

        self.pub.publish(msg)
def main():
    rclpy.init()
    node = ServoPublisher()

    model_path = hf_hub_download(
        repo_id="AdamCodd/YOLOv11n-face-detection",
        filename="model.pt"
    )
    model = YOLO(model_path)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not found")
        return
    servo_center = 90
    current_angle = 90
    camera_fov = 70
    gain = 2
    print("Press q to quit")

    velocity_gain = 0.15

    last_time = time.time()
    while rclpy.ok():
        rclpy.spin_once(
            node,
            timeout_sec=0
        )
        ret, frame = cap.read()
        if not ret:
            break
        h, w, _ = frame.shape
        image_center_x = w // 2
        results = model(
            frame,
            conf=0.5,
            verbose=False
        )
        face_found = False
        for r in results:
            for box in r.boxes:
                face_found = True
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )
                center_x = (x1 + x2)//2
                cv2.rectangle(
                    frame,
                    (x1,y1),
                    (x2,y2),
                    (0,255,0),
                    2
                )
                cv2.circle(
                    frame,
                    (center_x, h//2),
                    5,
                    (0,0,255),
                    -1
                )
                cv2.circle(
                    frame,
                    (image_center_x, h//2),
                    5,
                    (255,0,0),
                    -1
                )
                pixel_error = (
                    center_x -
                    image_center_x
                )
                angle_error = (

                    pixel_error *

                    (camera_fov / w)

                )

# Convert error to velocity

                velocity = angle_error * velocity_gain


                # Limit velocity

                velocity = max(
                    -60,
                    min(
                        60,
                        velocity
                    )
                )


                # Time difference

                now = time.time()

                dt = now - last_time

                last_time = now



                # Integrate velocity into angle

                current_angle += velocity * dt



                # Servo limits

                current_angle = max(
                    0,
                    min(
                        180,
                        current_angle
                    )
                )

                node.publish_angle(
                    current_angle
                )
                print(
                    "Error:",
                    round(angle_error,2),
                    "Angle:",
                    round(current_angle,2)
                )
        if not face_found:

            # return to center

            node.publish_angle(
                servo_center
            )
        cv2.imshow(
            "face_tracking",
            frame
        )
        if cv2.waitKey(1) & 0xFF == ord('q'):

            break
    cap.release()

    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()
if __name__ == "__main__":

    main()