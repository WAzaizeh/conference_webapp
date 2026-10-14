"""Fill in the 2026 speaker photos/bios and the sponsor list, using image files kept in app/assets.
Companion to load_2026_program.py (which creates the speakers by name but leaves photo and bio empty).

Images live in the repo instead of being linked from other websites, so every page shows the same,
consistently sized files. Steps:

  1. Download the source images (needs Pillow for this step only):
         uv run --with pillow python load_2026_speakers_sponsors.py --download
     Speaker photos are saved as assets/speaker_XXXX.png at their original size, sponsor logos as
     assets/sponsor_<name>.<ext>. Files that already exist are never overwritten.
  2. Manual step: crop every speaker photo to exactly 200x200 (square, face centred) and save it as
     PNG under the same name. Sponsor logos need no crop; they are shown in a fixed white box.
  3. Update the database (dry run without --apply):
         python load_2026_speakers_sponsors.py --apply [--overwrite]
     A photo is linked only once its file is a 200x200 PNG; missing or uncropped ones are listed and
     those speakers show the initials avatar until it's ready.

Image fields always follow the files here. Text fields (bio, description, links) are only filled when
empty, so hand edits are kept; pass --overwrite to replace them. Missing sponsors are added.

Sources are in the organizers' fill-ins doc (MASCYP 2026 Fill-ins). Known gaps: Sr. Mervat Farag has no
public bio; OINUS's logo is cut from its social card and
Baitulmaal's is small (150x115) — replace the files if HD versions come from the organizers.
"""
import asyncio
import struct
import sys
import urllib.request
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

ASSETS = Path(__file__).parent / 'assets'
PHOTO_SIZE = (200, 200)
PLACEHOLDER_HOST = 'ui-avatars.com'  # generated initials avatars must never be stored

DOWNLOAD = '--download' in sys.argv
APPLY = '--apply' in sys.argv
OVERWRITE = '--overwrite' in sys.argv

