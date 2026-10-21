"""Fill in the 2026 speakers' bios and the sponsors' details (and add missing sponsors).
Companion to load_2026_program.py (which creates the speakers by name but leaves their bio empty).
Photos and logos are uploaded in the app (/admin/speakers, /admin/sponsors) and aren't touched here.

Usage (dry run without --apply):
    python load_2026_speakers_sponsors.py --apply [--overwrite]

Text fields (bio, description, links) are only filled when empty, so hand edits are kept;
pass --overwrite to replace them.
"""
import asyncio
import sys
from urllib.parse import urlparse

APPLY = '--apply' in sys.argv
OVERWRITE = '--overwrite' in sys.argv

# name -> bio. Names must match load_2026_program.py.
SPEAKERS = {
    'Sh. Yaser Birjas': dict(
        bio="Imam of Valley Ranch Islamic Center in Irving, TX, and an instructor with AlMaghrib Institute. "
            "Originally from Palestine and born in Kuwait, he graduated valedictorian from the College of Shariah at the "
            "Islamic University of Madinah in 1996. He spent four years in Bosnia as a youth counselor and relief program "
            "aide, then served as Imam at the Islamic Center of El Paso and at Orland Park Prayer Center near Chicago. "
            "He holds a Master's in Adult Education and Training and speaks nationally on youth, marriage and parenting, "
            "offering pre-marital training, marriage coaching and conflict resolution. Father of four."),
    'Dr. Suzy Ismail': dict(
        bio="Founding Director of Cornerstone, a nonprofit faith-based communication and counseling organization serving "
            "youth, families, marriage, identity, socioemotional wellness and refugee resilience. Her research, writing "
            "and speaking focus on where education, faith, communication and culture meet. She holds an M.A. in "
            "Communication and an M.Phil. and Ph.D. in Human Services, and is the author of \"Modern Muslim Marriage\", "
            "\"When Muslim Marriage Fails\" and \"9 to 5\". She has spoken at Harvard, Yale, Princeton, NYU and many "
            "other universities."),
    'Dr. Omar Husain': dict(
        bio="Senior Fellow at Yaqeen Institute, Religious Director of the McKinney Islamic Association, and a licensed "
            "counselor at his practice, OH Counseling, where he offers individual, couples and family counseling. He "
            "graduated from the University of Illinois at Chicago in Information Sciences, studied Arabic and Islamic "
            "sciences in Toronto, and completed a degree in Islamic Studies and Arabic from Al-Azhar University. He "
            "holds a Ph.D. in Counselor Education and Supervision from UT San Antonio, and is an instructor with "
            "AlMaghrib Institute."),
    'Sr. Haleh Banani': dict(
        bio="Holds a master's in clinical psychology and has provided faith-based counseling to Muslim clients worldwide "
            "since 1998. She founded The Mindful Hearts Academy, a global mentorship program for women, and co-created "
            "the 5 Pillars of Marriage Program with her husband. She has hosted shows on Al-Fajr TV and Huda TV and been "
            "featured on Al Jazeera. Her coaching combines cognitive behavioral exercises with "
            "Islamic principles across anxiety, depression, marriage and parenting. She holds an ijaza in Quran recitation."),
    'Ustadh Morad Awad': dict(
        bio="Youth Director at East Plano Islamic Center (EPIC) since 2019. Raised in New Jersey in a Palestinian family, "
            "he earned a B.S. in Civil Engineering from NJIT, where he began Islamic outreach and youth programs. He "
            "studied Islamic sciences in Riyadh and Madinah, taught English and Islamic Studies at King Saud University "
            "and the College of Excellence in Madinah, and holds ijazas in Quran, Hadith, Fiqh and Usool al-Fiqh. He "
            "enjoys martial arts, travel and cooking, and is known for his kunafa."),
    'Sr. Youssra Kandil': dict(
        bio="Motivational speaker, Quran teacher and contributor at Yaqeen Institute, focused on the Quran and Sunnah. "
            "She spent her early years in Kenya and Zimbabwe, then in Egypt, where she worked with Amr Khaled and "
            "appeared on the weekly show \"Parables of the Quran\". After settling in the United States she taught "
            "Quranic studies and Islamic history at an Islamic school, completed the Uwaylim scholarship track with "
            "Shaykh Shadee El Masry, and is working on memorizing the Quran. Her lectures are driven by the belief that "
            "everyone has a duty to pass on even a little knowledge."),
    'Sr. Mervat Farag': dict(
        bio="Organizational Development Consultant who helps mission-driven organizations build strong governance, "
            "people and performance systems. As an educator and business trainer, she has designed and facilitated "
            "programs for executive leaders and mentors centered on faith-grounded service leadership. Through her "
            "mentorship of young professionals, she helps young Muslims connect faith with personal growth, "
            "relationships and leadership. She holds an MBA and is pursuing a Master of Divinity and Religious "
            "Leadership at TISA."),
    'Ustadh Ozair Hasan': dict(
        bio="Head of Information Technology at Qalam Institute in Carrollton, Texas, and an Islamic scholar, educator and "
            "tech professional. Raised in Dayton, Ohio, he graduated from the intensive ʾĀlimiyyah Program at the Qalam "
            "Seminary, where he continues advanced specialization in Takhaṣṣuṣ & Iftāʾ (Islamic jurisprudence). He also "
            "holds a degree in Computer Science from the University of Texas at Dallas and specializes in AI engineering "
            "and cloud architecture."),
    'Hassaan Haq': dict(
        bio="Operations professional and entrepreneur based in the San Francisco Bay Area. He serves on the Core Team at "
            "Alif and is the founder of Chai Guy, a popular local catering and event initiative. He holds a degree in "
            "Computational and Applied Mathematics from San Jose State University and previously worked in Business "
            "Operations at tech companies like Cisco and ServiceNow. Alongside his corporate and entrepreneurial "
            "ventures, he completed studies in Classical Arabic and Islamic sciences at the Qalam Seminary."),
}

