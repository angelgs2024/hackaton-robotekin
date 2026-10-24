"""Prueba ROS real desde entrada HRI/clics hasta el ejecutable del árbol."""
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from ament_index_python.packages import get_package_prefix
from PyQt6.QtWidgets import QApplication
from std_msgs.msg import Empty, String

from binary_tree_gui.ros_bridge import HriBridge
from binary_tree_hri.confirma import Confirma

app = QApplication.instance() or QApplication(['test_hri_bridge'])


class TestHriBridge(unittest.TestCase):
    def setUp(self):
        rclpy.init()
        self.executor = SingleThreadedExecutor()
        self.nodes = []
        self.bt = None
        self.output = tempfile.TemporaryFile(mode='w+')

    def tearDown(self):
        if self.bt is not None and self.bt.poll() is None:
            self.bt.terminate()
            try:
                self.bt.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.bt.kill()
                self.bt.wait(timeout=5)
        for node in reversed(self.nodes):
            if isinstance(node, HriBridge):
                node.window.close()
            self.executor.remove_node(node)
            node.destroy_node()
        self.executor.shutdown()
        rclpy.shutdown()
        self.output.close()

    def add(self, node):
        self.nodes.append(node)
        self.executor.add_node(node)
        return node

    def wait_for(self, predicate, timeout=8):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            self.executor.spin_once(timeout_sec=0.01)
            app.processEvents()
            if predicate():
                return
        self.fail('Tiempo agotado esperando el resultado ROS')

    def start_tree(self, interface):
        executable = Path(get_package_prefix('binary_tree')) / 'lib/binary_tree/waiter_behavior_bt'
        self.bt = subprocess.Popen(
            [str(executable), '--ros-args', '-p', f'interface_mode:={str(interface).lower()}'],
            stdout=self.output, stderr=subprocess.STDOUT,
        )

    def assert_saved(self, order):
        self.wait_for(lambda: self.bt.poll() is not None)
        self.output.seek(0)
        output = self.output.read()
        self.assertEqual(self.bt.returncode, 0, output)
        self.assertIn(f'Order saved to blackboard: {order}', output)

    def test_buttons_publish_only_complete_confirmed_order_to_tree(self):
        bridge = self.add(HriBridge(interface_mode=True))
        self.start_tree(interface=True)
        self.wait_for(lambda: bridge.active)
        window = bridge.window
        window.btn_order.click()
        self.assertIsNone(self.bt.poll())
        window.menu_widget._on_item_clicked(window.menu_widget.cards['sopa'])
        window.btn_order.click()
        self.assertTrue(bridge.active)
        self.assertFalse(window.btn_order.isEnabled())
        window.menu_widget._on_item_clicked(window.menu_widget.cards['cocacola'])
        self.assertTrue(window.btn_order.isEnabled())
        window.btn_order.click()
        self.assert_saved('sopa,cocacola')
        self.assertFalse(bridge.active)
        self.assertEqual(window.table_widget.drink.drink_id, 'cocacola')

    def test_voice_previews_rejection_and_yes_confirmation_to_tree(self):
        bridge = self.add(HriBridge(interface_mode=False))
        confirms = self.add(Confirma())
        # Sustituye solo el hardware de audio: la interpretación, ROS y BT son reales.
        audio = self.add(Node('test_audio'))
        audio.create_subscription(Empty, '/hri/empezar', lambda _: None, 10)
        audio.create_subscription(Empty, '/hri/escuchar', lambda _: None, 10)
        heard = audio.create_publisher(String, '/hri/oido', 10)
        self.start_tree(interface=False)
        self.wait_for(lambda: bridge.active and heard.get_subscription_count() >= 2)
        heard.publish(String(data='quiero sopa'))
        self.wait_for(lambda: bridge.window.menu_widget.selected_plato == 'sopa')
        self.assertEqual(bridge.window.menu_widget.selected_bebida, 'vacio')
        self.assertIsNone(self.bt.poll())
        heard.publish(String(data='y coca cola'))
        self.wait_for(lambda: bridge.window.menu_widget.selected_bebida == 'cocacola')
        self.assertFalse(bridge.window.btn_order.isEnabled())
        heard.publish(String(data='no'))
        self.wait_for(lambda: bridge.window.menu_widget.selected_plato == 'vacio')
        heard.publish(String(data='quiero chuletón de vaca y agua'))
        self.wait_for(lambda: bridge.window.menu_widget.selected_plato == 'chuleton')
        self.assertTrue(bridge.window.menu_widget.cards['agua'].is_selected)
        self.assertEqual(bridge.window.table_widget.plate.dish_id, 'chuleton')
        self.assertEqual(bridge.window.table_widget.drink.drink_id, 'agua')
        self.assertIsNone(self.bt.poll())
        heard.publish(String(data='sí'))
        self.wait_for(lambda: not bridge.active)
        self.assert_saved('chuleton,agua')
        self.assertTrue(confirms.terminado)
        self.assertTrue(bridge.window.menu_widget.cards['chuleton'].is_selected)
