from fasthtml.common import *
from routes.main import get_main_routes
from routes.admin import get_admin_routes
from utils.static import fetch_static_files
from routes.sessions import get_session_routes
from routes.speakers import get_speaker_routes
from routes.sponsors import get_sponsor_routes
from routes.feedback import get_feedback_routes
import os, uvicorn

tlink = (Script(src='https://unpkg.com/tailwindcss-cdn@3.4.3/tailwindcss.js'),)
dlink = [Link(
    rel='stylesheet',
    href='https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css',),
    Script(src='https://cdn.tailwindcss.com'),
]
falink = Link(
    rel='stylesheet',
    href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css', 
    integrity='sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==', 
    crossorigin='anonymous',
    referrerpolicy='no-referrer'
)
fontLink = Link(
    rel='stylesheet',
    href='https://fonts.cdnfonts.com/css/inter',
)
materialLink = Link(
    rel='stylesheet',
    href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200',
)
static_fils_hdrs = fetch_static_files()

app = FastHTML(hdrs=[tlink, dlink, falink, fontLink, materialLink, *static_fils_hdrs])
rt = app.route

# stylesheet link routing
@app.route('/{fname:path}.{ext:static}')
def get(fname:str, ext:str): 
    return FileResponse(f'./assets/{fname}.{ext}')

# Routes
get_main_routes(rt)
get_admin_routes(rt)
get_session_routes(rt)
get_speaker_routes(rt)
get_sponsor_routes(rt)
get_feedback_routes(rt)

# Run the FastHTML app with Uvicorn, using the SSL certificate and private key
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
    )