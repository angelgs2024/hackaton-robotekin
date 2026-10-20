#!/usr/bin/env python3
"""Control del SO101 simulado con DualShock 4 en Linux: pixi run mando."""
from __future__ import annotations

import argparse
from contextlib import closing
from dataclasses import dataclass
import math
import sys
import time

import numpy as np
from evdev import InputDevice, ecodes as E, list_devices

CONTROLES = """
╔════════════════ SO101 · MANDO PS4 ═════════════════╗
║ L2 / R2             Abrir / cerrar pinza           ║
║ Izquierdo ↑ / ↓      Alargar / recoger brazo       ║
║ Derecho ← / →        Girar la base                 ║
║ X / Círculo          Subir / bajar la pinza         ║
║ Cuadrado / Triángulo Inclinar muñeca en cada sentido║
║ Derecho ↑ / ↓        Rotar muñeca en cada sentido  ║
║ L1 (mantener)        Movimiento lento / preciso    ║
║ OPTIONS              Pausar / continuar            ║
║ SHARE                Reiniciar escena (en pausa)  ║
║ PS o Ctrl+C          Salir                         ║
╚═══════════════════════════════════════════════════╝
Los movimientos duran mientras mantienes el control pulsado.
L2/R2 regulan la apertura; no son un control de fuerza.
"""


@dataclass
class Orden:
    alcance: float = 0.0
    altura: float = 0.0
    giro: float = 0.0
    inclinacion: float = 0.0
    rotacion: float = 0.0
    pinza: float = 0.0
    lento: bool = False


def normalizar(valor, minimo, maximo, zona_muerta=0.12, gatillo=False):
    if maximo <= minimo:
        raise ValueError("El mando comunica un rango de eje inválido.")
    fraccion = float(np.clip((valor - minimo) / (maximo - minimo), 0, 1))
    valor = fraccion if gatillo else 2 * fraccion - 1
    return math.copysign(max(0, abs(valor) - zona_muerta) / (1 - zona_muerta), valor)


class Mando:
    EJES = (E.ABS_Y, E.ABS_RX, E.ABS_RY, E.ABS_Z, E.ABS_RZ)

    def __init__(self, dispositivo, zona_muerta):
        self.dispositivo = dispositivo
        self.zona_muerta = zona_muerta
        caps = dispositivo.capabilities(absinfo=False)
        if not set(self.EJES).issubset(caps.get(E.EV_ABS, [])) or not {
            E.BTN_SOUTH, E.BTN_EAST, E.BTN_WEST, E.BTN_NORTH,
        }.issubset(caps.get(E.EV_KEY, [])):
            raise ValueError("Ese dispositivo no tiene los ejes/botones de un DualShock 4.")
        self.anteriores = set(dispositivo.active_keys())

    def leer(self):
        # Drenar eventos y consultar estado actual evita conservar ejes obsoletos.
        pulsados = set()
        try:
            for evento in self.dispositivo.read():
                if evento.type == E.EV_KEY and evento.value == 1:
                    pulsados.add(evento.code)
        except BlockingIOError:
            pass
        botones = set(self.dispositivo.active_keys())
        pulsados |= botones - self.anteriores
        self.anteriores = botones

        def eje(codigo, gatillo=False):
            info = self.dispositivo.absinfo(codigo)
            return normalizar(info.value, info.min, info.max,
                              0.03 if gatillo else self.zona_muerta, gatillo)

        return Orden(
            alcance=-eje(E.ABS_Y),
            altura=int(E.BTN_SOUTH in botones) - int(E.BTN_EAST in botones),
            giro=-eje(E.ABS_RX),
            inclinacion=int(E.BTN_WEST in botones) - int(E.BTN_NORTH in botones),
            rotacion=-eje(E.ABS_RY),
            pinza=eje(E.ABS_Z, True) - eje(E.ABS_RZ, True),
            lento=E.BTN_TL in botones,
        ), pulsados


def buscar_mandos():
    encontrados = []
    for ruta in sorted(list_devices()):
        try:
            with closing(InputDevice(ruta)) as dispositivo:
                caps = dispositivo.capabilities(absinfo=False)
                if E.BTN_SOUTH in caps.get(E.EV_KEY, []):
                    encontrados.append((ruta, dispositivo.name, dispositivo.info.vendor))
        except OSError:
            continue
    return sorted(encontrados, key=lambda d: d[2] != 0x054C)


