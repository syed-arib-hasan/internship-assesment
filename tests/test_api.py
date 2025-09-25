import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_create_student_success(client):
    payload = {"name": "Alice", "email": "alice@example.com"}
    r = client.post("/students", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert isinstance(data["id"], int)


def test_get_student_not_found(client):
    r = client.get("/students/999999")
    assert r.status_code == 404


def _create_teacher(client, name: str, email: str) -> int:
    r = client.post("/teachers", json={"name": name, "email": email})
    assert r.status_code == 200
    return r.json()["id"]


def _create_course(client, title: str, capacity: int, teacher_id: int | None) -> int:
    r = client.post("/courses", json={"title": title, "capacity": capacity, "teacher_id": teacher_id})
    assert r.status_code == 200
    return r.json()["id"]


def test_enroll_capacity_limit(client):
    # create teacher and a course with capacity 1
    tid = _create_teacher(client, "T1", "t1@example.com")
    cid = _create_course(client, "C1", 1, tid)

    # create two students
    s1 = client.post("/students", json={"name": "S1", "email": "s1@example.com"}).json()["id"]
    s2 = client.post("/students", json={"name": "S2", "email": "s2@example.com"}).json()["id"]

    # first enroll succeeds
    r1 = client.post(f"/students/{s1}/enroll", json={"course_id": cid})
    assert r1.status_code == 200

    # second enroll fails due to capacity
    r2 = client.post(f"/students/{s2}/enroll", json={"course_id": cid})
    assert r2.status_code == 400
    assert "full" in r2.json()["detail"].lower()


def test_import_scraped_dedup_and_list(client):
    sample = [
        {"title": "A", "link": "http://x/1", "image_url": "i", "price": "10", "scraped_at": "now"},
        {"title": "B", "link": "http://x/2", "image_url": "i2", "price": "12", "scraped_at": "now"},
    ]
    # first import adds 2
    r = client.post("/import/scraped", json=sample)
    assert r.status_code == 200
    assert r.json()["imported"] >= 0

    # second import should add 0 (dedupe by link)
    r2 = client.post("/import/scraped", json=sample)
    assert r2.status_code == 200
    assert r2.json()["imported"] == 0

    # list shows at least 2
    r3 = client.get("/scraped_resources")
    assert r3.status_code == 200
    assert isinstance(r3.json(), list)
    assert len(r3.json()) >= 2


def test_create_course_and_get(client):
    tid = _create_teacher(client, "T2", "t2@example.com")
    cid = _create_course(client, "C2", 30, tid)
    r = client.get(f"/courses/{cid}")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "C2"
    assert body["capacity"] == 30


