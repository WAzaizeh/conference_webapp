"""Load the 4th Annual CYP Conference (Oct 24, 2026) program: speakers, agenda, prayer times.
Creates any missing tables first, so it also sets up a brand-new database.
Safe to re-run: existing speakers (by name) and sessions (by title + start time) are skipped.
Usage: python load_2026_program.py [--apply]   (dry run without --apply)
"""
import asyncio, sys
from urllib.parse import urlparse
from datetime import datetime, timezone
from sqlalchemy import select
from db.connection import db_manager
from db.models import Event, Speaker, PrayerTime, event_speakers
from utils.tags import tags_from_category

APPLY = '--apply' in sys.argv
LOCATION = 'GEM Academy & Facility'

YASER, SUZY, MORAD, MERVAT, OMAR, HALEH, YOUSSRA = (
    'Sh. Yaser Birjas', 'Dr. Suzy Ismail', 'Ustadh Morad Awad', 'Sr. Mervat Farag',
    'Dr. Omar Husain', 'Sr. Haleh Banani', 'Sr. Youssra Kandil',
)

def t(hhmm):
    # Conference wall-clock time tagged as UTC, matching how existing events are stored
    h, m = map(int, hhmm.split(':'))
    return datetime(2026, 10, 24, h, m, tzinfo=timezone.utc)

AGENDA = [
    ('11:00', '11:05', "Qur'an Recitation", 'MAIN', [], "Opening the day with the words of Allah."),
    ('11:05', '11:15', 'Welcome & Opening Remarks', 'MAIN', [], "MAS Dallas CYP leadership frames the day and the theme."),
    ('11:15', '12:15', 'Opening Keynote — Him & Her: Building Success at Every Stage', 'TALK', [YASER, SUZY],
     "A joint session introducing Allah's complementary vision for men and women. Empowering young Muslim men and women to build success at every stage — from college and career to marriage and parenthood — through faith-rooted guidance, practical tools, and dedicated tracks that turn individual growth into resilient families and a thriving community."),
    ('12:15', '12:20', 'Dhikr Break', 'BREAK', [], "A brief moment of remembrance before transitioning."),
    ('12:20', '13:20', 'Masculinity Track: Leadership Through Responsibility', 'WORKSHOP', [YASER],
     "Islamic manhood is often reduced to two words: protect and provide. But true leadership in the home and community requires a third, often-overlooked pillar: emotional maturity. This 50-minute interactive workshop moves beyond slogans to unpack what responsibility actually looks like in daily life — as a son, a future or current husband, a colleague, and a community member. Through guided discussion, real scenarios, and honest reflection, participants will walk away with a clearer, more grounded understanding of what it means to lead with strength and softness at the same time."),
    ('12:20', '13:20', 'Womanhood Track: Strength Through Faith', 'WORKSHOP', [SUZY],
     "This isn't a lecture — it's a guided, interactive workshop. True feminine strength isn't borrowed from external validation; it's rooted in faith. Through guided reflection, small-group discussion, and real scenarios, participants will unpack what it means to walk in confident identity (izzah) while nurturing others with intention, not self-erasure."),
    ('13:20', '13:25', 'Dhikr Break', 'BREAK', [], "A brief moment of remembrance before transitioning."),
    ('13:25', '14:10', 'Masculinity Track: Small-Group Reflection', 'ACTIVITY', [MORAD],
     "Facilitated conversation on emotional maturity, protecting, and providing.\n\nThis is a guided, small-group conversation — not a lecture — where young Muslim men can speak honestly about what protecting, providing, and emotional maturity actually look like in their own lives. Rather than presenting content, the facilitator poses open questions and creates a safe space for brothers to reflect, share, and learn from each other's real experiences. The goal is authentic dialogue, not answers handed down from the front of the room."),
    ('13:25', '14:10', 'Womanhood Track: Small-Group Reflection', 'ACTIVITY', [MERVAT],
     "Facilitated conversation on identity, nurturing, and balancing aspirations.\n\nThis is a guided, small-group conversation — not a lecture — where young Muslim women can speak honestly about who they are, who they care for, and what they're striving toward, without feeling like these three things have to compete with one another. Rather than presenting content, the facilitator poses open questions and creates a safe space for sisters to reflect, share, and learn from each other's real experiences. The goal is authentic dialogue, not answers handed down from the front of the room."),
    ('14:10', '15:40', 'Dhuhr Prayer & Lunch', 'PRAYER', [], "Congregational prayer followed by a shared meal (90 minutes)."),
    ('15:40', '15:45', 'Dhikr Break', 'BREAK', [], "A brief moment of remembrance before the panel."),
    ('15:45', '16:45', 'Marriage: Real Life not Reel Life', 'TALK', [OMAR, HALEH],
     "Social media, dating culture, and endless content have quietly rewritten what people expect from marriage — instant gratification, constant validation, comparison to curated \"highlight reels,\" and an addiction to novelty that leaves real, everyday marriage feeling disappointing by comparison. Dr. Omar Husain and Sr. Haleh Banani each bring 20 minutes addressing this from their own vantage point — confronting the illusion and offering grounded, faith-rooted tools to protect real marriages from a culture that was never designed to help them succeed. The session closes with a joint Q&A, giving attendees space to ask what's genuinely on their minds."),
    ('15:45', '16:45', 'Emotional Intelligence & Healthy Relationships: Family, Friends, and Beyond', 'TALK', [YOUSSRA, MERVAT],
     "Equipping every CYP — students, professionals, and business owners alike — with practical emotional intelligence and communication tools for the relationships they navigate daily, whether at school, work, or in business."),
    ('16:50', '17:30', 'Masculinity Track: Spiritual Leadership', 'WORKSHOP', [OMAR],
     "Becoming the husband, father, and community leader Islam calls men to be.\n\nEvery man wears multiple hats throughout his life — son, brother, husband, father, community leader — yet few are ever taught what Islam actually expects of him in each role. This workshop moves past vague ideals and into concrete spiritual leadership: how a man leads with taqwa (God-consciousness) at home, among his brothers, and in his community, long before he ever leads a family. Participants will walk away with a clearer sense of what it means to lead each relationship with faith, not just effort."),
    ('16:50', '17:30', 'Womanhood Track: Her Leadership Journey', 'WORKSHOP', [HALEH],
     "Becoming the daughter, sister, wife, mother, and community builder Islam honors.\n\nEvery woman holds roles of profound influence throughout her life — daughter, sister, wife, mother, community builder — yet few are ever taught what Islam actually honors in each of these roles. This workshop moves past vague ideals and into concrete spiritual leadership: how a woman leads with taqwa (God-consciousness) at home, among her sisters, and in her community, long before any formal title is given to her. Participants will walk away with a clearer sense of what it means to nurture each relationship with faith, not just effort."),
    ('17:30', '18:10', 'Asr Prayer', 'PRAYER', [], "Congregational prayer break (40 minutes)."),
    ('18:10', '19:00', 'The Parenting Challenges No One Warned You About', 'TALK', [SUZY],
     "Nobody hands new parents a manual for raising kids in today's world — a world their own parents never had to navigate. Young CYP parents are juggling toddlers and screens, sleep deprivation and social media comparison, Islamic identity and Western schooling, all while building careers and marriages at the same time. This session names the real, often unspoken challenges facing young Muslim parents today and offers practical, faith-rooted strategies to parent with intention instead of just surviving."),
    ('18:10', '19:00', 'More Than Yourself, Beyond Your Lifetime', 'TALK', [YOUSSRA],
     "Most of us live inside three small circles: ourselves, our families, and our personal ambitions. This talk challenges that boundary. Drawing from the Islamic understanding of legacy — Sadaqah Jariyah, beneficial knowledge, and righteous impact — this session invites every CYP to ask a harder question than \"What do I want out of life?\" It asks: \"What will remain after I'm gone?\" By the end of the talk, attendees won't just be inspired — they'll walk away with a practical blueprint for living with intention, contributing beyond themselves, and building something that outlives them."),
    ('19:00', '19:25', 'Maghrib Prayer', 'PRAYER', [], "Congregational prayer break (25 minutes)."),
    ('19:25', '19:55', 'Closing Keynote & Commitment', 'TALK', [MORAD],
     "As the day draws to a close, this keynote weaves together everything explored across the Masculinity, Womanhood, Marriage, and Parenting tracks into one unified message: building success at every stage is not a collection of separate roles, but a single, intentional journey rooted in faith. Rather than introducing new content, this session reflects back what CYPs have discussed, discovered, and committed to throughout the day — and challenges every attendee to leave not just inspired, but accountable. It closes with a clear, practical call to action, so no one walks out the door without a concrete next step."),
    ('19:55', '20:00', "Closing Du'a & Group Photo", 'MAIN', [], "Ending the day in gratitude and unity."),
]

