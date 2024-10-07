from pathlib import Path
from fasthtml.common import Link, Script

def fetch_static_files():
    static_files = []
    for path in Path('./assets').rglob('*'):
        if path.is_file() and path.suffix == '.css':
            static_files.append(Link(rel='stylesheet', href=f'/{path.name}', type='text/css'))
        elif path.is_file() and path.suffix == '.js':
            static_files.append(Script(src=f'/{path.name}'))
    return static_files