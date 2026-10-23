#include <gtest/gtest.h>
#include <behaviortree_cpp/bt_factory.h>
#include <thread>
#include "binary_tree/waiter_bt_nodes/tomar_pedido.hpp"

using namespace std::chrono_literals;

class PedidoTest : public testing::Test
{
protected:
  static void SetUpTestSuite() { rclcpp::init(0, nullptr); }
  static void TearDownTestSuite() { rclcpp::shutdown(); }

  void SetUp() override
  {
    node = std::make_shared<rclcpp::Node>("test_tomar_pedido");
    pedido_pub = node->create_publisher<std_msgs::msg::String>(
      "/hri/pedido", rclcpp::QoS(1).transient_local());
    start_sub = node->create_subscription<std_msgs::msg::Empty>(
      "/hri/empezar", 10, [this](std_msgs::msg::Empty::ConstSharedPtr) { ++starts; });
    reset_sub = node->create_subscription<std_msgs::msg::Empty>(
      "/hri/empezar", 10, [](std_msgs::msg::Empty::ConstSharedPtr) {});
    listen_sub = node->create_subscription<std_msgs::msg::Empty>(
      "/hri/escuchar", 10, [](std_msgs::msg::Empty::ConstSharedPtr) {});
    heard_sub = node->create_subscription<std_msgs::msg::String>(
      "/hri/oido", 10, [](std_msgs::msg::String::ConstSharedPtr) {});
    factory.registerBuilder<TomarPedido>("TomarPedido",
      [this](const std::string & name, const BT::NodeConfig & config) {
        return std::make_unique<TomarPedido>(name, config, node);
      });
  }

  BT::Tree makeTree(double timeout = 3.0)
  {
    return factory.createTreeFromText(
      "<root BTCPP_format=\"4\"><BehaviorTree ID=\"Test\">"
      "<TomarPedido comida=\"{food_order}\" bebida=\"{drink_order}\" "
      "pedido=\"{order}\" timeout=\"" + std::to_string(timeout) + "\"/>"
      "</BehaviorTree></root>");
  }

  BT::NodeStatus tick(BT::Tree & tree)
  {
    rclcpp::spin_some(node);
    return tree.tickOnce();
  }

  bool waitForStart(BT::Tree & tree)
  {
    const auto deadline = std::chrono::steady_clock::now() + 2s;
    while (std::chrono::steady_clock::now() < deadline && starts == 0) {
      if (tick(tree) != BT::NodeStatus::RUNNING) { return false; }
      std::this_thread::sleep_for(10ms);
    }
    return starts == 1;
  }

  BT::NodeStatus result(BT::Tree & tree)
  {
    const auto deadline = std::chrono::steady_clock::now() + 4s;
    while (std::chrono::steady_clock::now() < deadline) {
      const auto status = tick(tree);
      if (status != BT::NodeStatus::RUNNING) { return status; }
      std::this_thread::sleep_for(10ms);
    }
    return BT::NodeStatus::RUNNING;
  }

  void publish(const std::string & text)
  {
    std_msgs::msg::String msg;
    msg.data = text;
    pedido_pub->publish(msg);
  }

  rclcpp::Node::SharedPtr node;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pedido_pub;
  rclcpp::Subscription<std_msgs::msg::Empty>::SharedPtr start_sub, reset_sub, listen_sub;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr heard_sub;
  BT::BehaviorTreeFactory factory;
  int starts = 0;
};

TEST_F(PedidoTest, ConfirmedOrderPopulatesBlackboard)
{
  auto tree = makeTree();
  ASSERT_TRUE(waitForStart(tree));
  publish("chuleton,agua");
  ASSERT_EQ(result(tree), BT::NodeStatus::SUCCESS);
  auto bb = tree.rootBlackboard();
  EXPECT_EQ(bb->get<std::string>("food_order"), "chuleton");
  EXPECT_EQ(bb->get<std::string>("drink_order"), "agua");
  EXPECT_EQ(bb->get<std::string>("order"), "chuleton,agua");
  EXPECT_EQ(starts, 1);
}

TEST_F(PedidoTest, MalformedOrderFailsWithoutOutputs)
{
  auto tree = makeTree();
  ASSERT_TRUE(waitForStart(tree));
  publish("chuleton,agua,extra");
  EXPECT_EQ(result(tree), BT::NodeStatus::FAILURE);
  EXPECT_EQ(tree.rootBlackboard()->get<std::string>("order"), "");
}

TEST_F(PedidoTest, MissingHriTimesOutAndClearsPreviousOrder)
{
  listen_sub.reset();
  auto tree = makeTree(0.1);
  tree.rootBlackboard()->set("order", std::string("old,order"));
  EXPECT_EQ(result(tree), BT::NodeStatus::FAILURE);
  EXPECT_EQ(starts, 0);
  EXPECT_EQ(tree.rootBlackboard()->get<std::string>("order"), "");
}

TEST_F(PedidoTest, RetainedOrderDoesNotCompleteNewConversation)
{
  publish("merluza,cocacola");
  auto tree = makeTree(0.5);
  ASSERT_TRUE(waitForStart(tree));
  EXPECT_EQ(result(tree), BT::NodeStatus::FAILURE);
  EXPECT_EQ(tree.rootBlackboard()->get<std::string>("food_order"), "");
}

TEST_F(PedidoTest, HaltDiscardsPendingOrder)
{
  auto tree = makeTree();
  ASSERT_TRUE(waitForStart(tree));
  tree.haltTree();
  publish("merluza,cocacola");
  for (int i = 0; i < 10; ++i) {
    rclcpp::spin_some(node);
    std::this_thread::sleep_for(10ms);
  }
  starts = 0;
  ASSERT_TRUE(waitForStart(tree));
  publish("chuleton,agua");
  EXPECT_EQ(result(tree), BT::NodeStatus::SUCCESS);
  EXPECT_EQ(tree.rootBlackboard()->get<std::string>("order"), "chuleton,agua");
}
