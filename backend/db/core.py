from datetime import datetime
from typing import Optional, List
from sqlalchemy import Table, Column, create_engine, ForeignKey, Integer
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase, Mapped, mapped_column

DATABASE_URL = 'sqlite:///test.db'


class NotFoundError(Exception):
    pass


class Base(DeclarativeBase):
    pass

event_speaker = Table(
    'event_speaker',
    Base.metadata,
    Column('speaker_id', Integer, ForeignKey('speakers.id')),
    Column('event_id', Integer, ForeignKey('events.id')),
)


class DBEvent(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    location: Mapped[str]
    category: Mapped[str]
    description: Mapped[Optional[str]]


class DBSpeaker(Base):
    __tablename__ = 'speakers'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    image_url: Mapped[Optional[str]]
    bio: Mapped[Optional[str]]
    events: Mapped[List[DBEvent]] = relationship('events', secondary=event_speaker, backref='speakers')


engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()