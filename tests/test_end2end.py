from time import sleep

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from common.enums import TaskStatus
from common.models import User, Task, Base

BASE_URL = "http://task-tracker:9000"
CHECKIN_URL = f"{BASE_URL}/checkin"
CHECKOUT_URL = f"{BASE_URL}/checkout"
REPORT_URL = f"{BASE_URL}/report"
DB_URL = "postgresql+psycopg2://admin:admin@postgres:5432/tasktracker"

engine = create_engine(DB_URL, echo=True)
Base.metadata.create_all(engine)
SessionLocal = scoped_session(sessionmaker(bind=engine))


@pytest.fixture
def http_client():
    with requests.Session() as client:
        yield client


@pytest.fixture(autouse=True, scope="package")
def wait():
    sleep(5)


@pytest.fixture(autouse=True)
def cleanup():
    session = SessionLocal()
    session.query(Task).delete()
    session.query(User).delete()

    yield

    session.query(Task).delete()
    session.query(User).delete()

    session.commit()
    session.close()


def test_checkin_when_input_is_valid_then_response_status_is_200(http_client):
    response = http_client.post(CHECKIN_URL, json={"user": "Bob", "task": "Eat banana"})
    assert response.status_code == 200

    session = SessionLocal()
    tasks = session.query(Task).all()
    users = session.query(User).all()

    assert len(users) == 1
    assert any(user.user_name == "Bob" for user in users)

    assert len(tasks) == 1
    assert any(task.task_name == "Eat banana" and task.status == TaskStatus.active for task in tasks)


def test_checkin_when_input_is_missing_task_name_then_response_status_is_422(http_client):
    response = http_client.post(CHECKIN_URL, json={"user": "Bob"})
    assert response.status_code == 422

    session = SessionLocal()
    tasks = session.query(Task).all()
    users = session.query(User).all()

    assert len(users) == 0
    assert len(tasks) == 0


def test_checkin_when_user_already_has_active_task_then_response_status_is_400(http_client):
    http_client.post(CHECKIN_URL, json={"user": "Bob", "task": "Eat banana"})
    response = http_client.post(CHECKIN_URL, json={"user": "Bob", "task": "Call Mary"})
    assert response.status_code == 400

    session = SessionLocal()
    tasks = session.query(Task).all()
    users = session.query(User).all()

    assert len(users) == 1
    assert any(user.user_name == "Bob" for user in users)

    assert len(tasks) == 1
    assert any(task.task_name == "Eat banana" and task.status == TaskStatus.active for task in tasks)


def test_checkout_when_input_is_valid_then_response_status_is_200(http_client):
    http_client.post(CHECKIN_URL, json={"user": "Bob", "task": "Eat banana"})

    response = http_client.post(CHECKOUT_URL, json={"user": "Bob"})
    assert response.status_code == 200

    session = SessionLocal()
    tasks = session.query(Task).all()
    users = session.query(User).all()

    assert len(users) == 1
    assert any(user.user_name == "Bob" for user in users)

    assert len(tasks) == 1
    assert any(task.task_name == "Eat banana" and task.status == TaskStatus.finished for task in tasks)


def test_checkout_when_user_doesnt_exist_then_response_status_is_400(http_client):
    response = http_client.post(CHECKOUT_URL, json={"user": "Bob"})
    assert response.status_code == 400

    session = SessionLocal()
    tasks = session.query(Task).all()
    users = session.query(User).all()

    assert len(users) == 0
    assert len(tasks) == 0


def test_checkout_when_user_doesnt_have_an_active_task_then_response_status_is_400(http_client):
    http_client.post(CHECKIN_URL, json={"user": "Bob", "task": "Eat banana"})
    http_client.post(CHECKOUT_URL, json={"user": "Bob"})

    response = http_client.post(CHECKOUT_URL, json={"user": "Bob"})
    assert response.status_code == 400


def test_report_when_db_is_empty_then_response_status_is_204(http_client):
    response = http_client.get(REPORT_URL)
    assert response.status_code == 204


def test_report_when_db_is_populated_then_assert_response(http_client):
    http_client.post(CHECKIN_URL, json={"user": "Bob", "task": "Eat banana"})
    http_client.post(CHECKOUT_URL, json={"user": "Bob"})

    http_client.post(CHECKIN_URL, json={"user": "Mary", "task": "Call Bob"})
    http_client.post(CHECKIN_URL, json={"user": "Bob", "task": "Get more bananas"})
    http_client.post(CHECKOUT_URL, json={"user": "Bob"})
    http_client.post(CHECKOUT_URL, json={"user": "Mary"})

    response = http_client.get(REPORT_URL)
    assert response.status_code == 200
    assert response.json() == {'Bob': [{'Eat banana': '0 minutes'},
                                       {'Get more bananas': '0 minutes'}],
                               'Mary': [{'Call Bob': '0 minutes'}]}
