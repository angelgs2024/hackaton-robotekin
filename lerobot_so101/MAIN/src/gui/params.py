"""
Parámetros de posición para cada widget sobre la mesa.

Las coordenadas son OFFSETS respecto al CENTRO del panel.
  - offset_x positivo → desplaza a la derecha
  - offset_x negativo → desplaza a la izquierda
  - offset_y positivo → desplaza hacia abajo
  - offset_y negativo → desplaza hacia arriba

Ajusta estos valores para colocar cada elemento sobre la mesa de la imagen de fondo.
"""

# ──────────────────────────────────────────────
# PLATO  (comida) — centrado ligeramente a la izquierda
# ──────────────────────────────────────────────
PLATO_OFFSET_X = 0
PLATO_OFFSET_Y = 0
PLATO_SOPA_OFFSET_Y = PLATO_OFFSET_Y - 25

# ──────────────────────────────────────────────
# VASO / BEBIDA — a la derecha del plato
# ──────────────────────────────────────────────
BEBIDA_OFFSET_X = -100
BEBIDA_OFFSET_Y = 70

# ──────────────────────────────────────────────
# CUBIERTO: CUCHILLO
# Cada cubierto tiene su propio offset respecto al centro de la mesa.
# ──────────────────────────────────────────────
CUCHILLO_OFFSET_X = -160
CUCHILLO_OFFSET_Y = 10

# ──────────────────────────────────────────────
# CUBIERTO: TENEDOR
# ──────────────────────────────────────────────
TENEDOR_OFFSET_X = 160
TENEDOR_OFFSET_Y = 10

# ──────────────────────────────────────────────
# CUBIERTO: CUCHARA
# ──────────────────────────────────────────────
CUCHARA_OFFSET_X = CUCHILLO_OFFSET_X
CUCHARA_OFFSET_Y = CUCHILLO_OFFSET_Y

# ──────────────────────────────────────────────
# BOCADILLO DE TEXTO  (speech bubble) — abajo centrado
# ──────────────────────────────────────────────
BOCADILLO_OFFSET_X = 0
BOCADILLO_OFFSET_Y = 200
