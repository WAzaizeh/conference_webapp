from pathlib import Path
from datetime import datetime
from fasthtml.common import Link, Script

def cache_busting():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def fetch_static_files() -> list:
    current_dir = Path(__file__).parent
    assets_dir = current_dir.parent / 'assets'

    static_files = []
    # Sorted so stylesheets load in a stable order (main.css before theme-26.css, which overrides it)
    for path in sorted(assets_dir.rglob('*')):
        if path.is_file():
            # Get path relative to assets directory
            relative_path = path.relative_to(assets_dir)

            if path.suffix == '.css':
                static_files.append(Link(
                    rel='stylesheet', 
                    href=f'/assets/{relative_path}?t={cache_busting()}', 
                    type='text/css'
                ))
            elif path.suffix == '.js':
                static_files.append(Script(
                    src=f'/assets/{relative_path}?t={cache_busting()}'
                ))

    return static_files