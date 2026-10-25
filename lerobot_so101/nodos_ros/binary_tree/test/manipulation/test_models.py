from pathlib import Path
from contextlib import redirect_stdout
import io
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from binary_tree_manipulation.run_model import ModelCatalog, main, order_models


class TestModelCatalog(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='model catalog ')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'models.xml'
        original = Path(get_package_share_directory('binary_tree')) / 'config/lerobot_models.xml'
        self.tree = ET.parse(original)
        self.tree.write(self.path)

    def save(self):
        self.tree.write(self.path)
        return ModelCatalog(self.path)

    def test_user_command_preserves_camera_mapping_as_one_argument(self):
        yellow = self.tree.find("./models/model[@id='coger_vaso_amarillo']")
        yellow.set('policy', 'robotekin/act_vaso_amarillo')
        args = self.save().arguments('coger_vaso_amarillo')
        self.assertIn('--robot.port=/dev/ttyACM1', args)
        self.assertIn('--policy.n_action_steps=1', args)
        self.assertIn('--policy.temporal_ensemble_coeff=0.01', args)
        self.assertIn('--duration=60', args)
        self.assertIn('--task=Pick up the yellow cup and place it next to the plate', args)
        cameras = [arg for arg in args if arg.startswith('--robot.cameras=')]
        self.assertEqual(len(cameras), 1)
        self.assertIn('/dev/video6', cameras[0])
        self.assertIn('/dev/video4', cameras[0])
        self.assertIn('{ top:', cameras[0])

    def test_pending_model_fails_but_simulation_accepts_it(self):
        catalog = ModelCatalog(self.path)
        with self.assertRaisesRegex(ValueError, 'Rellena policy'):
            catalog.arguments('coger_tenedor')
        self.assertIn('--policy.path=PENDIENTE', catalog.arguments('coger_tenedor', dry_run=True))

    def test_simulation_prints_actions_without_executing_lerobot(self):
        for model, message in (
            ('coger_vaso_amarillo', 'Cojo vaso amarillo'),
            ('coger_tenedor', 'Cojo tenedor'),
            ('coger_cuchillo', 'Cojo cuchillo'),
            ('coger_cuchara', 'Cojo cuchara'),
        ):
            output = io.StringIO()
            with self.subTest(model=model), redirect_stdout(output), patch(
                'sys.argv', ['ejecutar_modelo', '--config', str(self.path), '--model', model, '--dry-run']
            ), patch('binary_tree_manipulation.run_model.os.execvpe') as execute:
                self.assertEqual(main(), 0)
                execute.assert_not_called()
                self.assertEqual(output.getvalue().strip(), f'[SIMULACIÓN] {message}')

    def test_pedido_test_enables_simulation_and_keeps_voice_by_default(self):
        script = Path(__file__).resolve().parents[2] / 'scripts/run_voice.sh'
        # Captura el lanzamiento sin arrancar voz, ventana ni brazo.
        stub = '''exec() { printf '%s\\n' "$@"; }
source "$@"
'''
        for extra, interface in (([], 'false'), (['--interface'], 'true'),
                                 (['simular_modelos:=false'], 'false')):
            with self.subTest(extra=extra):
                result = subprocess.run(
                    ['bash', '-c', stub, 'test-pedido', str(script), 'test', *extra],
                    capture_output=True, text=True, check=True, timeout=10,
                )
                lines = result.stdout.splitlines()
                arguments = dict(line.split(':=', 1) for line in lines if ':=' in line)
                self.assertEqual(arguments['simular_modelos'], 'true')
                self.assertEqual(arguments['interface'], interface)
                self.assertIn('waiter_behavior.py', lines)
                self.assertNotIn('test', lines)

    def test_relative_model_paths_are_resolved_from_xml(self):
        model_dir = Path(self.temp.name) / 'models' / 'fork'
        model_dir.mkdir(parents=True)
        model = self.tree.find("./models/model[@id='coger_tenedor']")
        model.set('policy', './models/fork')
        self.assertIn(f'--policy.path={model_dir}', self.save().arguments('coger_tenedor'))

    def test_invalid_duration_and_unknown_orders_fail(self):
        model = self.tree.find("./models/model[@id='coger_tenedor']")
        for duration in ('0', '-1', 'nan', 'inf'):
            model.set('duration', duration)
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                self.save().arguments('coger_tenedor', dry_run=True)
        with self.assertRaises(ValueError):
            order_models('pizza', 'agua')
        with self.assertRaises(ValueError):
            order_models('sopa', 'vino')
