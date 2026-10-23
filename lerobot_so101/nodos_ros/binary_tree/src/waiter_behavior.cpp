// Copyright 2025 Intelligent Robotics Lab
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <rclcpp/rclcpp.hpp>
#include <behaviortree_cpp/bt_factory.h>
#include <behaviortree_cpp/loggers/bt_cout_logger.h>
#include <ament_index_cpp/get_package_share_directory.hpp>

#include "binary_tree/waiter_bt_nodes/bt_node_registration.hpp"

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("waiter_behavior_bt");

  // Factory para registrar nodos personalizados
  BT::BehaviorTreeFactory factory;

  // Registrar las acciones del árbol
  register_bt_nodes(factory, node);

  // Obtener path al archivo XML
  std::string package_share_dir = ament_index_cpp::get_package_share_directory("binary_tree");
  std::string tree_path = node->declare_parameter<std::string>(
    "tree_file", package_share_dir + "/config/waiter_behavior_tree.xml");

  for (auto & manifest : factory.manifests()) {
    RCLCPP_INFO(node->get_logger(), "Registered: %s", manifest.first.c_str());
  }

  // Cargar árbol desde XML
  auto tree = factory.createTreeFromFile(tree_path);

  // Logger para depuración
  BT::StdCoutLogger logger(tree);

  RCLCPP_INFO(node->get_logger(), "HRI behavior tree started");
  RCLCPP_INFO(node->get_logger(),
    "Waiting for HRI to take a confirmed order and save it to the blackboard");

  // Bucle principal: tick del árbol a 10 Hz
  rclcpp::Rate rate(10);
  BT::NodeStatus status = BT::NodeStatus::IDLE;

  while (rclcpp::ok()) {
    // Procesar el pedido recibido antes de evaluar el árbol
    rclcpp::spin_some(node);

    // Evaluar árbol
    status = tree.tickOnce();

    if (status == BT::NodeStatus::RUNNING) {
      // El árbol todavía está ejecutándose
      rate.sleep();
    } else if (status == BT::NodeStatus::SUCCESS) {
      RCLCPP_INFO(node->get_logger(), "Interaction completed successfully!");
      break;
    } else if (status == BT::NodeStatus::FAILURE) {
      RCLCPP_ERROR(node->get_logger(), "Interaction failed");
      break;
    }
  }

  rclcpp::shutdown();
  return status == BT::NodeStatus::SUCCESS ? 0 : 1;
}
