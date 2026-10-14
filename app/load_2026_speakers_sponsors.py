"""Fill in the 2026 speaker photos/bios and the sponsor list.
Companion to load_2026_program.py (which creates the speakers by name but leaves photo and bio empty).
Speakers are matched by name and only EMPTY fields are filled, so hand edits made in /admin are kept;
pass --overwrite to replace them. Sponsors are matched by name: missing ones are added, existing ones
are left alone (or updated with --overwrite).
Usage: python load_2026_speakers_sponsors.py [--apply] [--overwrite]   (dry run without --apply)

Sources for every entry are in the organizers' fill-ins doc (MASCYP 2026 Fill-ins). Known gaps:
Sr. Mervat Farag has no public bio or photo; OINUS and Blue Fig have no public logo (Kamran at MAS has HD versions).
"""
import asyncio, sys
from urllib.parse import urlparse
from sqlalchemy import select
from db.connection import db_manager
from db.models import Speaker, Sponsor

APPLY = '--apply' in sys.argv
OVERWRITE = '--overwrite' in sys.argv

# name -> (image_url, bio). Names must match load_2026_program.py exactly.
SPEAKERS = {
    'Sh. Yaser Birjas': (
        'https://c7c8edde.delivery.rocketcdn.me/wp-content/uploads/YaserBirjas-1.jpg',
        "Imam of Valley Ranch Islamic Center in Irving, TX, and an instructor with AlMaghrib Institute. "
        "Originally from Palestine and born in Kuwait, he graduated valedictorian from the College of Shariah at the "
        "Islamic University of Madinah in 1996. He spent four years in Bosnia as a youth counselor and relief program "
        "aide, then served as Imam at the Islamic Center of El Paso and at Orland Park Prayer Center near Chicago. "
        "He holds a Master's in Adult Education and Training and speaks nationally on youth, marriage and parenting, "
        "offering pre-marital training, marriage coaching and conflict resolution. Father of four."),
    'Dr. Suzy Ismail': (
        'https://s3.amazonaws.com/berkley-center/SuzyIsmail.jpg',
        "Founding Director of Cornerstone, a nonprofit faith-based communication and counseling organization serving "
        "youth, families, marriage, identity, socioemotional wellness and refugee resilience. Her research, writing "
        "and speaking focus on where education, faith, communication and culture meet. She holds an M.A. in "
        "Communication and an M.Phil. and Ph.D. in Human Services, and is the author of \"Modern Muslim Marriage\", "
        "\"When Muslim Marriage Fails\" and \"9 to 5\". She has spoken at Harvard, Yale, Princeton, NYU and many "
        "other universities."),
    'Dr. Omar Husain': (
        'https://cdn.yaqeeninstitute.org/wp-content/uploads/2020/04/omar-husain.jpg',
        "Senior Fellow at Yaqeen Institute, Religious Director of the McKinney Islamic Association, and a licensed "
        "counselor at his practice, OH Counseling, where he offers individual, couples and family counseling. He "
        "graduated from the University of Illinois at Chicago in Information Sciences, studied Arabic and Islamic "
        "sciences in Toronto, and completed a degree in Islamic Studies and Arabic from Al-Azhar University. He is a "
        "holds a Ph.D. in Counselor Education and Supervision from UT San Antonio, and is an instructor with "
        "AlMaghrib Institute."),
    'Sr. Haleh Banani': (
        'https://halehbanani.com/wp-content/uploads/2019/12/haleh-website-portrait-0035.png',
        "Holds a master's in clinical psychology and has provided faith-based counseling to Muslim clients worldwide "
        "since 1998. She founded The Mindful Hearts Academy, a global mentorship program for women, and co-created "
        "the 5 Pillars of Marriage Program with her husband. She has hosted shows on Al-Fajr TV and Huda TV and been "
        "featured on Al Jazeera. Her coaching combines cognitive behavioral exercises with "
        "Islamic principles across anxiety, depression, marriage and parenting. She holds an ijaza in Quran recitation."),
    'Ustadh Morad Awad': (
        'https://dstworldtravel.com/wp-content/uploads/2022/01/Morad.jpg',
        "Youth Director at East Plano Islamic Center (EPIC) since 2019. Raised in New Jersey in a Palestinian family, "
        "he earned a B.S. in Civil Engineering from NJIT, where he began Islamic outreach and youth programs. He "
        "studied Islamic sciences in Riyadh and Madinah, taught English and Islamic Studies at King Saud University "
        "and the College of Excellence in Madinah, and holds ijazas in Quran, Hadith, Fiqh and Usool al-Fiqh. He "
        "enjoys martial arts, travel and cooking, and is known for his kunafa."),
    'Sr. Youssra Kandil': (
        'https://cdn.yaqeeninstitute.org/wp-content/uploads/2023/03/IMG_4061-scaled-e1679857496935.jpeg',
        "Motivational speaker, Quran teacher and contributor at Yaqeen Institute, focused on the Quran and Sunnah. "
        "She spent her early years in Kenya and Zimbabwe, then in Egypt, where she worked with Amr Khaled and "
        "appeared on the weekly show \"Parables of the Quran\". After settling in the United States she taught "
        "Quranic studies and Islamic history at an Islamic school, completed the Uwaylim scholarship track with "
        "Shaykh Shadee El Masry, and is working on memorizing the Quran. Her lectures are driven by the belief that "
        "everyone has a duty to pass on even a little knowledge."),
    # 'Sr. Mervat Farag': no public bio or photo found; fill in from the organizers.
}

