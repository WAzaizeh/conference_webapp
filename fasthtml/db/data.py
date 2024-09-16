from datetime import datetime
from .schemas import (
    EventOut,
    SpeakerOut,
    EVENT_CATEGORY,
    PrayerTime,
    PRAYER_NAME,
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

PRAYER_TIMES = [
            PrayerTime(id=1, name=PRAYER_NAME.DHUHR, time=datetime(2024, 10, 12, 14, 00)),
            PrayerTime(id=2, name=PRAYER_NAME.ASR, time=datetime(2024, 10, 12, 17, 30)),
            PrayerTime(id=3, name=PRAYER_NAME.MAGHRIB, time=datetime(2024, 10, 12, 19, 10)),
            PrayerTime(id=4, name=PRAYER_NAME.ISHA, time=datetime(2024, 10, 12, 21, 00)),
            ]

SPEAKERS = [
            SpeakerOut(id=1, name='Dr. Yasir Qadhi',
                       image_url='speaker_98079.jpg',
                       bio='''Dr. Yasir Qadhi joined East Plano Islamic Center as a resident scholar in July 2019. He completed his primary and secondary education in Jeddah, Saudi Arabia. He graduated with a B.Sc. in Chemical Engineering from the University of Houston, after which he was accepted as a student at the Islamic University of Madinah. There, he completed a second Bachelors degree, specializing in Hadith studies, and then went on to complete M.A. in in Islamic Theology from the College of Dawah. He then returned to the United States, and completed a PhD in Religious Studies from Yale University.'''),
            
            SpeakerOut(id=2, name='Dr. Haifa Younis',
                       image_url='speaker_13467.jpg',
                       bio='''Dr. Haifaa Younis is an American Board Certified Obstetrician and Gynecologist, and the founder and Chairman of Jannah Institute. She teaches seminars on the thematic commentary of various chapters of the Holy Qur’an and their practical relevance in our day-to-day living. She also offers retreats on key topics that combine the inner essence of Islam with an outward expression of practice. Dr. Haifaa graduated from the Mecca Institute of Islamic Studies in Jeddah, Saudi Arabia and completed memorizing the Qur'an at Al-Huda Qur’an Memorization School in Jeddah. She is passionate about spreading the word of Allah (swt) and igniting the love of Islam and the Qur’an through her teachings.'''),
            
            SpeakerOut(id=3, name='Sh. Abdul Nasir Jangda',
                       image_url='speaker_87665.jpg',
                       bio='''Shaykh AbdulNasir Jangda, born and raised in Dallas, is the founder, director, and an instructor at Qalam. He is a faculty member at the Qalam Seminary where he teaches Sahih Bukhari, advanced Tafseer, Usul, Fiqh, and Balagha. He has completed an extensive study of the life of the Prophet ﷺ in the Seerah Podcast. He annually teaches the Seerah Intensive and leads groups on the Seerah Umrah tour and a visit to Masjid Al-Aqsa. 
He memorized the Qur’an in Karachi at an early age. After high school, he returned to Karachi to study the Islamic sciences full-time at Jamia Binoria where he specialized in Fiqh and Tafsir. He graduated from the rigorous ‘alim program in 2001 at the top of his class. He also attained a B.A. and M.A. in Arabic from Karachi University while completing a Masters in Islamic Studies from the University of Sindh.'''),
            
            SpeakerOut(id=4, name='Dr. Eaman Attia',
                       image_url='speaker_08976.jpg',
                       bio='Bio of Dr. Eaman Attia'),
            
            SpeakerOut(id=5, name='Ustadh Sami Hamdi ',
                       image_url='speaker_89773.jpeg',
                       bio='''Sami Hamdi is the Managing Director of the International Interest, a global risk and intelligence company. He advises government institutions, global companies, and NGOs on the geopolitical dynamics of Europe and the MENA region, and has significant expertise in advising on commercial issues related to volatile political environments and their implications on market entry, market expansion, and management of stakeholders. Sami is a frequent guest on Aljazeera (Arabic and English), Sky News, BBC and other outlets.'''),
            
            SpeakerOut(id=6, name='Sh. Yaser Birjas',
                       image_url='speaker_79872.png',
                       bio='''Often described as the fatherly figure by students, Shaykh Yaser exudes a calm, gentle and caring demeanor that welcomes students to ask questions with awe and respect. Shaykh Yaser started his career in Electronic Engineering in the UAE, then in Madinah where he graduated as class Valedictorian with the highest honors from the Islamic University of Madinah’s College of Shari'ah (Fiqh and Usul) in 1996. He learned from various highly respected scholars such as Shaykh Mohammed Amin Al-Shanqiti and Shaykh Al-'Uthaymin. In 1997, he went to work as a relief program aide to rebuild war-torn Bosnia. In 2000, he immigrated to the U.S. where he served as an Imam at The Islamic Center in El Paso, Texas and a director of English programs in Da'wah and outreach for the Orland Park Prayer Center. He is currently serving as Imam of the renowned Valley Ranch Islamic Center in Irving, Texas.'''),
                    
            SpeakerOut(id=7, name='Dr. Mohamed Abutaleb',
                       image_url='speaker_55263.jpg',
                       bio='''Mohamed AbuTaleb serves as Dean of Administration and Professor at the Boston Islamic Seminary and Senior Fellow at the Yaqeen Institute for Islamic Research. He transitioned from a successful career in technology at a Fortune 100 company to serve the community full-time at the helm of one of the largest Islamic centers in the South, serving as Imam, Religious Director, and Member of the Board for seven years. Dr. AbuTaleb has been featured in media coverage from outlets including National Geographic, NPR, ABC11, Religion News Service, and WRAL; and lectured in many universities including Harvard, MIT, Columbia, Duke, and Georgia Tech. Mohamed pursued seminary training through the Cambridge Islamic College and Al-Salam Institute in the United Kingdom, and completed his Ph.D. and Master’s degrees in electrical engineering from MIT along with degrees in physics and mathematics from the University of Maryland.'''),
            ]