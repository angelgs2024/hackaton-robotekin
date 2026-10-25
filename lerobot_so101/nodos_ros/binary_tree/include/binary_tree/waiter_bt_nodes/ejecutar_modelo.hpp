#pragma once

#include <chrono>
#include <string>
#include <sys/types.h>
#include <behaviortree_cpp/action_node.h>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

// Supervisa un proceso sin bloquear el tick del árbol; SUCCESS solo al finalizar.
class EjecutarModelo : public BT::StatefulActionNode
{
public:
  EjecutarModelo(const std::string & name, const BT::NodeConfig & config,
    rclcpp::Node::SharedPtr node, bool validate_only = false);
  ~EjecutarModelo() override;
  static BT::PortsList providedPorts();
  BT::NodeStatus onStart() override;
  BT::NodeStatus onRunning() override;
  void onHalted() override;

private:
  void stopProcess();
  void report(const std::string & message);
  rclcpp::Node::SharedPtr node_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  bool validate_only_;
  pid_t pid_ = -1;
  std::string label_;
  std::chrono::steady_clock::time_point started_;
  double timeout_ = 300.0;
};
