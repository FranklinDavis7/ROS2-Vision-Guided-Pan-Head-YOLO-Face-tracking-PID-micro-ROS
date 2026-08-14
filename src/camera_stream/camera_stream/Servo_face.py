#!/usr/bin/env python3

from ultralytics import YOLO
from huggingface_hub import hf_hub_download
import cv2
import time
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


# ==========================================
# PID Controller
# ==========================================
class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0.0
        self.integral = 0.0

    def update(self, error, dt):
        if dt <= 0:
            dt = 0.01
        self.integral += error * dt
        self.integral = max(-100, min(100, self.integral))
        derivative = (error - self.previous_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output

    def reset_integral(self):
        self.integral = 0.0


# ==========================================
# Servo Publisher (face tracking)
# ==========================================
class ServoPublisher(Node):
    def __init__(self):
        super().__init__("servo_publisher")
        self.pub = self.create_publisher(Float64, "/servo_angle", 10)
        
        self.bridge = CvBridge()
        self.latest_frame = None
        self.frame_available = False
        self.sub = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        try:
            self.latest_frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.frame_available = True
        except Exception as e:
            self.get_logger().error(f"CV Bridge error: {e}")

    def publish_angle(self, angle):
        msg = Float64()
        msg.data = float(angle)
        self.pub.publish(msg)


# ==========================================
# Main
# ==========================================
def main():
    rclpy.init()
    
    # Instantiate the servo node only
    servo_node = ServoPublisher()
    
    # ---------- Load YOLO face model ----------
    model_path = hf_hub_download(
        repo_id="AdamCodd/YOLOv11n-face-detection",
        filename="model.pt"
    )
    model = YOLO(model_path)

    # Servo limits
    servo_min = 0
    servo_max = 180
    neutral_angle = 90.0

    # Camera FOV (degrees)
    camera_fov = 80

    # PID gains – initially zero
    pid = PID(kp=0.0, ki=0.0, kd=0.0)
    selected = 0  # 0=Kp, 1=Ki, 2=Kd

    last_time = time.time()

    print("Face tracking started. Servo only (neck removed).")
    print("Keyboard controls (focus the OpenCV window):")
    print("  1, 2, 3  : select Kp, Ki, or Kd")
    print("  + (or =) : increase selected gain")
    print("  -         : decrease selected gain")
    print("  r         : reset integral term")
    print("  q         : quit")

    # ---------- Main loop: spin servo node and process frames ----------
    while rclpy.ok():
        # Let the servo node process its callbacks (non‑blocking)
        rclpy.spin_once(servo_node, timeout_sec=0.0)

        # If no frame is available yet, wait a bit and continue
        if not servo_node.frame_available:
            time.sleep(0.01)
            continue

        # Get a copy of the latest frame
        frame = servo_node.latest_frame.copy()
        h, w, _ = frame.shape
        image_center_x = w // 2

        # Run YOLO face detection
        results = model(frame, conf=0.5, verbose=False)
        face_found = False

        for r in results:
            for box in r.boxes:
                face_found = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center_x = (x1 + x2) // 2

                # Draw rectangle and center marks
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (center_x, h // 2), 5, (0, 0, 255), -1)
                cv2.circle(frame, (image_center_x, h // 2), 5, (255, 0, 0), -1)

                # Compute error
                pixel_error = center_x - image_center_x
                angle_error = pixel_error * (camera_fov / w)

                now = time.time()
                dt = now - last_time
                last_time = now

                # PID update
                correction = pid.update(angle_error, dt)

                # Clamp servo angle
                desired_angle = neutral_angle + correction
                desired_angle = max(servo_min, min(servo_max, desired_angle))

                # Publish to servo
                servo_node.publish_angle(desired_angle)

                # ---------- Display information on frame ----------
                # Highlight selected gain
                if selected == 0:
                    kp_text = f"*Kp={pid.kp:.2f}*"
                    ki_text = f"Ki={pid.ki:.2f}"
                    kd_text = f"Kd={pid.kd:.2f}"
                elif selected == 1:
                    kp_text = f"Kp={pid.kp:.2f}"
                    ki_text = f"*Ki={pid.ki:.2f}*"
                    kd_text = f"Kd={pid.kd:.2f}"
                else:
                    kp_text = f"Kp={pid.kp:.2f}"
                    ki_text = f"Ki={pid.ki:.2f}"
                    kd_text = f"*Kd={pid.kd:.2f}*"

                cv2.putText(frame, f"Err: {angle_error:.2f}°", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Corr: {correction:.2f}°", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Angle: {desired_angle:.1f}°", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, kp_text, (20, 130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255) if selected==0 else (255,255,255), 2)
                cv2.putText(frame, ki_text, (20, 160),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255) if selected==1 else (255,255,255), 2)
                cv2.putText(frame, kd_text, (20, 190),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255) if selected==2 else (255,255,255), 2)

                print(f"Err:{angle_error:.2f} Corr:{correction:.2f} Ang:{desired_angle:.1f}  Kp={pid.kp:.2f} Ki={pid.ki:.2f} Kd={pid.kd:.2f}")
                break  # only process first face
            if face_found:
                break

        if not face_found:
            pid.reset_integral()

        # Show frame and handle keyboard input
        cv2.imshow("Face Tracking", frame)
        key = cv2.waitKey(1) & 0xFF

        # ----- Keyboard tuning -----
        if key == ord('q'):
            break
        elif key == ord('1'):
            selected = 0
            print("Selected: Kp")
        elif key == ord('2'):
            selected = 1
            print("Selected: Ki")
        elif key == ord('3'):
            selected = 2
            print("Selected: Kd")
        elif key == ord('+') or key == ord('='):
            if selected == 0:
                pid.kp += 0.1
                print(f"Kp increased to {pid.kp:.2f}")
            elif selected == 1:
                pid.ki += 0.01
                print(f"Ki increased to {pid.ki:.2f}")
            else:
                pid.kd += 0.1
                print(f"Kd increased to {pid.kd:.2f}")
        elif key == ord('-'):
            if selected == 0:
                pid.kp = max(0.0, pid.kp - 0.1)
                print(f"Kp decreased to {pid.kp:.2f}")
            elif selected == 1:
                pid.ki = max(0.0, pid.ki - 0.01)
                print(f"Ki decreased to {pid.ki:.2f}")
            else:
                pid.kd = max(0.0, pid.kd - 0.1)
                print(f"Kd decreased to {pid.kd:.2f}")
        elif key == ord('r'):
            pid.reset_integral()
            print("Integral reset.")

    # Cleanup
    cv2.destroyAllWindows()
    servo_node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()