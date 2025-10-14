from fasthtml.common import *
from core.app import app, rt
import os, uvicorn

# Get absolute path to assets directory
assets_dir = Path(__file__).parent / 'assets'

# Static file routes - more specific pattern to avoid conflicts
@rt('/assets/{fname:path}')
def get(fname:str): 
    file_path = assets_dir / fname
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return Response("File not found", status_code=404)


# Static file routes - for images
@rt('/{fname:path}.{ext:static}')
def get_static(fname:str, ext:str): 
    file_path = assets_dir / f'{fname}.{ext}'
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return Response("File not found", status_code=404)

# Import route modules - routes are registered on import
import routes.main
import routes.admin
import routes.session
import routes.speaker
import routes.sponsor
import routes.feedback
import routes.qa

# Run the FastHTML app with Uvicorn, using the SSL certificate and private key
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
    )