"""
CONFIRMA — entiende al cliente y confirma el pedido.

Escucha:  /hri/oido      (String)  <- lo que ha oído el nodo escucha
Publica:  /hri/preguntar (String)  -> para seguir la conversación
          /hri/decir     (String)  -> mensaje final
          /hri/pedido    (String)  -> "chuleton,agua" al confirmar (para Manipulación)
"""
import unicodedata

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import Empty, String

from .menu import BEBIDAS, COMIDAS, opciones


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def buscar(texto, carta):
    texto = normalizar(texto)
    for clave, (_, palabras) in carta.items():
        if any(p in texto for p in palabras):
            return clave
    return None


def es_si(texto):
    return any(p in normalizar(texto).split() for p in ["si", "vale", "correcto", "exacto", "claro"])


class Confirma(Node):
    def __init__(self):
        super().__init__("confirma")
        self.pub_preguntar = self.create_publisher(String, "/hri/preguntar", 10)
        self.pub_decir = self.create_publisher(String, "/hri/decir", 10)
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub_pedido = self.create_publisher(String, "/hri/pedido", latched)
        self.create_subscription(String, "/hri/oido", lambda m: self.oido(m.data), 10)
        self.create_subscription(Empty, "/hri/empezar", lambda _: self.reiniciar(), 10)
        self.reiniciar()

    def reiniciar(self):
        self.comida = self.bebida = None
        self.confirmando = False

    def preguntar(self, texto):
        self.pub_preguntar.publish(String(data=texto))

    def oido(self, texto):
        if not texto.strip():
            return self.preguntar("¿Perdone? No le he oído.")

        if self.confirmando:
            if es_si(texto):
                self.pub_decir.publish(String(data="¡Perfecto! Ahora mismo le preparo la mesa."))
                self.pub_pedido.publish(String(data=f"{self.comida},{self.bebida}"))
                self.get_logger().info(f"Pedido: {self.comida},{self.bebida}")
            else:
                self.preguntar("Vale, dígame otra vez qué quiere.")
            return self.reiniciar()

        self.comida = self.comida or buscar(texto, COMIDAS)
        self.bebida = self.bebida or buscar(texto, BEBIDAS)
        if self.comida and self.bebida:
            self.confirmando = True
            self.preguntar(f"Entonces, {COMIDAS[self.comida][0]} y {BEBIDAS[self.bebida][0]}. ¿Es correcto?")
        elif self.comida:
            self.preguntar(f"¿Y para beber? ¿{opciones(BEBIDAS)}?")
        elif self.bebida:
            self.preguntar(f"¿Y para comer? ¿{opciones(COMIDAS)}?")
        else:
            self.preguntar(f"Perdone, no le he entendido. ¿{opciones(COMIDAS)}? ¿{opciones(BEBIDAS)}?")


def main():
    rclpy.init()
    try:
        rclpy.spin(Confirma())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
