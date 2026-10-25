#!/usr/bin/env python3
"""
Ejecutor de las pruebas de interfaz, HRI y secuencia LeRobot.
Descubre las pruebas de test/ en modo headless, sin audio ni robot real.
"""
import os
import sys
import unittest

# Asegurar plataforma offscreen para que funcione en cualquier entorno
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Evita que las pruebas de integración envíen pedidos al dominio ROS habitual.
os.environ.setdefault("ROS_DOMAIN_ID", "117")

# Asegurar rutas
TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run():
    print("=" * 60)
    print("🚀 EJECUTANDO SUITE DE PRUEBAS - HRI + GUI + LEROBOT")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=TESTS_DIR, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("-" * 60)
    if result.wasSuccessful():
        print(f"✅ TODAS LAS PRUEBAS ({result.testsRun}) HAN PASADO CON ÉXITO")
        return 0
    else:
        print(f"❌ FALLOS: {len(result.failures)} | ERRORES: {len(result.errors)}")
        return 1

if __name__ == '__main__':
    sys.exit(run())
