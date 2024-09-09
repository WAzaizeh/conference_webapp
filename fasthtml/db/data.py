from datetime import datetime
from .schemas import (
    EventOut,
    SpeakerOut,
    EVENT_CATEGORY,
    PrayerTime,
    PRAYER_NAME,
)

SESSIONS = [
            EventOut(id=1, title='Quran Recitation & Welcome', description='', start_time=datetime(2024, 10, 21, 10, 00), end_time=datetime(2024, 10, 21, 10, 15), location='room 1', category=EVENT_CATEGORY.MAIN),
            EventOut(id=2, title='Talk#1', description='', start_time=datetime(2024, 10, 21, 10, 15), end_time=datetime(2024, 10, 21, 11, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[4]),
            EventOut(id=3, title='Talk#2', description='', start_time=datetime(2024, 10, 21, 11, 00), end_time=datetime(2024, 10, 21, 11, 45), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[5]),
            EventOut(id=4, title='Trivia Break & Prizes', description='', start_time=datetime(2024, 10, 21, 11, 45), end_time=datetime(2024, 10, 21, 12, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=5, title='Talk#3', description='', start_time=datetime(2024, 10, 21, 12, 00), end_time=datetime(2024, 10, 21, 12, 45), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=6, title='Youth Lightning Talk-1', description='', start_time=datetime(2024, 10, 21, 12, 45), end_time=datetime(2024, 10, 21, 13, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=7, title='Break [Lunch & Dhuhr Prayer]', description='', start_time=datetime(2024, 10, 21, 13, 00), end_time=datetime(2024, 10, 21, 14, 30), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=8, title='Trivia Break & Prizes Sponsor Presentation #1', description='', start_time=datetime(2024, 10, 21, 14, 30), end_time=datetime(2024, 10, 21, 14, 45), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=9, title='Talk#4', description='', start_time=datetime(2024, 10, 21, 14, 45), end_time=datetime(2024, 10, 21, 15, 30), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=10, title='Talk#5', description='', start_time=datetime(2024, 10, 21, 15, 30), end_time=datetime(2024, 10, 21, 16, 15), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=11, title='Youth Lightning Talk-2', description='', start_time=datetime(2024, 10, 21, 16, 15), end_time=datetime(2024, 10, 21, 16, 30), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=12, title='Talk#6', description='', start_time=datetime(2024, 10, 21, 16, 30), end_time=datetime(2024, 10, 21, 17, 15), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=13, title='Break [Snacks & Asr Prayer]', description='', start_time=datetime(2024, 10, 21, 17, 15), end_time=datetime(2024, 10, 21, 18, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=14, title='Talk#7', description='', start_time=datetime(2024, 10, 21, 18, 00), end_time=datetime(2024, 10, 21, 18, 45), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=15, title='Sponsor Presentation#2', description='', start_time=datetime(2024, 10, 21, 18, 45), end_time=datetime(2024, 10, 21, 18, 55), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=16, title='Break [Maghreb Prayer]', description='', start_time=datetime(2024, 10, 21, 18, 55), end_time=datetime(2024, 10, 21, 19, 30), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=17, title='Talk#8', description='', start_time=datetime(2024, 10, 21, 19, 30), end_time=datetime(2024, 10, 21, 20, 15), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=18, title='Talk#9 & Conclusion', description='', start_time=datetime(2024, 10, 21, 20, 15), end_time=datetime(2024, 10, 21, 21, 00), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            EventOut(id=19, title='Break [Isha Prayer]', description='', start_time=datetime(2024, 10, 21, 21, 00), end_time=datetime(2024, 10, 21, 21, 15), location='room 1', category=EVENT_CATEGORY.MAIN, speakers=[]),
            ]
PRAYER_TIMES = [
            PrayerTime(id=1, name=PRAYER_NAME.DHUHR, time=datetime(2024, 10, 21, 14, 00)),
            PrayerTime(id=2, name=PRAYER_NAME.ASR, time=datetime(2024, 10, 21, 17, 30)),
            PrayerTime(id=3, name=PRAYER_NAME.MAGHRIB, time=datetime(2024, 10, 21, 19, 10)),
            PrayerTime(id=4, name=PRAYER_NAME.ISHA, time=datetime(2024, 10, 21, 21, 00)),
            ]
SPEAKERS = [
            SpeakerOut(id=1, name='Dr. Yasir Qadhi',
                       image_url='https://masconvention.org/wp-content/uploads/2023/08/Staff-Yasir-Qadhi-500x500-1.jpg',
                       bio='''Dr. Yasir Qadhi joined East Plano Islamic Center as a resident scholar in July 2019. He completed his primary and secondary education in Jeddah, Saudi Arabia.
He graduated with a B.Sc. in Chemical Engineering from the University of Houston, after which he was accepted as a student at the Islamic University of Madinah. There, he completed a second Bachelors degree, specializing in Hadith studies, and then went on to complete M.A. in in Islamic Theology from the College of Dawah. He then returned to the United States, and completed a PhD in Religious Studies from Yale University.

Dr. Yasir Qadhi has authored several books, published academic articles, and appeared on numerous satellite and TV stations around the globe. His online videos are some of the most popular and highly-watched Islamic videos in English.'''),
            
            SpeakerOut(id=2, name='Dr. Haifa Younis',
                       image_url='https://masconvention.org/wp-content/uploads/2023/09/haifaa-younis.webp',
                       bio='''Dr. Haifaa Younis is an American Board Certified Obstetrician and Gynecologist, and the founder and Chairman of Jannah Institute. She teaches seminars on the thematic commentary of various chapters of the Holy Qur’an and their practical relevance in our day-to-day living. She also offers retreats on key topics that combine the inner essence of Islam with an outward expression of practice. Dr. Haifaa graduated from the Mecca Institute of Islamic Studies in Jeddah, Saudi Arabia and completed memorizing the Qur'an at Al-Huda Qur’an Memorization School in Jeddah. She is passionate about spreading the word of Allah (swt) and igniting the love of Islam and the Qur’an through her teachings.'''),
            
            SpeakerOut(id=3, name='Sh. Abdul Nasir Jangda',
                       image_url='https://masconvention.org/wp-content/uploads/2018/12/Abdul-Nasir-Jangda-scaled.jpg',
                       bio='''Shaykh AbdulNasir Jangda is the founder, director, and an instructor at Qalam. He is a faculty member at the Qalam Seminary where he teaches Sahih Bukhari, advanced Tafseer, Usul, Fiqh, and Balagha. He has completed an extensive study of the life of the Prophet ﷺ in the Seerah Podcast. He annually teaches the Seerah Intensive and leads groups on the Seerah Umrah tour and a visit to Masjid Al-Aqsa.

Born and raised in Dallas, he currently resides there with his wife and three children. He memorized the Qur’an in Karachi at an early age. After high school, he returned to Karachi to study the Islamic sciences full-time at Jamia Binoria where he specialized in Fiqh and Tafsir. He graduated from the rigorous ‘alim program in 2001 at the top of his class. He also attained a B.A. and M.A. in Arabic from Karachi University while completing a Masters in Islamic Studies from the University of Sindh. After returning home, he taught at the local university and Islamic schools and served as the Imam in the Dallas area.'''),
            
            SpeakerOut(id=4, name='Dr. Eaman Attia',
                       image_url='https://muslimamericansociety.org/wp-content/uploads/2022/04/Staff_Headshot_Eaman_Attia-216x300.jpg.webp',
                       bio='Bio of Dr. Eaman Attia'),
            
            SpeakerOut(id=5, name='Ustadh Sami Hamdi ',
                       image_url='https://masconvention.org/wp-content/uploads/2023/12/Sami-Hamdi.jpg',
                       bio='''Sami Hamdi is the Managing Director of the International Interest, a global risk and intelligence company. He advises government institutions, global companies, and NGOs on the geopolitical dynamics of Europe and the MENA region, and has significant expertise in advising on commercial issues related to volatile political environments and their implications on market entry, market expansion, and management of stakeholders. Sami is a frequent guest on Aljazeera (Arabic and English), Sky News, BBC and other outlets.'''),
            
            SpeakerOut(id=6, name='Sh. Yaser Birjas',
                       image_url='https://masconvention.org/wp-content/uploads/2022/12/Yaser-Birjas.jpeg',
                       bio='''Often described as the fatherly figure by students, Shaykh Yaser exudes a calm, gentle and caring demeanor that welcomes students to ask questions with awe and respect. Shaykh Yaser started his career in Electronic Engineering in the UAE, then in Madinah where he graduated as class Valedictorian with the highest honors from the Islamic University of Madinah’s College of Shari'ah (Fiqh and Usul) in 1996. He learned from various highly respected scholars such as Shaykh Mohammed Amin Al-Shanqiti and Shaykh Al-'Uthaymin. In 1997, he went to work as a relief program aide to rebuild war-torn Bosnia. In 2000, he immigrated to the U.S. where he served as an Imam at The Islamic Center in El Paso, Texas and a director of English programs in Da'wah and outreach for the Orland Park Prayer Center. He is currently serving as Imam of the renowned Valley Ranch Islamic Center in Irving, Texas, rapidly establishing himself as an invaluable leader of the Texan Muslim Community.​His speciality in the subject of marriage and relations made him a highly sought marriage counsellor for the Muslim community, and with four children and much experience, his parenting classes are equally popular. With his superb all-round grasp on Islamic sciences, Shaykh Yaser is welcomed eagerly in every city he teaches whether it is his Usul, Fiqh, Financial Literacy, or Relationship classes. It is no wonder that he has taught more students than any other of our instructors at AlMaghrib! Shaykh Yaser started his career in Electronic Engineering in the UAE, then in Madinah where he graduated as class Valedictorian with the highest honors from the Islamic University of Madinah’s College of Shari'ah (Fiqh and Usul) in 1996. He learned from various highly respected scholars such as Shaykh Mohammed Amin Al-Shanqiti and Shaykh Al-'Uthaymin. In 1997, he went to work as a relief program aide to rebuild war-torn Bosnia. In 2000, he immigrated to the U.S. where he served as an Imam at The Islamic Center in El Paso, Texas and a director of English programs in Da'wah and outreach for the Orland Park Prayer Center. He is currently serving as Imam of the renowned Valley Ranch Islamic Center in Irving, Texas, rapidly establishing himself as an invaluable leader of the Texan Muslim Community.​His speciality in the subject of marriage and relations made him a highly sought marriage counsellor for the Muslim community, and with four children and much experience, his parenting classes are equally popular. With his superb all-round grasp on Islamic sciences, Shaykh Yaser is welcomed eagerly in every city he teaches whether it is his Usul, Fiqh, Financial Literacy, or Relationship classes. It is no wonder that he has taught more students than any other of our instructors at AlMaghrib! In addition to be being a mentor and speaker, Lobna has written for myvirtualmosque.com and the MAS Blog. Lobna is a recent graduate of Chapman University with a Masters of Fine Arts in Screenwriting. She is the creator of the YouTube channel, Double Shot Mocha Productions, where she strives to promote social awareness through humor. Lobna was born and raised in Los Angeles, California. She graduated from California State University, Northridge in Business Administration with a focus in Accounting. She worked as an accountant for ten years until she began her career as a mother. Lobna moved to Egypt for three years with her husband, Shaikh Suhail Mulla, and her children and studied Arabic, Qur’anic Recitation and Islamic Sciences under Azhari scholars. Lobna Mulla currently resides in Los Angeles, CA with her husband and four children.'''),
                    
            SpeakerOut(id=7, name='Dr. Mohamed Abutaleb',
                       image_url='https://masconvention.org/wp-content/uploads/2022/12/Mohamed-Abutaleb.jpeg',
                       bio='''Mohamed AbuTaleb serves as Dean of Administration and Professor at the Boston Islamic Seminary and Senior Fellow at the Yaqeen Institute for Islamic Research. He transitioned from a successful career in technology at a Fortune 100 company to serve the community full-time at the helm of one of the largest Islamic centers in the South, serving as Imam, Religious Director, and Member of the Board for seven years. Dr. AbuTaleb has been featured in media coverage from outlets including National Geographic, NPR, ABC11, Religion News Service, and WRAL; and lectured in many universities including Harvard, MIT, Columbia, Duke, and Georgia Tech. Mohamed pursued seminary training through the Cambridge Islamic College and Al-Salam Institute in the United Kingdom, and completed his Ph.D. and Master’s degrees in electrical engineering from MIT along with degrees in physics and mathematics from the University of Maryland.'''),

            SpeakerOut(id=8, name='Dr. Haifaa Younis',
                       image_url='',
                       bio='''''')
            ]