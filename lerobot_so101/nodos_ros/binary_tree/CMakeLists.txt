cmake_minimum_required(VERSION 3.20)
project(binary_tree)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(behaviortree_cpp REQUIRED)

# Include directories
include_directories(include)

# BT node implementations library
add_library(waiter_bt_nodes SHARED
  src/waiter_bt_nodes/tomar_pedido.cpp
  src/waiter_bt_nodes/bt_node_registration.cpp
)

ament_target_dependencies(waiter_bt_nodes
  rclcpp
  std_msgs
  behaviortree_cpp
)

# Waiter behavior with local HRI
add_executable(waiter_behavior_bt src/waiter_behavior.cpp)
target_link_libraries(waiter_behavior_bt waiter_bt_nodes)
ament_target_dependencies(waiter_behavior_bt
  rclcpp
  ament_index_cpp
  behaviortree_cpp
)

install(TARGETS waiter_bt_nodes waiter_behavior_bt
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

# Python HRI is part of this ROS package.
ament_python_install_package(binary_tree_hri PACKAGE_DIR hri)
foreach(hri_node pregunta escucha confirma)
  # With --symlink-install ROS executes this generated file directly, so it
  # needs executable permissions before install(PROGRAMS) creates the link.
  configure_file(scripts/hri_node.in ${CMAKE_CURRENT_BINARY_DIR}/${hri_node}
    @ONLY
    FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
                     GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
  install(PROGRAMS ${CMAKE_CURRENT_BINARY_DIR}/${hri_node}
    DESTINATION lib/${PROJECT_NAME})
endforeach()

# Models can travel with the package, or be supplied as absolute launch arguments.
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/models")
  install(DIRECTORY models DESTINATION share/${PROJECT_NAME})
endif()

# Install config files
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_tomar_pedido
    test/test_tomar_pedido.cpp
    src/waiter_bt_nodes/tomar_pedido.cpp)
  ament_target_dependencies(test_tomar_pedido rclcpp std_msgs behaviortree_cpp)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  # set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
