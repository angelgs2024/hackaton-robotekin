"""Árbol y procesos reales, sustituyendo únicamente LeRobot por un ejecutor de prueba."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET

import rclpy
from ament_index_python.packages import get_package_prefix, get_package_share_directory
from rclpy.node import Node
from std_msgs.msg import Empty, String


class TestModelSequence(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='lerobot sequence ')
        self.directory = Path(self.temp.name)
        self.trace = self.directory / 'trace.jsonl'
        self.xml = self.directory / 'models.xml'
        self.fake = self.directory / 'fake_policy.py'
        self.fake.write_text('''import json, os, sys, time
model, trace, fail, delay = sys.argv[1:]
def event(name):
    with open(trace, 'a') as stream:
        stream.write(json.dumps([name, model, os.getpid()]) + '\\n')
    with open(trace + '.times', 'a') as stream:
        stream.write(str(time.monotonic()) + '\\n')
event('start')
time.sleep(float(delay))
event('end')
sys.exit(7 if model == fail else 0)
''')
        source = Path(get_package_share_directory('binary_tree')) / 'config/lerobot_models.xml'
        self.catalog = ET.parse(source)
        for model in self.catalog.findall('./models/model'):
            model.set('policy', model.get('id'))
        self.configure()
        rclpy.init()
        self.node = Node('test_model_sequence')
        self.publisher = self.node.create_publisher(String, '/hri/pedido', 10)
        self.node.create_subscription(Empty, '/hri/empezar', self.start_order, 10)
        # Sustituye el nodo de voz, que también debe estar listo en modo botones.
        self.node.create_subscription(Empty, '/hri/empezar', lambda _: None, 10)
        self.process = None
        self.log = tempfile.TemporaryFile(mode='w+')

    def tearDown(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=6)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)
        self.node.destroy_node()
        rclpy.shutdown()
        self.log.close()
        self.temp.cleanup()

    def configure(self, fail='', delay='0.05'):
        command = self.catalog.find('./command')
        command.clear()
        for arg in [sys.executable, str(self.fake), '{policy}', str(self.trace), fail or 'none', delay]:
            ET.SubElement(command, 'arg').text = arg
        self.catalog.write(self.xml)

    def start_order(self, _):
        self.publisher.publish(String(data=self.order))

    def launch_order(self, order, timeout=10.0):
        self.order = order
        self.trace.write_text('')
        Path(str(self.trace) + '.times').write_text('')
        self.launched_at = time.monotonic()
        self.log.seek(0)
        self.log.truncate()
        executable = Path(get_package_prefix('binary_tree')) / 'lib/binary_tree/waiter_behavior_bt'
        self.process = subprocess.Popen([
            str(executable), '--ros-args', '-p', 'interface_mode:=true',
            '-p', f'modelos_xml:={self.xml}', '-p', f'model_timeout:={timeout}',
        ], stdout=self.log, stderr=subprocess.STDOUT)

    def wait_for(self, condition, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.01)
            if condition():
                return
        self.log.seek(0)
        self.fail('Tiempo agotado: ' + self.log.read())

    def events(self):
        return [json.loads(line) for line in self.trace.read_text().splitlines() if line]

    def assert_finished(self, success):
        self.wait_for(lambda: self.process.poll() is not None, timeout=25)
        self.log.seek(0)
        self.assertEqual(self.process.returncode, 0 if success else 1, self.log.read())

    def test_all_orders_run_glass_then_cutlery_without_overlap(self):
        # El pedido tampoco requiere el modelo de cuchillo.
        models = self.catalog.find('./models')
        models.remove(models.find("model[@id='coger_cuchillo']"))
        self.configure()
        for order, expected in (
            ('chuleton,agua', ['coger_vaso_amarillo', 'coger_tenedor']),
            ('chuleton,cocacola', ['coger_vaso_amarillo', 'coger_tenedor']),
            ('sopa,agua', ['coger_vaso_amarillo', 'coger_cuchara']),
            ('sopa,cocacola', ['coger_vaso_amarillo', 'coger_cuchara']),
        ):
            with self.subTest(order=order):
                self.launch_order(order)
                self.assert_finished(True)
                self.assertEqual([(event, model) for event, model, _ in self.events()],
                                 [(event, model) for model in expected for event in ('start', 'end')])
                times = [float(value) for value in Path(str(self.trace) + '.times').read_text().splitlines()]
                self.assertGreaterEqual(times[0] - self.launched_at, 5.0)
                for previous_end, next_start in zip(times[1::2], times[2::2]):
                    self.assertGreaterEqual(next_start - previous_end, 5.0)

    def test_failed_glass_does_not_execute_cutlery(self):
        self.configure(fail='coger_vaso_amarillo')
        self.launch_order('chuleton,agua')
        self.assert_finished(False)
        self.assertEqual([model for event, model, _ in self.events() if event == 'start'],
                         ['coger_vaso_amarillo'])

    def test_missing_last_model_prevents_first_motion(self):
        self.catalog.find("./models/model[@id='coger_tenedor']").set('policy', '')
        self.configure()
        self.launch_order('chuleton,agua')
        self.assert_finished(False)
        self.assertEqual(self.events(), [])

    def test_timeout_stops_running_model_and_remaining_sequence(self):
        self.configure(delay='20')
        self.launch_order('sopa,agua', timeout=0.5)
        self.assert_finished(False)
        events = self.events()
        self.assertEqual([(event, model) for event, model, _ in events], [('start', 'coger_vaso_amarillo')])
        with self.assertRaises(ProcessLookupError):
            os.kill(events[0][2], 0)

    def test_shutdown_stops_current_model(self):
        self.configure(delay='20')
        self.launch_order('chuleton,cocacola')
        self.wait_for(lambda: bool(self.events()))
        pid = self.events()[0][2]
        self.process.terminate()
        self.wait_for(lambda: self.process.poll() is not None)
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)
        self.assertEqual(len(self.events()), 1)

    def test_shutdown_during_delay_does_not_start_model(self):
        self.launch_order('sopa,agua')
        self.wait_for(lambda: time.monotonic() - self.launched_at >= 2)
        self.assertEqual(self.events(), [])
        self.process.terminate()
        self.wait_for(lambda: self.process.poll() is not None)
        self.assertEqual(self.events(), [])
