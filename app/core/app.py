import os
from fasthtml.common import *
from core.static import fetch_static_files
from core.visitor import VisitorMiddleware
from starlette.middleware import Middleware

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
htmxScript = Script(src='https://unpkg.com/htmx.org@1.9.10')
static_fils_hdrs = fetch_static_files()
favicon_link = Link(rel='icon', type='image/x-icon', href='/assets/favicon.ico'),

# Session cookies are signed with SESSION_SECRET (set per environment in the deploy workflows).
# Locally it falls back to a generated, git-ignored .sesskey file.
app = FastHTML(
    secret_key=os.getenv('SESSION_SECRET') or None,
    hdrs=[tlink, favicon_link, dlink, falink, fontLink, materialLink, htmxScript, *static_fils_hdrs],
    middleware=[Middleware(VisitorMiddleware)],
)

rt = app.route
