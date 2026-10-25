"""
PREGUNTA — la voz del robot.

Escucha:  /hri/empezar   (Empty)   -> saluda y dice la carta
          /hri/preguntar (String)  -> dice el texto y después pide escuchar
          /hri/decir     (String)  -> solo dice el texto
Publica:  /hri/escuchar  (Empty)   -> cuando termina de preguntar

Parámetros: voz    (modelo de Piper)
            robot  (0 por defecto = voz natural, 1.5 = muy metálica)
            interface_mode (habla sin solicitar escucha por micrófono)
Si Piper falla, habla con pyttsx3; si tampoco hay, solo escribe el texto.
"""
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Empty, String

from .menu import BEBIDAS, COMIDAS, opciones


def robotizar(audio, frecuencia, cantidad):
    """Timbre de robot que se sigue entendiendo: eco muy corto (suena a lata) y modulación en anillo suave."""
    if cantidad <= 0:
        return audio
    x = audio.astype(np.float32) / 32768
    retardo = int(frecuencia * 0.006)   # 6 ms: resonancia metálica
    eco = np.concatenate([np.zeros(retardo, np.float32), x[:-retardo]])
    x = x + 0.6 * cantidad * eco
    t = np.arange(len(x)) / frecuencia
    x = (1 - 0.4 * cantidad) * x + 0.4 * cantidad * x * np.sin(2 * np.pi * 50 * t)   # zumbido de 50 Hz
    return (x / max(np.abs(x).max(), 1e-9) * 0.9 * 32767).astype(np.int16)


class Pregunta(Node):
    def __init__(self, interface_mode=False):
        super().__init__("pregunta")
        self.interface_mode = self.declare_parameter("interface_mode", interface_mode).value
        modelo = self.declare_parameter("voz", "models/es_ES-davefx-medium.onnx").value
        self.robot = self.declare_parameter("robot", 0.0).value
        self.piper = self.voz = None
        try:
            import sounddevice
            from piper import PiperVoice, SynthesisConfig
            self.sd = sounddevice
            self.piper = PiperVoice.load(modelo)
            # Usa el ritmo y la entonación naturales del modelo de voz.
            self.ajustes = SynthesisConfig()
        except Exception as e:
            self.get_logger().warn(f"Sin Piper ({e}): uso pyttsx3")
            self.voz_pyttsx3()

        self.escuchar = self.create_publisher(Empty, "/hri/escuchar", 10)
        self.create_subscription(String, "/hri/preguntar", lambda m: self.preguntar(m.data), 10)
        self.create_subscription(String, "/hri/decir", lambda m: self.decir(m.data), 10)
        # El árbol espera esta suscripción antes de iniciar el pedido.
        self.create_subscription(Empty, "/hri/empezar", lambda _: self.saludar(), 10)

    def voz_pyttsx3(self):
        try:
            import pyttsx3
            self.voz = pyttsx3.init()
            for voz in self.voz.getProperty("voices"):
                if "spanish" in voz.name.lower() or "es" in voz.id.lower().replace(".", "/").split("/"):
                    self.voz.setProperty("voice", voz.id)
                    break
        except Exception as e:
            self.voz = None
            self.get_logger().warn(f"Sin voz ({e}): solo escribo el texto")

    def decir(self, texto):
        print(f"🤖 {texto}", flush=True)
        if self.piper:
            trozos = [np.frombuffer(c.audio_int16_bytes, np.int16) for c in self.piper.synthesize(texto, syn_config=self.ajustes)]
            if trozos:
                frecuencia = self.piper.config.sample_rate
                self.sd.play(robotizar(np.concatenate(trozos), frecuencia, self.robot), frecuencia)
                self.sd.wait()   # espera a terminar de hablar antes de mandar escuchar
        elif self.voz:
            self.voz.say(texto)
            self.voz.runAndWait()

    def preguntar(self, texto):
        self.decir(texto)
        if rclpy.ok() and not self.interface_mode:
            self.escuchar.publish(Empty())

    def saludar(self):
        if self.interface_mode:
            self.decir(f"¡Hola, bienvenido! Para comer tenemos {opciones(COMIDAS)}. "
                       f"Y para beber, {opciones(BEBIDAS)}. "
                       "Elige una comida y una bebida en la pantalla y pulsa Confirmar Comanda.")
            return
        self.preguntar(f"¡Hola, bienvenido! Para comer tenemos {opciones(COMIDAS)}. "
                       f"Y para beber, {opciones(BEBIDAS)}. ¿Qué va a tomar?")


def main():
    rclpy.init()
    try:
        rclpy.spin(Pregunta())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
