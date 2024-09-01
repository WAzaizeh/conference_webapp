import pytest
from main import app
from typing import Generator
from datetime import datetime
from db.models import DBEvent
from db.core import Base, get_db
from db.schemas import EventCreate, EventUpdate
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, StaticPool
from crud.common import get_db_event
from crud.events import (
    create_db_event,
    update_db_event,
    delete_db_event,
    read_db_event_speakers,
)


# Setup the in-memory SQLite database for testing
DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(
    DATABASE_URL,
    connect_args={
        'check_same_thread': False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def session() -> Generator[Session, None, None]:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()
    yield db_session

    # close the session and drop the tables
    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_db_create_event(session: Session) -> None:
    new_event = EventCreate(
        id=1,
        title='Test Event',
        start_time=datetime(2024, 10, 21, 10, 0),
        end_time=datetime(2024, 10, 21, 12, 0),
        location='Colin College Conference Center',
        category='main session'
    )
    event = create_db_event(new_event, session)
    assert event.id == 1
    assert event.title == 'Test Event'
    assert event.start_time == datetime(2024, 10, 21, 10, 0)
    assert event.end_time == datetime(2024, 10, 21, 12, 0)
    assert event.location == 'Colin College Conference Center'
    assert event.category == 'main session'


def test_db_read_event(session: Session) -> None:
    event = create_db_event(
        EventCreate(title='Test Event 2'), session
    )
    event_id = event.id

    event = get_db_event(event_id, session)
    assert event.id == event_id
    assert event.title == 'Test Event 2'
    # confirm event dafault values
    assert event.start_time == datetime(2024, 10, 21, 10, 0)
    assert event.end_time == datetime(2024, 10, 21, 21, 0)
    assert event.location == 'Colin College Conference Center'
    assert event.category == 'main session'
    assert event.description == None
    assert event.speakers == []


def test_db_update_event(session: Session) -> None:
    event = create_db_event(
        EventCreate(title='Test Event 3',
                    start_time=datetime(2024, 10, 21, 10, 0),
                    end_time=datetime(2024, 10, 21, 12, 0),
                    location='Colin College Conference Center',
                    category='main session'
                    ),
                    session
    )
    event_id = event.id

    updated_event = EventUpdate(
                                title='Updated Event',
                                start_time=datetime(2024, 10, 21, 11, 0),
                                end_time=datetime(2024, 10, 21, 13, 0),
                                description='The start time and end time have been updated'
                                )
    
    event = update_db_event(event_id, updated_event, session)
    assert event.id == event_id
    assert event.title == 'Updated Event'
    assert event.description == 'The start time and end time have been updated'
    assert event.start_time == datetime(2024, 10, 21, 11, 0)
    assert event.end_time == datetime(2024, 10, 21, 13, 0)


def test_db_delete_event(session: Session) -> None:
    event_id = 100
    event = delete_db_event(event_id, session)
    assert event.id == event_id
    # Try to get the deleted event
    try:
        event = get_db_event(event_id, session)
    except Exception as e:
        assert str(e) == 'Event not found'




# def test_create_item():
#     response = client.post(
#         '/events/', json={'title': 'Test Event', 'start_time': '2024-10-21T10:00:00', 'end_time': '2024-10-21T12:00:00', 'location': 'Colin College Conference Center', 'category': 'main session'}
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data['title'] == 'Test Event'
#     assert data['start_time'] == '2024-10-21T10:00:00'
#     assert data['end_time'] == '2024-10-21T12:00:00'
#     assert data['location'] == 'Colin College Conference Center'
#     assert data['category'] == 'main session'
#     assert 'id' in data


# def test_read_item():
#     # Create an item
#     response = client.post(
#         '/items/', json={'name': 'Test Item', 'description': 'This is a test item'}
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     item_id = data['id']

#     response = client.get(f'/items/{item_id}')
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data['name'] == 'Test Item'
#     assert data['description'] == 'This is a test item'
#     assert data['id'] == item_id


# def test_update_item():
#     item_id = 1
#     response = client.put(
#         f'/items/{item_id}',
#         json={'name': 'Updated Item', 'description': 'This is an updated item'},
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data['name'] == 'Updated Item'
#     assert data['description'] == 'This is an updated item'
#     assert data['id'] == item_id


# def test_delete_item():
#     item_id = 1
#     response = client.delete(f'/items/{item_id}')
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data['id'] == item_id
#     # Try to get the deleted item
#     response = client.get(f'/items/{item_id}')
#     assert response.status_code == 404, response.text