"""Pruebas sin mando ni ventana: pixi run python -m unittest -v test_controlar_ps4."""
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from unittest.mock import Mock, patch

import controlar_ps4
from types import SimpleNamespace

import gymnasium as gym
import numpy as np
import so101_nexus.mujoco
from evdev import ecodes as E
from controlar_ps4 import Brazo, Mando, Orden, normalizar


class DispositivoFalso:
    def __init__(self):
        self.botones = set()
        self.valores = {e: 127.5 for e in Mando.EJES}
        self.valores.update({E.ABS_Z: 0, E.ABS_RZ: 0})

    def capabilities(self, **kwargs):
        return {E.EV_ABS: list(Mando.EJES),
                E.EV_KEY: [E.BTN_SOUTH, E.BTN_EAST, E.BTN_WEST, E.BTN_NORTH]}

    def active_keys(self):
        return list(self.botones)

    def absinfo(self, codigo):
        return SimpleNamespace(value=self.valores[codigo], min=0, max=255)

    def read(self):
        raise BlockingIOError()


class EntradaTest(unittest.TestCase):
    def test_zona_muerta_y_extremos(self):
        for value in (120, 127, 128, 135):
            self.assertEqual(normalizar(value, 0, 255), 0)
        self.assertEqual(normalizar(0, 0, 255), -1)
        self.assertEqual(normalizar(255, 0, 255), 1)
        self.assertEqual(normalizar(0, 0, 255, gatillo=True), 0)

    def test_mapeo_completo(self):
        d = DispositivoFalso()
        m = Mando(d, 0.12)
        self.assertEqual(m.leer()[0], Orden())
        d.valores.update({E.ABS_Y: 0, E.ABS_RX: 255, E.ABS_RY: 0, E.ABS_Z: 255})
        d.botones = {E.BTN_SOUTH, E.BTN_WEST, E.BTN_TL}
        self.assertEqual(m.leer()[0], Orden(1, 1, -1, 1, 1, 1, True))
        d.valores.update({E.ABS_Y: 255, E.ABS_RX: 0, E.ABS_RY: 255,
                          E.ABS_Z: 0, E.ABS_RZ: 255})
        d.botones = {E.BTN_EAST, E.BTN_NORTH}
        self.assertEqual(m.leer()[0], Orden(-1, -1, 1, -1, -1, -1))
        d.botones = {E.BTN_SOUTH, E.BTN_EAST, E.BTN_WEST, E.BTN_NORTH}
        d.valores[E.ABS_Z] = 255
        orden, _ = m.leer()
        self.assertEqual((orden.altura, orden.inclinacion, orden.pinza), (0, 0, 0))

    def test_options_solo_al_pulsar(self):
        d = DispositivoFalso()
        m = Mando(d, 0.12)
        d.botones = {E.BTN_START}
        self.assertIn(E.BTN_START, m.leer()[1])
        self.assertNotIn(E.BTN_START, m.leer()[1])
        d.botones.clear()
        m.leer()
        d.botones.add(E.BTN_START)
        self.assertIn(E.BTN_START, m.leer()[1])

    def test_desconexion_no_reutiliza_orden(self):
        d = DispositivoFalso()
        m = Mando(d, 0.12)
        def desconectado():
            raise OSError('Mando desconectado')
        d.read = desconectado
        with self.assertRaises(OSError):
            m.leer()


