#include <micro_ros_arduino.h>

#include <rcl/rcl.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <std_msgs/msg/float64.h>

#include <ESP32Servo.h>

Servo servo;

// ----------------------------
// Servo Settings
// ----------------------------
const int SERVO_PIN = 13;

float target_angle = 90.0;
float current_angle = 90.0;

// degrees moved every update
const float STEP = 1.0;

// ----------------------------
// micro-ROS
// ----------------------------
rcl_subscription_t subscriber;
std_msgs__msg__Float64 msg;

rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;

// ----------------------------

void subscription_callback(const void *msgin)
{
    const std_msgs__msg__Float64 *m =
        (const std_msgs__msg__Float64 *)msgin;

    target_angle = m->data;

    if (target_angle < 0.0)
        target_angle = 0.0;

    if (target_angle > 180.0)
        target_angle = 180.0;
}

// ----------------------------

void setup()
{
    Serial.begin(115200);

    set_microros_transports();

    servo.setPeriodHertz(50);
    servo.attach(SERVO_PIN, 500, 2400);

    servo.write(current_angle);

    delay(2000);

    allocator = rcl_get_default_allocator();

    rclc_support_init(
        &support,
        0,
        NULL,
        &allocator);

    rclc_node_init_default(
        &node,
        "esp32_servo_node",
        "",
        &support);

    rclc_subscription_init_default(
        &subscriber,
        &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(
            std_msgs,
            msg,
            Float64),
        "/servo_angle");

    rclc_executor_init(
        &executor,
        &support.context,
        1,
        &allocator);

    rclc_executor_add_subscription(
        &executor,
        &subscriber,
        &msg,
        &subscription_callback,
        ON_NEW_DATA);
}

// ----------------------------

void loop()
{
    rclc_executor_spin_some(
        &executor,
        RCL_MS_TO_NS(10));

    if (current_angle < target_angle)
    {
        current_angle += STEP;

        if (current_angle > target_angle)
            current_angle = target_angle;

        servo.write(current_angle);
    }
    else if (current_angle > target_angle)
    {
        current_angle -= STEP;

        if (current_angle < target_angle)
            current_angle = target_angle;

        servo.write(current_angle);
    }

    delay(10);
}