# name -> Sponsor columns
SPONSORS = {
    'IDEA': dict(
        description='Islamic Development & Empowerment in America (IDEA), formerly Islamic Relief USA, is a U.S. humanitarian and development nonprofit based in Alexandria, Virginia. Alongside emergency relief, it focuses on long-term development and empowerment, supporting communities across the United States and around the world.',
        website='https://development.org/',
        facebook='https://www.facebook.com/PoweredByIDEA/',
        instagram='https://www.instagram.com/developedbyidea/',
        linkedin='https://www.linkedin.com/company/poweredbyidea/',
        twitter='https://x.com/PoweredByIDEA',
        youtube='https://www.youtube.com/@PoweredByIDEA',
        tiktok='https://www.tiktok.com/@poweredbyidea',
        snapchat='https://www.snapchat.com/@poweredbyidea',
    ),
    'Mercy Without Limits': dict(
        description='Mercy Without Limits is a nonprofit based in Overland Park, Kansas, that began in 2012 helping orphans and widows affected by the crisis in Syria. Today it runs orphan sponsorship, widow support, food, water, shelter, healthcare, education and emergency aid in 12 countries, including Palestine, Syria, Lebanon, Jordan, Pakistan, Bangladesh and the United States.',
        website='https://mwl.org/',
        facebook='https://www.facebook.com/mwlimits',
        youtube='https://www.youtube.com/@MWLimits',
        twitter='https://x.com/mwlimits',
        instagram='https://www.instagram.com/mwlimits/',
        linkedin='https://www.linkedin.com/company/mwlimits-org/',
    ),
    'Baitulmaal': dict(
        description='Baitulmaal is a 501(c)(3) humanitarian nonprofit headquartered in Irving, Texas, delivering life-saving, life-sustaining and life-enriching aid to underserved people worldwide, regardless of faith or nationality. Its work spans emergency relief, food and water, healthcare, orphan support, winter relief, education and economic development in 16 countries across Africa, Asia, the Middle East and the United States.',
        website='https://baitulmaal.org/',
        facebook='https://www.facebook.com/baitulmaal/',
        twitter='https://twitter.com/baitulmaal',
        instagram='https://www.instagram.com/baitulmaal_usa/',
    ),
    'Orphans in Need USA': dict(
        description="Orphans in Need USA is a nonprofit based in Dublin, California, that supports orphans and widows in some of the world's poorest and conflict-affected regions. Through monthly orphan sponsorship, food parcels, school funding, medical care and its Orphans Village project, it gives children and their families consistent, long-term support.",
        website='https://oinusa.org/',
        facebook='https://www.facebook.com/OrphansinNeedUSA/',
        instagram='https://www.instagram.com/orphansinneedusa/',
        youtube='https://www.youtube.com/channel/UCC8rNDlDPn9bExw7-jzjebw',
        linkedin='https://www.linkedin.com/company/orphans-in-need-usa/',
    ),
    'TISA': dict(
        description='The Islamic Seminary of America (TISA) is a graduate-level Islamic seminary in Richardson, Texas, whose mission is to cultivate generations of doers and thinkers who lead from an Islamic paradigm. It offers an MA in Islamic Studies, a Master of Divinity, an M.Div. in Interreligious Chaplaincy and an Islamic Leadership and Management Certificate, with intensive and hybrid courses open to students across North America.',
        website='https://islamicseminary.us/',
        facebook='https://www.facebook.com/IslamicSeminaryofAmerica',
        twitter='https://twitter.com/ISeminaryofA',
        youtube='https://www.youtube.com/channel/UCllRF42Rq9IWlFOYI4lKhug/featured',
        linkedin='https://www.linkedin.com/company/the-islamic-seminary-of-america',
        instagram='https://instagram.com/islamicseminary',
    ),
    'Blue Fig International Market': dict(
        description='Blue Fig International Market is a family-owned, fully halal international grocery in East Plano with Muslim owners. It is known for its halal meat counter and deli, along with Mediterranean, Arabic, Indo-Pak and European groceries, fresh produce, breads and imported cheeses. Visit at 4101 E Park Blvd, Ste 135, Plano, TX 75074.',
        website=None,
        facebook='https://www.facebook.com/BlueFigMarket/',
        instagram='https://www.instagram.com/bluefigmarket/',
        tiktok='https://www.tiktok.com/@blue_fig_market_plano'),
}


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
            if info['bio'] and (OVERWRITE or not sp.bio):
                print(f'+ bio   {name}')
                sp.bio = info['bio']

        sponsors = {s.name: s for s in (await db.execute(select(Sponsor))).scalars()}
        for name, info in SPONSORS.items():
            sponsor = sponsors.get(name)
            if sponsor is None:
                print(f'+ sponsor {name}')
                db.add(Sponsor(name=name, **info))
                continue
            for field, value in info.items():
                current = getattr(sponsor, field)
                if value and (OVERWRITE or not current) and current != value:
                    print(f'~ {name}.{field}')
                    setattr(sponsor, field, value)

        if APPLY:
            await db.commit()
            print('committed')
        else:
            await db.rollback()
            print('dry run only (pass --apply to write)')


if __name__ == '__main__':
    asyncio.run(apply())
