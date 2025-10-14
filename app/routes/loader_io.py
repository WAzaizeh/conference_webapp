from core.app import rt
from fasthtml.common import *

# Static file for loader.io verification (if file exists)
@rt('/loaderio-2eacf95a8c9f241ca8c2e18e3b2ca777.txt')
def get():
    print('in loader io')
    file_path = Path(__file__).parent / 'loaderio-2eacf95a8c9f241ca8c2e18e3b2ca777.txt'
    if file_path.exists():
        return FileResponse(file_path)
    return Response("loaderio-2eacf95a8c9f241ca8c2e18e3b2ca777", media_type='text/plain')