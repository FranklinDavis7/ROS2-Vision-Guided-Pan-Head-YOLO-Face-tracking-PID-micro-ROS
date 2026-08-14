# ROS2-Vision-Guided-Pan-Head-YOLO-Face-tracking-PID-micro-ROS

A ROS 2 based vision-guided pan-head project combining **Gazebo, YOLO face detection, PID control, and ESP32/micro-ROS**.

The project demonstrates vision-based tracking of a rotating human-head model in Gazebo. A camera positioned in front of the head captures the head as it rotates. The camera image is published through a ROS 2 camera topic and processed by the face-tracking system.

`Servo_face.py` detects the face using YOLO, calculates the face position, and uses a PID controller to generate servo-angle commands. These commands are published to the `/servo_angle` topic and can be used to control a physical servo through an ESP32 and micro-ROS.

The `Neck_con.py` script rotates the head model in Gazebo to provide a moving target for the face-tracking system.

---

# Project Overview

The project contains two ROS 2 packages:

## `single_camera`

This package contains the **Gazebo simulation environment**.

It includes:

* Human head STL model
* Neck/head joint
* Camera positioned in front of the head
* Camera configuration
* URDF/Xacro files
* Gazebo world
* RViz configurations
* Gazebo launch file

The main launch file is:

```text
single_camera/launch/head.launch.xml
```

Launching this file starts the Gazebo environment containing the human-head model and camera.

The camera captures the head as it rotates and publishes the camera image through a ROS 2 topic.

---

## `camera_stream`

This package contains the **face detection, tracking, and PID control system**.

It includes:

* YOLO face detection
* Face position calculation
* PID controller
* Servo-angle generation
* ROS 2 camera subscription
* `/servo_angle` publishing
* ESP32/micro-ROS integration

Important scripts include:

```text
Servo_face.py
Neck_con.py
face_detection.py
face_centroid.py
```

---

# System Architecture

The overall system works as follows:

```text
                         GAZEBO
        ┌────────────────────────────────┐
        │                                │
        │       Human Head STL           │
        │             ▲                  │
        │             │                  │
        │        Head Joint              │
        │             ▲                  │
        │             │                  │
        │        Neck_con.py             │
        │                                │
        │             │                  │
        │             ▼                  │
        │           Camera               │
        │             │                  │
        └─────────────┼──────────────────┘
                      │
                      │ Camera Image Topic
                      ▼
              ┌─────────────────┐
              │  Servo_face.py  │
              └────────┬────────┘
                       │
                       ▼
                YOLO Face Detection
                       │
                       ▼
                  Face Position
                       │
                       ▼
                  PID Controller
                       │
                       ▼
                  /servo_angle
                       │
                       ▼
                     ESP32
                       │
                       ▼
                Physical Servo
```

The head model is rotated in Gazebo to provide a moving face for the vision system to track.

---

# Requirements

* Ubuntu
* ROS 2
* Gazebo
* Python 3
* OpenCV
* YOLO
* ESP32
* micro-ROS

---

# Installation

Clone the repository into your ROS 2 workspace:

```bash
cd ~/your_ros2_workspace/src

git clone https://github.com/YOUR_USERNAME/ROS2-Vision-Guided-Pan-Head-YOLO-Face-tracking-PID-micro-ROS.git
```

Go to the workspace:

```bash
cd ~/your_ros2_workspace
```

Install dependencies:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

Build the workspace:

```bash
colcon build --symlink-install
```

Source the workspace:

```bash
source install/setup.bash
```

---

# Running the Gazebo Simulation

## Step 1 — Launch Gazebo

Open a terminal and run:

```bash
source /opt/ros/jazzy/setup.bash
source ~/your_ros2_workspace/install/setup.bash

ros2 launch single_camera head.launch.xml
```

This launches the Gazebo environment containing:

* Human head STL model
* Head/neck joint
* Camera positioned in front of the head
* Gazebo world

The camera publishes the image through a ROS 2 camera topic.

---

# Step 2 — Rotate the Head Model

Open another terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/your_ros2_workspace/install/setup.bash
```

Run:

```bash
ros2 run camera_stream Neck_con.py
```

`Neck_con.py` controls the head joint in Gazebo and rotates the human-head model.

The rotating head provides a moving target for the face-tracking system.

---

# Step 3 — Start Face Tracking

Open another terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/your_ros2_workspace/install/setup.bash
```

Run:

```bash
ros2 run camera_stream Servo_face.py
```

`Servo_face.py` subscribes to the Gazebo camera image topic.

The camera observes the rotating human head and provides the image to the YOLO face-detection system.

The processing pipeline is:

```text
Gazebo Camera
      ↓
Camera Image Topic
      ↓
Servo_face.py
      ↓
YOLO Face Detection
      ↓
Face Position
      ↓
PID Controller
      ↓
/servo_angle
```

---

# Camera Topic

The camera used by the face-tracking system is the camera inside the Gazebo simulation.

To find the available camera topics, run:

```bash
ros2 topic list
```

Look for the camera image topic configured in `single_camera`.

For example:

```text
/camera/image_raw
```

The topic used by `Servo_face.py` must match the camera topic configured in the Gazebo simulation.

---

# PID Controller

The face-tracking system uses a PID controller to calculate the required servo-angle command.

