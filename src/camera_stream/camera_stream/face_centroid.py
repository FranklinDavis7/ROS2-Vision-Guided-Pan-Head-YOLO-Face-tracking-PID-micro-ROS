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
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # 3. Face detection
        results = model(frame, conf=0.5, verbose=False)

        # 4. Collect centers of all detected faces
        centers = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                centers.append((cx, cy))

                # Draw each face bounding box and its center
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # 5. Compute and draw the centroid of all faces (if any)
        if centers:
            # Average all center coordinates
            avg_x = int(sum(c[0] for c in centers) / len(centers))
            avg_y = int(sum(c[1] for c in centers) / len(centers))

            # Draw a bigger, distinct marker for the centroid
            cv2.circle(frame, (avg_x, avg_y), 10, (255, 0, 0), -1)           # filled blue circle
            cv2.putText(frame, f"Centroid: ({avg_x}, {avg_y})", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (255, 255, 0), 2)
        else:
            cv2.putText(frame, "No faces detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 6. Show output
        cv2.imshow("Face Detection with Centroid", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()