# name -> photo number (file speaker_<number>.png), photo source, bio. Names must match load_2026_program.py.
SPEAKERS = {
    'Sh. Yaser Birjas': dict(
        number=2601,
        source='https://c7c8edde.delivery.rocketcdn.me/wp-content/uploads/YaserBirjas-1.jpg',
        bio="Imam of Valley Ranch Islamic Center in Irving, TX, and an instructor with AlMaghrib Institute. "
            "Originally from Palestine and born in Kuwait, he graduated valedictorian from the College of Shariah at the "
            "Islamic University of Madinah in 1996. He spent four years in Bosnia as a youth counselor and relief program "
            "aide, then served as Imam at the Islamic Center of El Paso and at Orland Park Prayer Center near Chicago. "
            "He holds a Master's in Adult Education and Training and speaks nationally on youth, marriage and parenting, "
            "offering pre-marital training, marriage coaching and conflict resolution. Father of four."),
    'Dr. Suzy Ismail': dict(
        number=2602,
        source='https://s3.amazonaws.com/berkley-center/SuzyIsmail.jpg',
        bio="Founding Director of Cornerstone, a nonprofit faith-based communication and counseling organization serving "
            "youth, families, marriage, identity, socioemotional wellness and refugee resilience. Her research, writing "
            "and speaking focus on where education, faith, communication and culture meet. She holds an M.A. in "
            "Communication and an M.Phil. and Ph.D. in Human Services, and is the author of \"Modern Muslim Marriage\", "
            "\"When Muslim Marriage Fails\" and \"9 to 5\". She has spoken at Harvard, Yale, Princeton, NYU and many "
            "other universities."),
    'Dr. Omar Husain': dict(
        number=2603,
        source='https://cdn.yaqeeninstitute.org/wp-content/uploads/2020/04/omar-husain.jpg',
        bio="Senior Fellow at Yaqeen Institute, Religious Director of the McKinney Islamic Association, and a licensed "
            "counselor at his practice, OH Counseling, where he offers individual, couples and family counseling. He "
            "graduated from the University of Illinois at Chicago in Information Sciences, studied Arabic and Islamic "
            "sciences in Toronto, and completed a degree in Islamic Studies and Arabic from Al-Azhar University. He "
            "holds a Ph.D. in Counselor Education and Supervision from UT San Antonio, and is an instructor with "
            "AlMaghrib Institute."),
    'Sr. Haleh Banani': dict(
        number=2604,
        source='https://halehbanani.com/wp-content/uploads/2019/12/haleh-website-portrait-0035.png',
        bio="Holds a master's in clinical psychology and has provided faith-based counseling to Muslim clients worldwide "
            "since 1998. She founded The Mindful Hearts Academy, a global mentorship program for women, and co-created "
            "the 5 Pillars of Marriage Program with her husband. She has hosted shows on Al-Fajr TV and Huda TV and been "
            "featured on Al Jazeera. Her coaching combines cognitive behavioral exercises with "
            "Islamic principles across anxiety, depression, marriage and parenting. She holds an ijaza in Quran recitation."),
    'Ustadh Morad Awad': dict(
        number=2605,
        source='https://dstworldtravel.com/wp-content/uploads/2022/01/Morad.jpg',
        bio="Youth Director at East Plano Islamic Center (EPIC) since 2019. Raised in New Jersey in a Palestinian family, "
            "he earned a B.S. in Civil Engineering from NJIT, where he began Islamic outreach and youth programs. He "
            "studied Islamic sciences in Riyadh and Madinah, taught English and Islamic Studies at King Saud University "
            "and the College of Excellence in Madinah, and holds ijazas in Quran, Hadith, Fiqh and Usool al-Fiqh. He "
            "enjoys martial arts, travel and cooking, and is known for his kunafa."),
    'Sr. Youssra Kandil': dict(
        number=2606,
        source='https://cdn.yaqeeninstitute.org/wp-content/uploads/2023/03/IMG_4061-scaled-e1679857496935.jpeg',
        bio="Motivational speaker, Quran teacher and contributor at Yaqeen Institute, focused on the Quran and Sunnah. "
            "She spent her early years in Kenya and Zimbabwe, then in Egypt, where she worked with Amr Khaled and "
            "appeared on the weekly show \"Parables of the Quran\". After settling in the United States she taught "
            "Quranic studies and Islamic history at an Islamic school, completed the Uwaylim scholarship track with "
            "Shaykh Shadee El Masry, and is working on memorizing the Quran. Her lectures are driven by the belief that "
            "everyone has a duty to pass on even a little knowledge."),
    'Sr. Mervat Farag': dict(
        number=2607,
        source='https://baitulmaal.org/nitropack_static/mNaOYkwndABKrOlhekcrZgWGezLAAXtD/assets/images/optimized/'
               'rev-85e2440/baitulmaal.org/wp-content/uploads/2024/09/Our-People-MF-copy.jpeg',
        bio=None),  # no public bio yet
}

# name -> logo file in assets, logo source (None: file provided by hand), and other Sponsor columns
SPONSORS = {
    'IDEA': dict(
        logo='sponsor_idea.svg',
        source='https://development.org/logo/IDEA_LOGO_HORIZONTAL_FULL.svg',
        description='Islamic Development & Empowerment in America (formerly Islamic Relief USA), a humanitarian and development nonprofit.',
        website='https://development.org/'),
    'Mercy Without Limits': dict(
        logo='sponsor_mercy-without-limits.svg',
        source='https://mwl.org/wp-content/uploads/2025/10/logo-header.svg',  # colored version (logo-l.svg is white)
        description='Kansas-based 501(c)(3), established 2012, supporting orphans and widows in the Middle East and South Asia.',
        website='https://mwl.org/'),
    'Baitulmaal': dict(
        logo='sponsor_baitulmaal.png',
        source='https://baitulmaal.org/wp-content/uploads/2023/05/baitulmaal-black-white-WEB.png',
        description='US nonprofit delivering humanitarian aid worldwide regardless of faith or nationality.',
        website='https://baitulmaal.org/'),
    'Orphans in Need USA': dict(
        logo='sponsor_oinus.jpg',  # from the oinusa.org social card
        source=None,
        description='Dublin, CA based nonprofit supporting orphans and vulnerable children.',
        website='https://oinusa.org/'),
    'Blue Fig International Market': dict(
        logo='sponsor_blue-fig.jpg',  # Facebook page profile picture
        source=None,
        description='Muslim-owned halal international grocery, 4101 E Park Blvd Ste 135, Plano TX 75074.',
        website=None,
        facebook='https://www.facebook.com/BlueFigMarket/'),
}


