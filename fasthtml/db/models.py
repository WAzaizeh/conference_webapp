from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from db.core import Base

event_speaker = Table(
    'event_speaker', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id')),
    Column('speaker_id', Integer, ForeignKey('speakers.id'))
)

class DBEvent(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String)
    category = Column(String)
    description = Column(String, nullable=True)
    speakers = relationship('DBSpeaker', secondary='event_speaker', back_populates='events')

class DBSpeaker(Base):
    __tablename__ = 'speakers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    events = relationship('DBEvent', secondary='event_speaker', back_populates='speakers')