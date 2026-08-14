cmake_minimum_required(VERSION 3.8)

project(single_camera)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    launch
    rviz
    urdf
    meshes
    config
    world
  DESTINATION share/${PROJECT_NAME}
)

ament_package()