def photo_file(info: dict) -> Path:
    return ASSETS / f"speaker_{info['number']}.png"


def png_size(path: Path):
    """(width, height) of a PNG file, or None if it is missing or not a PNG"""
    if not path.exists():
        return None
    header = path.read_bytes()[:24]
    if header[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    return struct.unpack('>II', header[16:24])


def photo_status(info: dict) -> str:
    size = png_size(photo_file(info))
    if not photo_file(info).exists():
        return 'missing'
    if size is None:
        return 'not a PNG'
    return 'ready' if size == PHOTO_SIZE else f'needs crop ({size[0]}x{size[1]})'


# ---- Step 1: download ----

def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def download():
    from PIL import Image  # only needed here: uv run --with pillow ...

    def save_photo(data: bytes, target: Path) -> str:
        image = Image.open(BytesIO(data))
        image.convert('RGBA' if image.mode in ('RGBA', 'LA', 'P') else 'RGB').save(target, 'PNG')
        return f'{image.width}x{image.height}, crop to 200x200'

    def save_logo(data: bytes, target: Path) -> str:
        target.write_bytes(data)
        return 'logo'

    jobs = [(name, photo_file(info), info['source'], save_photo) for name, info in SPEAKERS.items()]
    jobs += [(name, ASSETS / info['logo'], info['source'], save_logo) for name, info in SPONSORS.items()]
    for name, target, source, save in jobs:
        if target.exists() or not source:
            print(f"  skip {target.name} ({'exists' if target.exists() else 'no source, add by hand'}) — {name}")
            continue
        try:
            print(f"+ {target.name} ({save(fetch(source), target)}) — {name}")
        except Exception as exc:  # keep going; a broken link shouldn't stop the other downloads
            print(f"! {target.name} failed ({exc}) — {name}: find another source or add the file by hand")


# ---- Step 3: database ----

def is_managed_elsewhere(url) -> bool:
    """True for values this script should replace: empty, linked from another site, or a generated avatar"""
    return not url or not url.startswith('/assets/') or PLACEHOLDER_HOST in url


async def apply():
    from sqlalchemy import select
    from db.connection import db_manager
    from db.models import Speaker, Sponsor

    print(f'target database: {urlparse(db_manager.database_url).hostname}')
    async with db_manager.AsyncSessionLocal() as db:
        speakers = {s.name: s for s in (await db.execute(select(Speaker))).scalars()}
        for name, info in SPEAKERS.items():
            sp = speakers.get(name)
            if not sp:
                print(f'! speaker not in database (run load_2026_program.py first): {name}')
                continue
            status = photo_status(info)
            photo = f'/assets/{photo_file(info).name}'
            if status == 'ready':
                if sp.image_url != photo:
                    print(f'+ photo {name}: {photo}')
                    sp.image_url = photo
            else:
                print(f'! photo {name}: {photo_file(info).name} {status}; showing initials')
                if sp.image_url and is_managed_elsewhere(sp.image_url):
                    sp.image_url = None
            if info['bio'] and (OVERWRITE or not sp.bio):
                print(f'+ bio   {name}')
                sp.bio = info['bio']

        sponsors = {s.name: s for s in (await db.execute(select(Sponsor))).scalars()}
        for name, info in SPONSORS.items():
            logo_path = ASSETS / info['logo']
            fields = {k: v for k, v in info.items() if k not in ('logo', 'source')}
            fields['image_url'] = f"/assets/{info['logo']}" if logo_path.exists() else None
            if not logo_path.exists():
                print(f"! logo {name}: {info['logo']} missing")
            sponsor = sponsors.get(name)
            if sponsor is None:
                print(f'+ sponsor {name}')
                db.add(Sponsor(name=name, **fields))
                continue
            for field, value in fields.items():
                current = getattr(sponsor, field)
                replace = (field == 'image_url' and current != value) or (value and (OVERWRITE or not current))
                if replace and current != value:
                    print(f'~ {name}.{field}')
                    setattr(sponsor, field, value)

        if APPLY:
            await db.commit()
            print('committed')
        else:
            await db.rollback()
            print('dry run only (pass --apply to write)')


if __name__ == '__main__':
    if DOWNLOAD:
        download()
    else:
        asyncio.run(apply())
