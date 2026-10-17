"""Uploaded images: resize to what the site shows, store in the database, and point a record at it.
Speaker photos become squares; sponsor logos keep their shape. Served by routes/media.py."""
from io import BytesIO
from typing import Optional, Tuple

from PIL import Image as PILImage, ImageOps
from sqlalchemy import delete

from db.models import Image

MEDIA_PREFIX = '/media/'
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
PHOTO_SIZE = 400        # speaker photos: square, sharp on the detail page
LOGO_MAX_SIDE = 800     # sponsor logos: fit within this box, shape kept


def _encode(image: PILImage.Image) -> Tuple[bytes, str]:
    """PNG when the image has transparency (logos), JPEG otherwise (smaller for photos)"""
    out = BytesIO()
    if image.mode in ('RGBA', 'LA', 'P') and image.convert('RGBA').getextrema()[3][0] < 255:
        image.convert('RGBA').save(out, 'PNG', optimize=True)
        return out.getvalue(), 'image/png'
    image.convert('RGB').save(out, 'JPEG', quality=88, optimize=True)
    return out.getvalue(), 'image/jpeg'


def _is_svg(data: bytes) -> bool:
    head = data[:1024].lstrip().lower()
    return head.startswith(b'<svg') or (head.startswith(b'<?xml') and b'<svg' in data[:4096].lower())


def prepare_upload(data: bytes, kind: str) -> Tuple[bytes, str]:
    """Resize an uploaded file for `kind` ('photo' or 'logo'); raises ValueError with a message for the form"""
    if not data:
        raise ValueError('The uploaded file is empty.')
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError('Images must be under 10 MB.')
    if kind == 'logo' and _is_svg(data):
        return data, 'image/svg+xml'  # vector logos are kept as-is
    try:
        image = PILImage.open(BytesIO(data))
        image.load()
    except Exception:
        raise ValueError('That file is not an image (use PNG, JPEG, WebP' + (' or SVG).' if kind == 'logo' else ').'))
    image = ImageOps.exif_transpose(image)  # phone photos: apply the rotation they were taken with
    if kind == 'photo':
        image = ImageOps.fit(image.convert('RGBA'), (PHOTO_SIZE, PHOTO_SIZE), PILImage.LANCZOS)
    else:
        image.thumbnail((LOGO_MAX_SIDE, LOGO_MAX_SIDE), PILImage.LANCZOS)
    return _encode(image)


async def save_image(db, data: bytes, content_type: str) -> str:
    """Store an image and return its URL (the session is flushed, not committed)"""
    image = Image(data=data, content_type=content_type)
    db.add(image)
    await db.flush()
    return f'{MEDIA_PREFIX}{image.id}'


def media_id(url: Optional[str]) -> Optional[int]:
    """The image id behind a /media/<id> URL, or None for any other URL"""
    if url and url.startswith(MEDIA_PREFIX) and url[len(MEDIA_PREFIX):].isdigit():
        return int(url[len(MEDIA_PREFIX):])
    return None


async def replace_image(db, record, new_url: Optional[str]):
    """Point record.image_url at new_url and delete the uploaded image it used before, if any"""
    old_id = media_id(record.image_url)
    record.image_url = new_url
    if old_id and old_id != media_id(new_url):
        await db.execute(delete(Image).where(Image.id == old_id))