def elegir_dispositivo(ruta):
    if ruta:
        return InputDevice(ruta)
    mandos = buscar_mandos()
    if not mandos:
        raise RuntimeError(
            "No se encuentra ningún mando accesible. Conecta el PS4 por USB o "
            "emparéjalo por Bluetooth y vuelve a intentarlo. Si ya está conectado, "
            "comprueba los permisos de lectura de /dev/input/event*."
        )
    if len(mandos) == 1:
        return InputDevice(mandos[0][0])
    for i, (ruta, nombre, _) in enumerate(mandos, 1):
        print(f"  {i}. {nombre} ({ruta})")
    seleccion = input("Número del mando: ").strip()
    if not seleccion.isdigit() or not 1 <= int(seleccion) <= len(mandos):
        raise ValueError("Número de mando inválido.")
    return InputDevice(mandos[int(seleccion) - 1][0])


class Brazo:
    """Objetivos acotados; IK de hombro, codo y muñeca para alcance y altura.

    Se calcula desde las articulaciones objetivo actuales, sin acumular
    posiciones cartesianas inalcanzables. Los otros ejes son control directo.
    """

    def __init__(self, env):
        import mujoco
        from so101_nexus.config import SO101_JOINT_NAMES, SO101_TCP_SITE_NAME

        self.mj = mujoco
        self.env = env
        self.model = env.unwrapped.model
        self.datos = mujoco.MjData(self.model)
        ids = [self.model.joint(nombre).id for nombre in SO101_JOINT_NAMES]
        self.qadr = self.model.jnt_qposadr[ids]
        self.dofs = self.model.jnt_dofadr[ids]
        self.site = self.model.site(SO101_TCP_SITE_NAME).id
        self.base = self.model.body("base").id
        self.minimo = env.action_space.low.astype(float)
        self.maximo = env.action_space.high.astype(float)
        self.sincronizar()

    def sincronizar(self):
        self.objetivo = np.clip(
            self.env.unwrapped.data.qpos[self.qadr].copy(), self.minimo, self.maximo
        )

    def posicion(self, q):
        self.datos.qpos[:] = self.env.unwrapped.data.qpos
        self.datos.qpos[self.qadr] = q
        self.mj.mj_forward(self.model, self.datos)
        return self.datos.site_xpos[self.site].copy()

    def accion(self, orden, dt, velocidad):
        factor = velocidad * (0.25 if orden.lento else 1.0)
        angular = 0.65 * dt * factor  # 37 grados/s al 100 %.
        q = self.objetivo.copy()
        q[[0, 3, 4, 5]] += angular * np.array([
            orden.giro, orden.inclinacion, orden.rotacion, orden.pinza * 2,
        ])
        q = np.clip(q, self.minimo, self.maximo)
        if orden.alcance or orden.altura:
            inicio = self.posicion(q)
            radial = inicio[:2] - self.datos.xpos[self.base, :2]
            radio = np.linalg.norm(radial)
            radial = radial / radio if radio > 1e-6 else np.array([1.0, 0.0])
            destino = inicio + 0.08 * dt * factor * np.array([
                radial[0] * orden.alcance, radial[1] * orden.alcance, orden.altura,
            ])
            # Acotar cada paso del IK evita saltos cerca de singularidades.
            bajo = np.maximum(self.minimo[1:4], self.objetivo[1:4] - angular)
            alto = np.minimum(self.maximo[1:4], self.objetivo[1:4] + angular)
            jac = np.zeros((3, self.model.nv))
            for _ in range(8):
                actual = self.posicion(q)
                self.mj.mj_jacSite(self.model, self.datos, jac, None, self.site)
                j = jac[:, self.dofs[1:4]]
                dq = j.T @ np.linalg.solve(j @ j.T + 0.002**2 * np.eye(3), destino - actual)
                # Escalar juntos los incrementos conserva la dirección solicitada.
                margen = np.where(dq >= 0, alto - q[1:4], q[1:4] - bajo)
                escala = min(1.0, float(np.min(margen / np.maximum(np.abs(dq), 1e-12))))
                q[1:4] = np.clip(q[1:4] + max(0.0, escala) * dq, bajo, alto)
        self.objetivo = q
        return q.astype(np.float32)


