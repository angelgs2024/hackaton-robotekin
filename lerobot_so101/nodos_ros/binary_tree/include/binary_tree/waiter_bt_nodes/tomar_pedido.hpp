#pragma once

#include <chrono>
#include <string>
#include <behaviortree_cpp/action_node.h>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/empty.hpp>
#include <std_msgs/msg/string.hpp>

// Callbacks and ticks run on the same executor thread in waiter_behavior.cpp.
class TomarPedido : public BT::StatefulActionNode
{
public:
  TomarPedido(const std::string & name, const BT::NodeConfig & config,
    rclcpp::Node::SharedPtr node);
  static BT::PortsList providedPorts();
  BT::NodeStatus onStart() override;
  BT::NodeStatus onRunning() override;
  void onHalted() override;

private:
  rclcpp::Node::SharedPtr node_;
  rclcpp::Publisher<std_msgs::msg::Empty>::SharedPtr empezar_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr pedido_sub_;
  std::chrono::steady_clock::time_point inicio_;
  double timeout_ = 120.0;
  bool activo_ = false;
  bool enviado_ = false;
  std::string pedido_;
};
