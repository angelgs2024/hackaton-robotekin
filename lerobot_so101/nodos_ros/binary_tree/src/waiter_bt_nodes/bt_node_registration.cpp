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

#include "binary_tree/waiter_bt_nodes/bt_node_registration.hpp"
#include "binary_tree/waiter_bt_nodes/tomar_pedido.hpp"
#include "binary_tree/waiter_bt_nodes/ejecutar_modelo.hpp"

void register_bt_nodes(
  BT::BehaviorTreeFactory & factory,
  rclcpp::Node::SharedPtr node)
{

  factory.registerBuilder<TomarPedido>(
    "TomarPedido",
    [node](const std::string & name, const BT::NodeConfig & config) {
      return std::make_unique<TomarPedido>(name, config, node);
    });
  factory.registerBuilder<EjecutarModelo>(
    "PrepararModelos",
    [node](const std::string & name, const BT::NodeConfig & config) {
      return std::make_unique<EjecutarModelo>(name, config, node, true);
    });
  factory.registerBuilder<EjecutarModelo>(
    "EjecutarModelo",
    [node](const std::string & name, const BT::NodeConfig & config) {
      return std::make_unique<EjecutarModelo>(name, config, node);
    });
}