def probar_mando(mando):
    print(CONTROLES)
    print("Prueba sin simulación. Mueve los controles; PS o Ctrl+C para salir.")
    try:
        while True:
            orden, pulsados = mando.leer()
            if E.BTN_MODE in pulsados:
                break
            print(f"\rAlargar {orden.alcance:+.2f} | Subir {orden.altura:+.0f} | "
                  f"Girar {orden.giro:+.2f} | Inclinar {orden.inclinacion:+.0f} | "
                  f"Rotar {orden.rotacion:+.2f} | Abrir {orden.pinza:+.2f} | "
                  f"Lento {int(orden.lento)}   ", end="", flush=True)
            time.sleep(0.05)
    finally:
        print()


def simular(mando, velocidad):
    import gymnasium as gym
    import mujoco.viewer
    import so101_nexus.mujoco  # Registra los entornos de Gymnasium.

    env = gym.make("MuJoCoPickLift-v1", render_mode="human",
                   control_mode="pd_joint_pos", robot_init_qpos_noise=0.0,
                   max_episode_steps=-1)
    try:
        env.reset(seed=42)
        brazo = Brazo(env)
        dt = env.unwrapped.control_dt
        pausa = True
        final_episodio = False
        print(CONTROLES)
        print("En pausa. Pulsa OPTIONS para empezar.")
        env.render()
        while env.unwrapped._viewer.is_running():
            inicio = time.monotonic()
            orden, pulsados = mando.leer()
            if E.BTN_MODE in pulsados:
                break
            if E.BTN_SELECT in pulsados and pausa:
                env.reset(seed=42)
                brazo.sincronizar()
                final_episodio = False
                print("Escena reiniciada. OPTIONS para empezar.")
            elif E.BTN_START in pulsados and not final_episodio:
                pausa = not pausa
                print("En pausa." if pausa else "Control activo.")
            if not pausa:
                accion = brazo.accion(orden, dt, velocidad)
                _, _, terminado, agotado, _ = env.step(accion)
                if terminado or agotado:
                    pausa = final_episodio = True
                    print("Episodio terminado. SHARE para reiniciar; OPTIONS para empezar después.")
            env.render()
            time.sleep(max(0, dt - (time.monotonic() - inicio)))
    finally:
        env.close()


def numero_rango(minimo, maximo):
    def convertir(texto):
        numero = float(texto)
        if not math.isfinite(numero) or not minimo <= numero <= maximo:
            raise argparse.ArgumentTypeError(f"Debe estar entre {minimo} y {maximo}.")
        return numero
    return convertir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--iniciar", action="store_true", help="Abrir directamente el simulador")
    modo.add_argument("--probar-mando", action="store_true", help="Ver controles sin abrir MuJoCo")
    modo.add_argument("--listar-mandos", action="store_true", help="Mostrar mandos accesibles")
    parser.add_argument("--dispositivo", help="Ruta /dev/input/eventN del mando")
    parser.add_argument("--velocidad", type=numero_rango(0.1, 2.0), default=1.0)
    parser.add_argument("--zona-muerta", type=numero_rango(0.0, 0.5), default=0.12)
    args = parser.parse_args()
    directo = args.iniciar or args.probar_mando or args.listar_mandos
    while True:
        try:
            if directo:
                opcion = "1" if args.iniciar else "2" if args.probar_mando else "3"
            else:
                print("\nSO101 — Control con mando PS4\n"
                      "  1. Abrir simulador\n  2. Probar mando\n"
                      "  3. Listar mandos\n  4. Ver controles\n  0. Salir")
                opcion = input("Elige una opción: ").strip()
            if opcion == "0":
                return 0
            if opcion == "4":
                print(CONTROLES)
            elif opcion == "3":
                mandos = buscar_mandos()
                for ruta, nombre, _ in mandos:
                    print(f"{ruta}: {nombre}")
                if not mandos:
                    print("No se encuentran mandos accesibles. Conecta el PS4 y comprueba sus permisos.")
            elif opcion in ("1", "2"):
                with closing(elegir_dispositivo(args.dispositivo)) as dispositivo:
                    mando = Mando(dispositivo, args.zona_muerta)
                    print(f"Mando: {dispositivo.name} ({dispositivo.path})")
                    if opcion == "1":
                        simular(mando, args.velocidad)
                    else:
                        probar_mando(mando)
            else:
                print("Elige un número del menú.")
        except (KeyboardInterrupt, EOFError):
            print("\nControl detenido.")
            return 0
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"\nControl detenido: {exc}", file=sys.stderr)
            if directo:
                return 1
        if directo:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
