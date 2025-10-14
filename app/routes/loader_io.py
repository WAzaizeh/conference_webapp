from core.app import rt
from fasthtml.common import *

# Static file for loader.io verification (if file exists)
@rt('/loaderio-6fe2ffb64dfc07be56f8da6e531010a2.txt')
def get():
    print('in loader io')
    file_path = Path(__file__).parent / 'loaderio-6fe2ffb64dfc07be56f8da6e531010a2.txt'
    if file_path.exists():
        return FileResponse(file_path)
    return Response("loaderio-6fe2ffb64dfc07be56f8da6e531010a2", media_type='text/plain')