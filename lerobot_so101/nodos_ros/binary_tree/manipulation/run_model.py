"""Valida el catálogo y ejecuta una política, sin interpretar comandos de shell."""
import argparse
import math
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

MODEL_MESSAGES = {
    'coger_vaso_amarillo': 'Cojo vaso amarillo',
    'coger_tenedor': 'Cojo tenedor',
    'coger_cuchillo': 'Cojo cuchillo',
    'coger_cuchara': 'Cojo cuchara',
}


def order_models(food, drink):
    cutlery = {'chuleton': ['coger_tenedor'], 'sopa': ['coger_cuchara']}
    if food not in cutlery or drink not in ('agua', 'cocacola'):
        raise ValueError(f'Pedido desconocido: {food},{drink}')
    return ['coger_vaso_amarillo', *cutlery[food]]


class ModelCatalog:
    def __init__(self, path):
        self.path = Path(path).expanduser().resolve()
        root = ET.parse(self.path).getroot()
        if root.tag != 'lerobot':
            raise ValueError('El XML debe tener raíz <lerobot>')
        self.command = [(arg.text or '').strip() for arg in root.findall('./command/arg')]
        if not self.command or any(not arg for arg in self.command):
            raise ValueError('Falta un comando LeRobot válido en <command>')
        if not any('{policy}' in arg for arg in self.command):
            raise ValueError('El comando debe incluir {policy}')
        self.models = {}
        for model in root.findall('./models/model'):
            key = model.get('id', '')
            if not key or key in self.models:
                raise ValueError(f'Identificador de modelo vacío o duplicado: {key}')
            self.models[key] = dict(model.attrib)

    def arguments(self, key, dry_run=False):
        if key not in self.models:
            raise ValueError(f'Falta el modelo {key} en {self.path}')
        model = self.models[key]
        policy = model.get('policy', '').strip()
        duration = model.get('duration', '')
        if not math.isfinite(float(duration)) or float(duration) <= 0:
            raise ValueError(f'Duración inválida para {key}: {duration}')
        if not dry_run and (not policy or 'PENDIENTE' in policy):
            raise ValueError(f'Rellena policy del modelo {key} en {self.path}')
        if policy.startswith(('./', '../', '/', '~')):
            local = Path(policy).expanduser()
            policy = str((self.path.parent / local).resolve())
            if not dry_run and not Path(policy).is_dir():
                raise ValueError(f'No existe la carpeta del modelo {key}: {policy}')
        substitutions = {
            '{python}': sys.executable, '{policy}': policy or 'PENDIENTE',
            '{task}': model.get('task', key), '{duration}': duration,
        }
        args = []
        for template in self.command:
            for token, value in substitutions.items():
                template = template.replace(token, value)
            if not dry_run and 'PENDIENTE' in template:
                raise ValueError(f'Completa los argumentos de conexión en {self.path}: {template}')
            args.append(template)
        return args


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--model')
    parser.add_argument('--food')
    parser.add_argument('--drink')
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        catalog = ModelCatalog(args.config)
        if args.validate_only:
            models = order_models(args.food, args.drink)
            # Comprueba TODOS los pasos del pedido antes de mover el primer vaso.
            for model in models:
                catalog.arguments(model, args.dry_run)
            print('Secuencia preparada: ' + ' -> '.join(models), flush=True)
            return 0
        command = catalog.arguments(args.model, args.dry_run)
        if args.dry_run:
            print(f'[SIMULACIÓN] {MODEL_MESSAGES.get(args.model, args.model)}', flush=True)
            return 0
        print(f'Ejecutando LeRobot: {args.model}', flush=True)
        # Conserva el PID y el grupo de procesos que supervisa el árbol.
        os.execvpe(command[0], command, os.environ)
    except (ValueError, OSError, ET.ParseError) as error:
        print(f'No se puede ejecutar LeRobot: {error}', file=sys.stderr, flush=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