class DispositivosTest(unittest.TestCase):
    def dispositivo(self):
        # Mock normal: close() disponible, sin __enter__ ni __exit__, como evdev.
        return SimpleNamespace(
            name='Wireless Controller', path='/dev/input/event99',
            info=SimpleNamespace(vendor=0x054C), close=Mock(),
            capabilities=Mock(return_value={E.EV_KEY: [E.BTN_SOUTH]}),
        )

    def test_listado_sin_protocolo_context_manager(self):
        dispositivo = self.dispositivo()
        with patch.object(controlar_ps4, 'list_devices', return_value=[dispositivo.path]), \
             patch.object(controlar_ps4, 'InputDevice', return_value=dispositivo):
            self.assertEqual(controlar_ps4.buscar_mandos(), [
                (dispositivo.path, dispositivo.name, 0x054C),
            ])
        dispositivo.close.assert_called_once_with()

    def test_listado_cierra_dispositivo_si_falla_lectura(self):
        dispositivo = self.dispositivo()
        dispositivo.capabilities.side_effect = OSError('Desconectado')
        with patch.object(controlar_ps4, 'list_devices', return_value=[dispositivo.path]), \
             patch.object(controlar_ps4, 'InputDevice', return_value=dispositivo):
            self.assertEqual(controlar_ps4.buscar_mandos(), [])
        dispositivo.close.assert_called_once_with()

    def test_abrir_y_cerrar_en_ambos_modos(self):
        for opcion, funcion in [('--iniciar', 'simular'), ('--probar-mando', 'probar_mando')]:
            for error in (None, OSError('Desconectado'), KeyboardInterrupt()):
                with self.subTest(opcion=opcion, error=type(error).__name__):
                    dispositivo = self.dispositivo()
                    with patch('sys.argv', ['controlar_ps4.py', opcion]), \
                         patch.object(controlar_ps4, 'elegir_dispositivo', return_value=dispositivo), \
                         patch.object(controlar_ps4, 'Mando'), \
                         patch.object(controlar_ps4, funcion, side_effect=error) as ejecutar, \
                         redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                        self.assertEqual(controlar_ps4.main(), 1 if isinstance(error, OSError) else 0)
                        ejecutar.assert_called_once()
                    dispositivo.close.assert_called_once_with()


class SimulacionTest(unittest.TestCase):
    def setUp(self):
        self.env = gym.make('MuJoCoPickLift-v1', control_mode='pd_joint_pos',
                            robot_init_qpos_noise=0, max_episode_steps=-1)
        self.env.reset(seed=42)
        self.b = Brazo(self.env)

    def tearDown(self):
        self.env.close()

    def test_movimientos_cartesianos(self):
        for campo, eje in [('alcance', 0), ('altura', 2)]:
            for signo in (-1, 1):
                with self.subTest(campo=campo, signo=signo):
                    self.env.reset(seed=42)
                    self.b.sincronizar()
                    inicial = self.b.posicion(self.b.objetivo)
                    orden = Orden(**{campo: signo})
                    for _ in range(10):
                        accion = self.b.accion(orden, 0.02, 1)
                        self.env.step(accion)
                    delta = self.b.posicion(self.b.objetivo) - inicial
                    self.assertGreater(delta[eje] * signo, 0.002)
                    self.assertLess(abs(delta[2 if eje == 0 else 0]), 0.001)
                    self.assertTrue(np.isfinite(self.env.unwrapped.data.qpos).all())

    def test_limites_y_velocidad(self):
        rng = np.random.default_rng(1)
        for _ in range(300):
            previa = self.b.objetivo.copy()
            orden = Orden(*rng.uniform(-1, 1, 6))
            accion = self.b.accion(orden, 0.02, 1)
            self.assertTrue(self.env.action_space.contains(accion))
            self.assertLessEqual(np.max(abs(accion[:5] - previa[:5])), 0.013001)
            self.assertLessEqual(abs(accion[5] - previa[5]), 0.026001)
            self.env.step(accion)
        np.testing.assert_allclose(self.b.accion(Orden(), 0.02, 1), accion, atol=1e-7)

    def test_pinza_y_modo_lento(self):
        inicial = self.b.objetivo.copy()
        abrir = self.b.accion(Orden(pinza=1), 0.02, 1)
        self.assertGreater(abrir[-1], inicial[-1])
        cerrar = self.b.accion(Orden(pinza=-1), 0.02, 1)
        self.assertLess(cerrar[-1], abrir[-1])
        self.b.sincronizar()
        normal = self.b.accion(Orden(giro=1), 0.02, 1)[0] - inicial[0]
        self.b.sincronizar()
        lento = self.b.accion(Orden(giro=1, lento=True), 0.02, 1)[0] - inicial[0]
        self.assertAlmostEqual(lento / normal, 0.25, places=5)


if __name__ == '__main__':
    unittest.main()
