from fasthtml.common import Response
from core.app import rt
from db.connection import db_manager
from db.models import Image

# An image never changes once saved (a new upload gets a new id), so browsers can keep it for good.
# The CSP stops an SVG logo opened on its own from running scripts.
HEADERS = {
    'Cache-Control': 'public, max-age=31536000, immutable',
    'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
    'X-Content-Type-Options': 'nosniff',
}


@rt('/media/{image_id}')
async def get(image_id: int):
    """Uploaded speaker photos and sponsor logos (see utils/images.py)"""
    async with db_manager.AsyncSessionLocal() as db:
        image = await db.get(Image, image_id)
    if not image:
        return Response('Image not found', status_code=404)
    return Response(image.data, media_type=image.content_type, headers=HEADERS)
