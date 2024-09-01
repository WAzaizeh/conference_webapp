from main import app
from db.core import Base, get_db
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool


# Setup the TestClient
client = TestClient(app)


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


def test_create_improper_event() -> None:
    response = client.post('/events', json={'start_time': '2024-10-21T10:00:00', 'end_time': '2024-10-21T12:00:00', 'location': 'Colin College Conference Center', 'category': 'main session'})
    assert response.status_code == 422, response.text


def setup() -> None:
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)


def teardown() -> None:
    # Drop the tables in the test database
    Base.metadata.drop_all(bind=engine)