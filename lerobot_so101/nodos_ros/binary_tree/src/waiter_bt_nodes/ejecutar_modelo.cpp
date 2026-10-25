#include "binary_tree/waiter_bt_nodes/ejecutar_modelo.hpp"

#include <ament_index_cpp/get_package_prefix.hpp>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <cerrno>
#include <cmath>
#include <csignal>
#include <cstring>
#include <spawn.h>
#include <sys/wait.h>
#include <thread>
#include <utility>
#include <vector>

extern char ** environ;

EjecutarModelo::EjecutarModelo(const std::string & name, const BT::NodeConfig & config,
  rclcpp::Node::SharedPtr node, bool validate_only)
: BT::StatefulActionNode(name, config), node_(std::move(node)), validate_only_(validate_only)
{
  if (!node_->has_parameter("modelos_xml")) {
    node_->declare_parameter<std::string>("modelos_xml",
      ament_index_cpp::get_package_share_directory("binary_tree") + "/config/lerobot_models.xml");
  }
  if (!node_->has_parameter("model_runner")) {
    node_->declare_parameter<std::string>("model_runner",
      ament_index_cpp::get_package_prefix("binary_tree") + "/lib/binary_tree/ejecutar_modelo");
  }
  if (!node_->has_parameter("simular_modelos")) {
    node_->declare_parameter<bool>("simular_modelos", false);
  }
  if (!node_->has_parameter("model_timeout")) {
    node_->declare_parameter<double>("model_timeout", 300.0);
  }
  status_pub_ = node_->create_publisher<std_msgs::msg::String>("/manipulacion/estado", 10);
}

EjecutarModelo::~EjecutarModelo() { stopProcess(); }

BT::PortsList EjecutarModelo::providedPorts()
{
  return {BT::InputPort<std::string>("modelo"), BT::InputPort<std::string>("comida"),
    BT::InputPort<std::string>("bebida")};
}

void EjecutarModelo::report(const std::string & message)
{
  RCLCPP_INFO(node_->get_logger(), "%s", message.c_str());
  if (rclcpp::ok()) {
    std_msgs::msg::String msg;
    msg.data = message;
    status_pub_->publish(msg);
  }
}

BT::NodeStatus EjecutarModelo::onStart()
{
  timeout_ = node_->get_parameter("model_timeout").as_double();
  if (!std::isfinite(timeout_) || timeout_ <= 0) {
    report("Error: model_timeout debe ser positivo");
    return BT::NodeStatus::FAILURE;
  }
  std::vector<std::string> args = {
    node_->get_parameter("model_runner").as_string(), "--config",
    node_->get_parameter("modelos_xml").as_string()};
  if (validate_only_) {
    auto food = getInput<std::string>("comida");
    auto drink = getInput<std::string>("bebida");
    if (!food || !drink) {
      report("Error: falta comida o bebida en la blackboard");
      return BT::NodeStatus::FAILURE;
    }
    args.insert(args.end(), {"--validate-only", "--food", food.value(), "--drink", drink.value()});
    label_ = "configuración de modelos";
  } else {
    auto model = getInput<std::string>("modelo");
    if (!model || model.value().empty()) {
      report("Error: falta el identificador del modelo");
      return BT::NodeStatus::FAILURE;
    }
    label_ = model.value();
    args.insert(args.end(), {"--model", label_});
  }
  const bool simulated = node_->get_parameter("simular_modelos").as_bool();
  if (simulated) { args.emplace_back("--dry-run"); }
  std::vector<char *> argv;
  for (auto & arg : args) { argv.push_back(arg.data()); }
  argv.push_back(nullptr);

  posix_spawnattr_t attributes;
  posix_spawnattr_init(&attributes);
  posix_spawnattr_setflags(&attributes, POSIX_SPAWN_SETPGROUP);
  posix_spawnattr_setpgroup(&attributes, 0);
  const int error = posix_spawn(&pid_, args[0].c_str(), nullptr, &attributes, argv.data(), environ);
  posix_spawnattr_destroy(&attributes);
  if (error != 0) {
    pid_ = -1;
    report("Error al arrancar " + label_ + ": " + std::strerror(error));
    return BT::NodeStatus::FAILURE;
  }
  started_ = std::chrono::steady_clock::now();
  report((simulated ? "Simulación: " : "Ejecutando: ") + label_);
  return BT::NodeStatus::RUNNING;
}

BT::NodeStatus EjecutarModelo::onRunning()
{
  int status = 0;
  const pid_t result = waitpid(pid_, &status, WNOHANG);
  if (result == pid_) {
    pid_ = -1;
    if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
      return BT::NodeStatus::SUCCESS;
    }
    report("Error en " + label_ + "; secuencia detenida (ver terminal)");
    return BT::NodeStatus::FAILURE;
  }
  if (result < 0 && errno != EINTR) {
    stopProcess();
    report("Error al supervisar " + label_);
    return BT::NodeStatus::FAILURE;
  }
  if (std::chrono::duration<double>(std::chrono::steady_clock::now() - started_).count() >= timeout_) {
    stopProcess();
    report("Tiempo agotado en " + label_ + "; secuencia detenida");
    return BT::NodeStatus::FAILURE;
  }
  return BT::NodeStatus::RUNNING;
}

void EjecutarModelo::stopProcess()
{
  if (pid_ <= 0) { return; }
  // El grupo incluye procesos auxiliares de cámaras/inferencia de LeRobot.
  bool reaped = false;
  for (const int signal : {SIGINT, SIGTERM, SIGKILL}) {
    kill(-pid_, signal);
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(1);
    int status;
    do {
      if (!reaped) {
        const auto result = waitpid(pid_, &status, WNOHANG);
        reaped = result == pid_ || (result < 0 && errno == ECHILD);
      }
      if (reaped && kill(-pid_, 0) < 0 && errno == ESRCH) {
        pid_ = -1;
        return;
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(20));
    } while (std::chrono::steady_clock::now() < deadline);
  }
  int status;
  if (!reaped) {
    while (waitpid(pid_, &status, 0) < 0 && errno == EINTR) {}
  }
  pid_ = -1;
}

void EjecutarModelo::onHalted()
{
  stopProcess();
  report("Secuencia cancelada");
}