The PID parameters are:

```text
Kp = Proportional gain
Ki = Integral gain
Kd = Derivative gain
```

The controller calculates the error between the detected face position and the desired position in the camera image.

```text
Face Position
      ↓
Calculate Error
      ↓
PID Controller
      ↓
Servo Angle
```

---

# Real-Time PID Adjustment

The PID values can be adjusted directly from the **face-tracking window** while `Servo_face.py` is running.

Make sure the face-tracking window has keyboard focus.

### Select Kp

Press:

```text
1
```

### Select Ki

Press:

```text
2
```

### Select Kd

Press:

```text
3
```

### Adjust the selected parameter

Press:

```text
+    Increase value
-    Decrease value
```

For example:

```text
1
+
+
-
```

selects `Kp` and adjusts its value.

Similarly:

```text
2
+
```

selects and increases `Ki`.

And:

```text
3
-
```

selects and decreases `Kd`.

The selected PID parameter and its current value are displayed in the face-tracking window.

This allows PID tuning while the tracking system is running.

---

# `/servo_angle` Topic

The PID controller publishes the calculated servo-angle commands to:

```text
/servo_angle
```

You can monitor the published values with:

```bash
ros2 topic echo /servo_angle
```

Check the topic information with:

```bash
ros2 topic info /servo_angle
```

---

# ESP32 + micro-ROS

The `/servo_angle` topic can be used to control a physical servo connected to an ESP32.

Connect the ESP32 to the computer and start the micro-ROS agent.

For example:

```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```

Check the connected serial device if required:

```bash
ls /dev/ttyUSB*
```

or:

```bash
ls /dev/ttyACM*
```

The physical control pipeline is:

```text
Servo_face.py
      ↓
PID Controller
      ↓
/servo_angle
      ↓
micro-ROS Agent
      ↓
ESP32
      ↓
Physical Servo
```

---

# Complete Demonstration

The complete demonstration consists of the following process:

```text
                 Gazebo
                   │
                   ▼
            Human Head Model
                   │
             Head Rotation
                   │
                   ▼
              Gazebo Camera
                   │
                   │ Camera Image
                   ▼
             Servo_face.py
                   │
                   ▼
            YOLO Face Detection
                   │
                   ▼
             Face Position
                   │
                   ▼
             PID Controller
                   │
                   ▼
              /servo_angle
                   │
                   ▼
                 ESP32
                   │
                   ▼
            Physical Servo
```

`Neck_con.py` is used to rotate the simulated human head, while `Servo_face.py` observes the head through the Gazebo camera and calculates the servo-angle commands.

---

# Running Order

## Terminal 1 — Launch Gazebo

```bash
source /opt/ros/jazzy/setup.bash
source ~/your_ros2_workspace/install/setup.bash

ros2 launch single_camera head.launch.xml
```

## Terminal 2 — Rotate the Head

```bash
source /opt/ros/jazzy/setup.bash
source ~/your_ros2_workspace/install/setup.bash

ros2 run camera_stream Neck_con.py
```

## Terminal 3 — Start Face Tracking

```bash
source /opt/ros/jazzy/setup.bash
source ~/your_ros2_workspace/install/setup.bash

ros2 run camera_stream Servo_face.py
```

## Terminal 4 — Start micro-ROS Agent

Only when using the physical ESP32:

```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```

---

# ROS 2 Package Structure

```text
ROS2-Vision-Guided-Pan-Head-YOLO-Face-tracking-PID-micro-ROS/
│
└── src/
    │
    ├── camera_stream/
    │   ├── camera_stream/
    │   │   ├── Servo_face.py
    │   │   ├── Neck_con.py
    │   │   ├── face_detection.py
    │   │   ├── face_centroid.py
    │   │   └── ...
    │   │
    │   ├── resource/
    │   ├── test/
    │   ├── package.xml
    │   ├── setup.py
    │   └── setup.cfg
    │
    └── single_camera/
        ├── config/
        ├── launch/
        │   └── head.launch.xml
        ├── meshes/
        │   ├── humanhead.stl
        │   ├── NeckV3.stl
        │   └── ...
        ├── rviz/
        ├── urdf/
        ├── world/
        ├── CMakeLists.txt
        └── package.xml
```

---

# Summary

This project demonstrates a **ROS 2 vision-guided pan-head system** using Gazebo, YOLO face detection, PID control, and ESP32/micro-ROS.

A human-head STL model is simulated in Gazebo with a camera positioned in front of it. `Neck_con.py` rotates the head model to create a moving target.

The Gazebo camera captures the rotating head and publishes its images to a ROS 2 camera topic. `Servo_face.py` subscribes to this topic, detects the face using YOLO, calculates the face position, and applies PID control.

The resulting servo-angle commands are published to:

```text
/servo_angle
```

These commands can be used by an ESP32 through micro-ROS to control a physical servo.

The overall concept is:

```text
Rotating Gazebo Head
        ↓
    Gazebo Camera
        ↓
   ROS 2 Image Topic
        ↓
  YOLO Face Detection
        ↓
   Face Position Error
        ↓
    PID Controller
        ↓
    /servo_angle
        ↓
      ESP32
        ↓
   Physical Servo
```

---

# Author

**Franklin Davis**
