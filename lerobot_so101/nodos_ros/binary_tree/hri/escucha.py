"""
ESCUCHA — el oído del robot.

Escucha:  /hri/escuchar (Empty)   -> escucha una frase
Publica:  /hri/oido     (String)  -> lo que ha entendido ("" si nada)

Reconocimiento de voz con micrófono y Vosk.
Parámetro microfono: índice de PortAudio; -1 usa la entrada predeterminada.
"""
import json
import queue
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Empty, String


class Escucha(Node):
    def __init__(self):
        super().__init__("escucha")
        self.microfono_id = self.declare_parameter("microfono", -1).value
        modelo = self.declare_parameter("modelo", "models/vosk-model-es-0.42").value
        import sounddevice
        import vosk
        vosk.SetLogLevel(-1)
        self.sd, self.vosk = sounddevice, vosk
        self.get_logger().info(f"Cargando reconocimiento de voz: {modelo}")
        self.modelo = vosk.Model(modelo)
        self.get_logger().info("Modelo de voz preparado")

        self.oido = self.create_publisher(String, "/hri/oido", 10)
        self.create_subscription(Empty, "/hri/escuchar", lambda _: self.escuchar(), 10)

    def escuchar(self):
        texto = self.microfono()
        if rclpy.ok():
            self.oido.publish(String(data=texto))

    def microfono(self, segundos=12):
        entrada = None if self.microfono_id < 0 else self.microfono_id
        dispositivo = self.sd.query_devices(device=entrada, kind="input")
        frecuencia = int(dispositivo["default_samplerate"])
        # Vosk debe recibir la misma frecuencia que entrega el micrófono.
        rec = self.vosk.KaldiRecognizer(self.modelo, frecuencia)
        audio = queue.Queue()
        with self.sd.RawInputStream(device=entrada, samplerate=frecuencia, blocksize=frecuencia // 2, dtype="int16", channels=1,
                                    callback=lambda datos, *_: audio.put(bytes(datos))):
            print(f"🎤 escuchando... ({dispositivo['name']})", flush=True)
            fin = time.monotonic() + segundos
            while rclpy.ok() and time.monotonic() < fin:
                try:
                    datos = audio.get(timeout=0.2)
                except queue.Empty:
                    continue
                if rec.AcceptWaveform(datos):
                    texto = json.loads(rec.Result())["text"]
                    if texto:
                        return texto
        return json.loads(rec.FinalResult())["text"]


def main():
    rclpy.init()
    try:
        rclpy.spin(Escucha())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
