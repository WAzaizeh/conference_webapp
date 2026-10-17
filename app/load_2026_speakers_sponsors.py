"""Point the 2026 speakers and sponsors at their image files in app/assets, and fill in bios and sponsor details.
Companion to load_2026_program.py (which creates the speakers by name but leaves photo and bio empty).

Images are files in the repo, named here:
  - speaker photos: assets/speaker_XXXX.png, cropped/resized to 200x200 (square, face centred)
  - sponsor logos:  assets/sponsor_<name>.<svg|png|jpg>, any shape (shown scaled to fit)

Usage (dry run without --apply):
    python load_2026_speakers_sponsors.py --apply [--overwrite]

Every speaker and sponsor listed here is pointed at its file, and the run flags any file that is missing
(the site shows the initials avatar / sponsor name until it's added) and any photo that still needs
resizing to 200x200. Replacing a file under the same name needs no re-run; a new file name does.

Image fields follow the files here, except images uploaded in the app (/admin/speakers, /admin/sponsors),
which are kept. Text fields (bio, description, links) are only filled when
empty, so hand edits are kept; pass --overwrite to replace them. Missing sponsors are added.
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

from PIL import Image

from core.assets import ASSETS_DIR as ASSETS
from utils.images import media_id

PHOTO_SIZE = (200, 200)

APPLY = '--apply' in sys.argv
OVERWRITE = '--overwrite' in sys.argv

# name -> photo number (file speaker_<number>.png) and bio. Names must match load_2026_program.py.
SPEAKERS = {
    'Sh. Yaser Birjas': dict(
        number=2601,
        bio="Imam of Valley Ranch Islamic Center in Irving, TX, and an instructor with AlMaghrib Institute. "
            "Originally from Palestine and born in Kuwait, he graduated valedictorian from the College of Shariah at the "
            "Islamic University of Madinah in 1996. He spent four years in Bosnia as a youth counselor and relief program "
            "aide, then served as Imam at the Islamic Center of El Paso and at Orland Park Prayer Center near Chicago. "
            "He holds a Master's in Adult Education and Training and speaks nationally on youth, marriage and parenting, "
            "offering pre-marital training, marriage coaching and conflict resolution. Father of four."),
    'Dr. Suzy Ismail': dict(
        number=2602,
        bio="Founding Director of Cornerstone, a nonprofit faith-based communication and counseling organization serving "
            "youth, families, marriage, identity, socioemotional wellness and refugee resilience. Her research, writing "
            "and speaking focus on where education, faith, communication and culture meet. She holds an M.A. in "
            "Communication and an M.Phil. and Ph.D. in Human Services, and is the author of \"Modern Muslim Marriage\", "
            "\"When Muslim Marriage Fails\" and \"9 to 5\". She has spoken at Harvard, Yale, Princeton, NYU and many "
            "other universities."),
    'Dr. Omar Husain': dict(
        number=2603,
        bio="Senior Fellow at Yaqeen Institute, Religious Director of the McKinney Islamic Association, and a licensed "
            "counselor at his practice, OH Counseling, where he offers individual, couples and family counseling. He "
            "graduated from the University of Illinois at Chicago in Information Sciences, studied Arabic and Islamic "
            "sciences in Toronto, and completed a degree in Islamic Studies and Arabic from Al-Azhar University. He "
            "holds a Ph.D. in Counselor Education and Supervision from UT San Antonio, and is an instructor with "
            "AlMaghrib Institute."),
    'Sr. Haleh Banani': dict(
        number=2604,
        bio="Holds a master's in clinical psychology and has provided faith-based counseling to Muslim clients worldwide "
            "since 1998. She founded The Mindful Hearts Academy, a global mentorship program for women, and co-created "
            "the 5 Pillars of Marriage Program with her husband. She has hosted shows on Al-Fajr TV and Huda TV and been "
            "featured on Al Jazeera. Her coaching combines cognitive behavioral exercises with "
            "Islamic principles across anxiety, depression, marriage and parenting. She holds an ijaza in Quran recitation."),
    'Ustadh Morad Awad': dict(
        number=2608,
        bio="Youth Director at East Plano Islamic Center (EPIC) since 2019. Raised in New Jersey in a Palestinian family, "
            "he earned a B.S. in Civil Engineering from NJIT, where he began Islamic outreach and youth programs. He "
            "studied Islamic sciences in Riyadh and Madinah, taught English and Islamic Studies at King Saud University "
            "and the College of Excellence in Madinah, and holds ijazas in Quran, Hadith, Fiqh and Usool al-Fiqh. He "
            "enjoys martial arts, travel and cooking, and is known for his kunafa."),
    'Sr. Youssra Kandil': dict(
        number=2606,
        bio="Motivational speaker, Quran teacher and contributor at Yaqeen Institute, focused on the Quran and Sunnah. "
            "She spent her early years in Kenya and Zimbabwe, then in Egypt, where she worked with Amr Khaled and "
            "appeared on the weekly show \"Parables of the Quran\". After settling in the United States she taught "
            "Quranic studies and Islamic history at an Islamic school, completed the Uwaylim scholarship track with "
            "Shaykh Shadee El Masry, and is working on memorizing the Quran. Her lectures are driven by the belief that "
            "everyone has a duty to pass on even a little knowledge."),
    'Sr. Mervat Farag': dict(
        number=2607,
        bio="Organizational Development Consultant who helps mission-driven organizations build strong governance, "
            "people and performance systems. As an educator and business trainer, she has designed and facilitated "
            "programs for executive leaders and mentors centered on faith-grounded service leadership. Through her "
            "mentorship of young professionals, she helps young Muslims connect faith with personal growth, "
            "relationships and leadership. She holds an MBA and is pursuing a Master of Divinity and Religious "
            "Leadership at TISA."),
}

# name -> logo file in assets and the other Sponsor columns
SPONSORS = {
    'IDEA': dict(
        logo='sponsor_idea.png',
        description='Islamic Development & Empowerment in America (formerly Islamic Relief USA), a humanitarian and development nonprofit.',
        website='https://development.org/'),
    'Mercy Without Limits': dict(
        logo='sponsor_mercy-without-limits.png',  # edited by hand from mwl.org/wp-content/uploads/2025/10/logo-header.svg
        description='Kansas-based 501(c)(3), established 2012, supporting orphans and widows in the Middle East and South Asia.',
        website='https://mwl.org/'),
    'Baitulmaal': dict(
        logo='sponsor_baitulmaal.png',  # replaced by hand with a larger transparent version
        description='US nonprofit delivering humanitarian aid worldwide regardless of faith or nationality.',
        website='https://baitulmaal.org/'),
    'Orphans in Need USA': dict(
        logo='sponsor_oinus.png',  # edited by hand from the oinusa.org social card
        description='Dublin, CA based nonprofit supporting orphans and vulnerable children.',
        website='https://oinusa.org/'),
    'Blue Fig International Market': dict(
        logo='sponsor_blue-fig.png',  # hand-prepared PNG
        description='Muslim-owned halal international grocery, 4101 E Park Blvd Ste 135, Plano TX 75074.',
        website=None,
        facebook='https://www.facebook.com/BlueFigMarket/'),
}


def photo_file(info: dict) -> Path:
    return ASSETS / f"speaker_{info['number']}.png"


def image_problem(path: Path, required_size: Optional[Tuple[int, int]] = None) -> str:
    """What's wrong with an image file ('' if it's fine): missing, unreadable, or not the required size"""
    if not path.exists():
        return 'MISSING'
    if path.suffix == '.svg':
        return ''
    try:
        with Image.open(path) as image:
            size = image.size
    except Exception:
        return 'UNREADABLE (not an image?)'
    if required_size and size != required_size:
        return f'RESIZE to {required_size[0]}x{required_size[1]} (now {size[0]}x{size[1]})'
    return ''


async def apply():
    from sqlalchemy import select
    from db.connection import db_manager
    from db.models import Speaker, Sponsor

    print(f'target database: {urlparse(db_manager.database_url).hostname}')
    problems = []
    async with db_manager.AsyncSessionLocal() as db:
        speakers = {s.name: s for s in (await db.execute(select(Speaker))).scalars()}
        for name, info in SPEAKERS.items():
            sp = speakers.get(name)
            if not sp:
                print(f'! speaker not in database (run load_2026_program.py first): {name}')
                continue
            photo = f'/assets/{photo_file(info).name}'
            problem = image_problem(photo_file(info), PHOTO_SIZE)
            if problem:
                problems.append(f'{photo_file(info).name}: {problem} — {name}')
            if media_id(sp.image_url):
                print(f'= photo {name}: uploaded in the app, kept')
            elif sp.image_url != photo:
                print(f'+ photo {name}: {photo}')
                sp.image_url = photo
            if info['bio'] and (OVERWRITE or not sp.bio):
                print(f'+ bio   {name}')
                sp.bio = info['bio']

        sponsors = {s.name: s for s in (await db.execute(select(Sponsor))).scalars()}
        for name, info in SPONSORS.items():
            logo_path = ASSETS / info['logo']
            fields = {k: v for k, v in info.items() if k != 'logo'}
            fields['image_url'] = f"/assets/{info['logo']}"
            problem = image_problem(logo_path)
            if problem:
                problems.append(f"{info['logo']}: {problem} — {name}")
            sponsor = sponsors.get(name)
            if sponsor is None:
                print(f'+ sponsor {name}')
                db.add(Sponsor(name=name, **fields))
                continue
            for field, value in fields.items():
                current = getattr(sponsor, field)
                if field == 'image_url' and media_id(current):
                    continue  # uploaded in the app
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

    if problems:
        print(f'\n⚠ {len(problems)} image(s) need attention (the site shows a fallback until fixed):')
        for problem in problems:
            print(f'  ⚠ {problem}')
    else:
        print('\n✓ all speaker photos and sponsor logos are in place')


if __name__ == '__main__':
    asyncio.run(apply())
