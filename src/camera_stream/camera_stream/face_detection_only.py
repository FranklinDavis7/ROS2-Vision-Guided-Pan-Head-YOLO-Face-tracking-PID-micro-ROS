import cv2
from ultralytics import YOLO

def main():
    # 1. Load the YOLO face model
    model = YOLO("/microros_ws/ros2_ws/src/camera_stream/resource/yolov8n-face.pt")

    # 2. Open the camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Error: Camera not found")
        return

    print("Press 'q' to quit")

    while True:
        # 3. Read a frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # 4. Run face detection (confidence threshold 0.5)
        results = model(frame, conf=0.5, verbose=False)

        # 5. Draw bounding boxes and centers
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # 6. Show the output
        cv2.imshow("Face Detection", frame)

        # 7. Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 8. Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()