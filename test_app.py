"""
Automated tests.

These are what the pipeline runs on every push. If any of them fail,
the deploy stops and nothing broken reaches your users. That single idea
is most of what CI is for.

Run them yourself with:  pytest -v
"""

import app as chat


def setup_function():
    """Start every test with an empty message list."""
    chat.messages.clear()


def client():
    return chat.app.test_client()


def test_home_page_loads():
    response = client().get("/")
    assert response.status_code == 200
    assert b"Radio Room" in response.data


def test_home_page_shows_the_picture():
    response = client().get("/")
    assert b"signal.svg" in response.data


def test_picture_is_actually_served():
    response = client().get("/static/signal.svg")
    assert response.status_code == 200


def test_health_check_reports_ok():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_room_without_a_name_sends_you_home():
    response = client().get("/room")
    assert response.status_code == 302


def test_room_with_a_name_loads():
    response = client().get("/room?name=sam")
    assert response.status_code == 200
    assert b"sam" in response.data


def test_sending_a_message_stores_it():
    client().post("/api/messages", json={"name": "sam", "text": "hello"})
    assert len(chat.messages) == 1
    assert chat.messages[0]["text"] == "hello"


def test_empty_message_is_rejected():
    response = client().post("/api/messages", json={"name": "sam", "text": "   "})
    assert response.status_code == 400
    assert len(chat.messages) == 0


def test_message_without_a_name_is_rejected():
    response = client().post("/api/messages", json={"name": "", "text": "hi"})
    assert response.status_code == 400


def test_messages_can_be_read_back():
    client().post("/api/messages", json={"name": "sam", "text": "hello"})
    response = client().get("/api/messages")
    assert response.get_json()[0]["name"] == "sam"


def test_old_messages_are_dropped():
    """The list must not grow forever."""
    for i in range(chat.MAX_MESSAGES + 20):
        chat.messages.append({"name": "sam", "text": str(i), "time": "10:00"})
    client().post("/api/messages", json={"name": "sam", "text": "newest"})
    assert len(chat.messages) == chat.MAX_MESSAGES
    assert chat.messages[-1]["text"] == "newest"