# name -> (adhan, iqama) in the existing 24h "HH:MM" format; iqama = congregational slot on the program
PRAYERS = {'DHUHR': ('13:12', '14:10'), 'ASR': ('16:19', '17:30'), 'MAGHRIB': ('18:45', '19:00')}


async def main():
    print(f'target database: {urlparse(db_manager.database_url).hostname}')
    if APPLY:
        await db_manager.create_tables()  # no-op for tables that already exist
    async with db_manager.AsyncSessionLocal() as db:
        # Speakers
        names = sorted({n for *_, sp, _ in AGENDA for n in sp})
        existing = {s.name: s for s in (await db.execute(select(Speaker))).scalars()}
        for name in names:
            if name in existing:
                print(f'speaker exists: {name}')
            else:
                print(f'+ speaker: {name}')
                if APPLY:
                    sp = Speaker(name=name)
                    db.add(sp)
                    await db.flush()
                    existing[name] = sp

        # Sessions
        current = {(e.title, e.start_time) for e in (await db.execute(select(Event))).scalars()}
        for start, end, title, cat, speakers, desc in AGENDA:
            if (title, t(start)) in current:
                print(f'session exists: {start} {title}')
                continue
            print(f'+ session: {start}-{end} {tags_from_category(cat, title)} {title}  {speakers or ""}')
            if APPLY:
                ev = Event(title=title, description=desc, start_time=t(start), end_time=t(end), location=LOCATION, tags=tags_from_category(cat, title))
                db.add(ev)
                await db.flush()
                for name in speakers:
                    await db.execute(event_speakers.insert().values(event_id=ev.id, speaker_id=existing[name].id))

        # Prayer times
        rows = {p.name: p for p in (await db.execute(select(PrayerTime))).scalars()}
        for name, (time, iqama) in PRAYERS.items():
            p = rows.get(name)
            print(f'~ prayer {name}: {p.time if p else None}/{p.iqama if p else None} -> {time}/{iqama}')
            if APPLY:
                if p:
                    p.time, p.iqama = time, iqama
                else:
                    db.add(PrayerTime(name=name, time=time, iqama=iqama))

        if APPLY:
            await db.commit()
            print('committed')
        else:
            print('dry run only (pass --apply to write)')

asyncio.run(main())