# name -> dict of Sponsor columns
SPONSORS = {
    'IDEA': dict(
        description='Islamic Development & Empowerment in America (formerly Islamic Relief USA), a humanitarian and development nonprofit.',
        website='https://development.org/',
        image_url='https://development.org/logo/IDEA_LOGO_HORIZONTAL_FULL.svg'),
    'Mercy Without Limits': dict(
        description='Kansas-based 501(c)(3), established 2012, supporting orphans and widows in the Middle East and South Asia.',
        website='https://mwl.org/',
        image_url='https://mwl.org/wp-content/uploads/2025/10/logo-l.svg'),
    'Baitulmaal': dict(
        description='US nonprofit delivering humanitarian aid worldwide regardless of faith or nationality.',
        website='https://baitulmaal.org/',
        image_url='https://baitulmaal.org/wp-content/uploads/2023/05/baitulmaal-black-white-WEB.png'),
    'Orphans in Need USA': dict(
        description='Dublin, CA based nonprofit supporting orphans and vulnerable children.',
        website='https://oinusa.org/',
        image_url='/assets/sponsor-oinus.jpg'),  # from oinusa.org social card (600x315); swap for HD file from Kamran if provided
    'Blue Fig International Market': dict(
        description='Muslim-owned halal international grocery, 4101 E Park Blvd Ste 135, Plano TX 75074.',
        website=None,
        facebook='https://www.facebook.com/BlueFigMarket/',
        image_url='/assets/sponsor-blue-fig.jpg'),  # Facebook page profile picture (960x960)
}


async def main():
    print(f'target database: {urlparse(db_manager.database_url).hostname}')
    async with db_manager.AsyncSessionLocal() as db:
        existing = {s.name: s for s in (await db.execute(select(Speaker))).scalars()}
        for name, (image_url, bio) in SPEAKERS.items():
            sp = existing.get(name)
            if not sp:
                print(f'! speaker not in database (run load_2026_program.py first): {name}')
                continue
            for field, value in (('image_url', image_url), ('bio', bio)):
                current = getattr(sp, field)
                if current and not OVERWRITE:
                    print(f'  keep {name}.{field} (already set)')
                else:
                    print(f'+ set  {name}.{field}')
                    if APPLY:
                        setattr(sp, field, value)

        sponsors = {s.name: s for s in (await db.execute(select(Sponsor))).scalars()}
        for name, fields in SPONSORS.items():
            if name in sponsors:
                if OVERWRITE:
                    print(f'~ update sponsor: {name}')
                    if APPLY:
                        for k, v in fields.items():
                            setattr(sponsors[name], k, v)
                else:
                    print(f'  sponsor exists: {name}')
            else:
                print(f'+ sponsor: {name}')
                if APPLY:
                    db.add(Sponsor(name=name, **fields))

        if APPLY:
            await db.commit()
            print('committed')
        else:
            print('dry run only (pass --apply to write)')

asyncio.run(main())
