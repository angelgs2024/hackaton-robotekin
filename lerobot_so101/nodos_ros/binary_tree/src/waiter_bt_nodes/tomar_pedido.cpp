#include "binary_tree/waiter_bt_nodes/tomar_pedido.hpp"

#include <cmath>
#include <utility>

TomarPedido::TomarPedido(const std::string & name, const BT::NodeConfig & config,
  rclcpp::Node::SharedPtr node)
: BT::StatefulActionNode(name, config), node_(std::move(node))
{
  if (!node_->has_parameter("interface_mode")) {
    node_->declare_parameter<bool>("interface_mode", false);
  }
  empezar_ = node_->create_publisher<std_msgs::msg::Empty>("/hri/empezar", 10);
  // Volatile: do not receive the retained order from a previous conversation.
  pedido_sub_ = node_->create_subscription<std_msgs::msg::String>(
    "/hri/pedido", rclcpp::QoS(10).durability_volatile(),
    [this](std_msgs::msg::String::ConstSharedPtr msg) {
      if (activo_ && enviado_) {
        pedido_ = msg->data;
      }
    });
}

BT::PortsList TomarPedido::providedPorts()
{
  return {
    BT::InputPort<double>("timeout", 120.0, "Maximum conversation time in seconds"),
    BT::OutputPort<std::string>("comida"),
    BT::OutputPort<std::string>("bebida"),
    BT::OutputPort<std::string>("pedido")
  };
}

BT::NodeStatus TomarPedido::onStart()
{
  activo_ = false;
  enviado_ = false;
  pedido_.clear();
  setOutput("comida", std::string{});
  setOutput("bebida", std::string{});
  setOutput("pedido", std::string{});
  auto timeout = getInput<double>("timeout");
  if (!timeout || !std::isfinite(timeout.value()) || timeout.value() <= 0.0) {
    RCLCPP_ERROR(node_->get_logger(), "TomarPedido requires a positive timeout");
    return BT::NodeStatus::FAILURE;
  }
  timeout_ = timeout.value();
  inicio_ = std::chrono::steady_clock::now();
  activo_ = true;
  return BT::NodeStatus::RUNNING;
}

BT::NodeStatus TomarPedido::onRunning()
{
  if (std::chrono::duration<double>(std::chrono::steady_clock::now() - inicio_).count()
    >= timeout_)
  {
    activo_ = false;
    RCLCPP_ERROR(node_->get_logger(), "Timeout waiting for a confirmed HRI order");
    return BT::NodeStatus::FAILURE;
  }

  const bool interface_mode = node_->get_parameter("interface_mode").as_bool();
  // Voice mode also includes the GUI subscribers; they must not stand in for
  // pregunta/escucha while the audio models are still loading.
  const bool input_ready = interface_mode ? empezar_->get_subscription_count() >= 1 :
    (empezar_->get_subscription_count() >= 3 &&
    node_->count_subscribers("/hri/escuchar") >= 2 &&
    node_->count_subscribers("/hri/oido") > 0);
  if (!enviado_ && input_ready && pedido_sub_->get_publisher_count() > 0)
  {
    enviado_ = true;
    empezar_->publish(std_msgs::msg::Empty{});
  }

  if (pedido_.empty()) {
    return BT::NodeStatus::RUNNING;
  }
  activo_ = false;
  const auto comma = pedido_.find(',');
  if (comma == std::string::npos || comma == 0 || comma + 1 == pedido_.size() ||
    pedido_.find(',', comma + 1) != std::string::npos)
  {
    RCLCPP_ERROR(node_->get_logger(), "Invalid order: '%s'", pedido_.c_str());
    return BT::NodeStatus::FAILURE;
  }
  setOutput("comida", pedido_.substr(0, comma));
  setOutput("bebida", pedido_.substr(comma + 1));
  setOutput("pedido", pedido_);
  RCLCPP_INFO(node_->get_logger(), "Order saved to blackboard: %s", pedido_.c_str());
  return BT::NodeStatus::SUCCESS;
}

void TomarPedido::onHalted()
{
  activo_ = false;
  enviado_ = false;
  pedido_.clear();
}
