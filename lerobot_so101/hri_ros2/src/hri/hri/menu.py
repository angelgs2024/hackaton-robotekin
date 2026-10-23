"""La carta. Para cambiar platos o bebidas, solo se toca este archivo."""

# clave: (cómo lo dice el robot, palabras que entiende)
COMIDAS = {
    "chuleton": ("chuletón de vaca", ["chuleton", "carne", "vaca"]),
    "sopa": ("sopa", ["sopa"]),
}
BEBIDAS = {
    "agua": ("agua", ["agua"]),
    "cocacola": ("Coca-Cola", ["coca", "cola"]),
}


def opciones(carta):
    return " o ".join(nombre for nombre, _ in carta.values())
