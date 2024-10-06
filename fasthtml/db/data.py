import pandas as pd
from datetime import datetime
from .schemas import EventOut, EVENT_CATEGORY
from .schemas import (
    EventOut,
    SpeakerOut,
    EVENT_CATEGORY,
    PrayerTime,
    PRAYER_NAME,
    SponsorOut,
)

SESSIONS = [
            EventOut(id=1, title='Quran Recitation & Welcome', description='', start_time=datetime(2024, 10, 12, 10, 00), end_time=datetime(2024, 10, 12, 10, 15), location='room 1', category=EVENT_CATEGORY.MAIN),
            EventOut(id=2, title='Talk#1', description='', start_time=datetime(2024, 10, 12, 10, 15), end_time=datetime(2024, 10, 12, 11, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[4]),
            EventOut(id=3, title='Talk#2', description='', start_time=datetime(2024, 10, 12, 11, 00), end_time=datetime(2024, 10, 12, 11, 45), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[5]),
            EventOut(id=4, title='Trivia Break & Prizes', description='', start_time=datetime(2024, 10, 12, 11, 45), end_time=datetime(2024, 10, 12, 12, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=5, title='Talk#3', description='', start_time=datetime(2024, 10, 12, 12, 00), end_time=datetime(2024, 10, 12, 12, 45), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[7]),
            EventOut(id=6, title='Youth Lightning Talk-1', description='', start_time=datetime(2024, 10, 12, 12, 45), end_time=datetime(2024, 10, 12, 13, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=7, title='Break [Lunch & Dhuhr Prayer]', description='', start_time=datetime(2024, 10, 12, 13, 00), end_time=datetime(2024, 10, 12, 14, 30), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=8, title='Trivia Break & Prizes Sponsor Presentation #1', description='', start_time=datetime(2024, 10, 12, 14, 30), end_time=datetime(2024, 10, 12, 14, 45), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=9, title='Talk#4', description='', start_time=datetime(2024, 10, 12, 14, 45), end_time=datetime(2024, 10, 12, 15, 30), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[2]),
            EventOut(id=10, title='Talk#5', description='', start_time=datetime(2024, 10, 12, 15, 30), end_time=datetime(2024, 10, 12, 16, 15), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[6]),
            EventOut(id=11, title='Youth Lightning Talk-2', description='', start_time=datetime(2024, 10, 12, 16, 15), end_time=datetime(2024, 10, 12, 16, 30), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=12, title='Talk#6', description='', start_time=datetime(2024, 10, 12, 16, 30), end_time=datetime(2024, 10, 12, 17, 15), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=13, title='Break [Snacks & Asr Prayer]', description='', start_time=datetime(2024, 10, 12, 17, 15), end_time=datetime(2024, 10, 12, 18, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=14, title='Talk#7', description='', start_time=datetime(2024, 10, 12, 18, 00), end_time=datetime(2024, 10, 12, 18, 45), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[3]),
            EventOut(id=15, title='Sponsor Presentation#2', description='', start_time=datetime(2024, 10, 12, 18, 45), end_time=datetime(2024, 10, 12, 18, 55), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=16, title='Break [Maghreb Prayer]', description='', start_time=datetime(2024, 10, 12, 18, 55), end_time=datetime(2024, 10, 12, 19, 30), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=17, title='Talk#8', description='', start_time=datetime(2024, 10, 12, 19, 30), end_time=datetime(2024, 10, 12, 20, 15), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[7]),
            EventOut(id=18, title='Talk#9 & Conclusion', description='', start_time=datetime(2024, 10, 12, 20, 15), end_time=datetime(2024, 10, 12, 21, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[2]),
            EventOut(id=19, title='Break [Isha Prayer]', description='', start_time=datetime(2024, 10, 12, 21, 00), end_time=datetime(2024, 10, 12, 21, 15), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            ]

# Read the CSV file
df = pd.read_pickle('db/updated_sessions.pkl')

# Convert the DataFrame to a list of EventOut objects
SESSIONS = []
for index, row in df.iterrows():
    event = EventOut(
        id=row['id'],
        title=row['title'],
        description=row['description'],
        start_time=datetime.strptime(row['start_time'], '%Y-%m-%d %H:%M:%S'),
        end_time=datetime.strptime(row['end_time'], '%Y-%m-%d %H:%M:%S'),
        location=row['location'],
        category=EVENT_CATEGORY.MAIN,
        speakers=[int(speaker_id) for speaker_id in row['speaker_id']] if len(row['speaker_id'])>0 else []
    )
    SESSIONS.append(event)

PRAYER_TIMES = [
    PrayerTime(id=1, name=PRAYER_NAME.DHUHR, iqama='2:00 p.m.', time='1:14 p.m.'),
    PrayerTime(id=2, name=PRAYER_NAME.ASR, iqama='6:00 p.m.', time='4:29 p.m.'),
    PrayerTime(id=3, name=PRAYER_NAME.MAGHRIB, iqama='7:40 p.m.', time='6:57 p.m.'),
    PrayerTime(id=4, name=PRAYER_NAME.ISHA, iqama='9:45 p.m.', time='8:06 p.m.'),
]

SPEAKERS = [
            SpeakerOut(id=1, name='Dr. Yasir Qadhi',
                       image_url='speaker_98079.jpg',
                       bio='''Dr. Yasir Qadhi joined East Plano Islamic Center as a resident scholar in July 2019. He completed his primary and secondary education in Jeddah, Saudi Arabia. He graduated with a B.Sc. in Chemical Engineering from the University of Houston, after which he was accepted as a student at the Islamic University of Madinah. There, he completed a second Bachelors degree, specializing in Hadith studies, and then went on to complete M.A. in in Islamic Theology from the College of Dawah. He then returned to the United States, and completed a PhD in Religious Studies from Yale University.'''),
            
            SpeakerOut(id=2, name='Dr. Haifaa Younis',
                       image_url='speaker_13467.jpg',
                       bio='''Dr. Haifaa Younis is an American Board Certified Obstetrician and Gynecologist, and the founder and Chairman of Jannah Institute. She teaches seminars on the thematic commentary of various chapters of the Holy Qur’an and their practical relevance in our day-to-day living. She also offers retreats on key topics that combine the inner essence of Islam with an outward expression of practice. Dr. Haifaa graduated from the Mecca Institute of Islamic Studies in Jeddah, Saudi Arabia and completed memorizing the Qur'an at Al-Huda Qur’an Memorization School in Jeddah. She is passionate about spreading the word of Allah (swt) and igniting the love of Islam and the Qur’an through her teachings.'''),
            
            SpeakerOut(id=3, name='Sh. Abdul Nasir Jangda',
                       image_url='speaker_87665.jpg',
                       bio='''Shaykh AbdulNasir Jangda, born and raised in Dallas, is the founder, director, and an instructor at Qalam. He is a faculty member at the Qalam Seminary where he teaches Sahih Bukhari, advanced Tafseer, Usul, Fiqh, and Balagha. He has completed an extensive study of the life of the Prophet ﷺ in the Seerah Podcast. He annually teaches the Seerah Intensive and leads groups on the Seerah Umrah tour and a visit to Masjid Al-Aqsa. 
He memorized the Qur’an in Karachi at an early age. After high school, he returned to Karachi to study the Islamic sciences full-time at Jamia Binoria where he specialized in Fiqh and Tafsir. He graduated from the rigorous ‘alim program in 2001 at the top of his class. He also attained a B.A. and M.A. in Arabic from Karachi University while completing a Masters in Islamic Studies from the University of Sindh.'''),
            
            SpeakerOut(id=4, name='Dr. Eaman Attia',
                       image_url='speaker_08976.jpg',
                       bio='''Dr Eaman Attia is a graduate of the Faculty of Pharmacy, University of Toronto. Over the past 25 years her passion has been and continues to be mentoring and inspiring lifelong growth and transformations in Muslim youth and community members. She has served many communities as an inspirational speaker, youth director, mentor, and teacher. She has served as the MAS National Tarbiya Director, and currently serves as the local MAS Dallas Tarbiya Director. She resides in Dallas, TX with her husband and five children'''),
            
            SpeakerOut(id=5, name='Ustadh Sami Hamdi ',
                       image_url='speaker_89773.jpeg',
                       bio='''Sami Hamdi is the Managing Director of the International Interest, a global risk and intelligence company. He advises government institutions, global companies, and NGOs on the geopolitical dynamics of Europe and the MENA region, and has significant expertise in advising on commercial issues related to volatile political environments and their implications on market entry, market expansion, and management of stakeholders. Sami is a frequent guest on Aljazeera (Arabic and English), Sky News, BBC and other outlets.'''),
            
            SpeakerOut(id=6, name='Sh. Yaser Birjas',
                       image_url='speaker_79872.png',
                       bio='''Often described as the fatherly figure by students, Shaykh Yaser exudes a calm, gentle and caring demeanor that welcomes students to ask questions with awe and respect. Shaykh Yaser started his career in Electronic Engineering in the UAE, then in Madinah where he graduated as class Valedictorian with the highest honors from the Islamic University of Madinah’s College of Shari'ah (Fiqh and Usul) in 1996. He learned from various highly respected scholars such as Shaykh Mohammed Amin Al-Shanqiti and Shaykh Al-'Uthaymin. In 1997, he went to work as a relief program aide to rebuild war-torn Bosnia. In 2000, he immigrated to the U.S. where he served as an Imam at The Islamic Center in El Paso, Texas and a director of English programs in Da'wah and outreach for the Orland Park Prayer Center. He is currently serving as Imam of the renowned Valley Ranch Islamic Center in Irving, Texas.'''),
                    
            SpeakerOut(id=7, name='Dr. Mohamed Aboutaleb',
                       image_url='speaker_55263.jpg',
                       bio='''Dr. Mohamed Aboutaleb serves as Dean of Administration and Professor at the Boston Islamic Seminary and Senior Fellow at the Yaqeen Institute for Islamic Research. He transitioned from a successful career in technology at a Fortune 100 company to serve the community full-time at the helm of one of the largest Islamic centers in the South, serving as Imam, Religious Director, and Member of the Board for seven years. Dr. Aboutaleb has been featured in media coverage from outlets including National Geographic, NPR, ABC11, Religion News Service, and WRAL; and lectured in many universities including Harvard, MIT, Columbia, Duke, and Georgia Tech. Mohamed pursued seminary training through the Cambridge Islamic College and Al-Salam Institute in the United Kingdom, and completed his Ph.D. and Master’s degrees in electrical engineering from MIT along with degrees in physics and mathematics from the University of Maryland.'''),
            ]

SPONSORS = [
            SponsorOut(id=1, name='Islamic Relief USA',
                       image_url='https://charity.org/wp-content/uploads/2022/09/IslamicReliefUSA-1536x864.png.webp',
                       description='''Islamic Relief USA provides relief and development in a dignified manner regardless of gender, race, or religion, and works to empower individuals in their communities and give them a voice in the world.''',
                       website='https://irusa.org/',
                       facebook='https://www.facebook.com/IslamicReliefUSA',
                       instagram='https://www.instagram.com/islamicreliefusa/',
                       twitter='https://twitter.com/IslamicRelief',
                       ),
            SponsorOut(id=2, name='Baitulmaal',
                       image_url='https://baitulmaal.org/wp-content/uploads/2019/03/baitulmaal-black-website.png',
                       description='''Islamic Relief USA provides relief and development in a dignified manner regardless of gender, race, or religion, and works to empower individuals in their communities and give them a voice in the world.''',
                       website='https://baitulmaal.org/',
                       facebook='https://www.facebook.com/baitulmaal/',
                       instagram='https://www.instagram.com/baitulmaal_usa/',
                       twitter='https://twitter.com/baitulmaal',
                       ),
            SponsorOut(id=3, name='Mercy Without Limits',
                       image_url='https://cdn-200e7.kxcdn.com/wp-content/uploads/2023/02/logo.svg',
                       description='''Islamic Relief USA provides relief and development in a dignified manner regardless of gender, race, or religion, and works to empower individuals in their communities and give them a voice in the world.''',
                       website='https://mwlimits.org/',
                       facebook='https://www.facebook.com/mwlimits',
                       instagram='https://www.instagram.com/mwlimits/',
                       twitter='https://twitter.com/mwlimits',
                       ),
            SponsorOut(id=4, name='United Mission for Relief & Development',
                       image_url='/sponsor_4.png',
                       description='''United Mission for Relief & Development (UMR) is a registered 501(c)(3) nonprofit organization focused on providing disaster relief and recovery services to the underserved both domestically in the U.S. and internationally across the globe.
                       We hope you'll join us in our efforts to make a significant impact in the lives of millions around the world.''',
                       website='https://www.umrelief.org/',
                       facebook='https://www.facebook.com/umrelief/',
                       instagram='https://www.instagram.com/umrelief/',
                       twitter='https://twitter.com/umrelief',
                       ),
            ]