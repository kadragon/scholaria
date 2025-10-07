from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_get_topic_by_slug(db_session, admin_headers):
    from backend.models.topic import Topic

    topic = Topic(name="코러스", slug="koreoseu", description="Test topic")
    db_session.add(topic)
    db_session.commit()
    db_session.refresh(topic)

    response = client.get(f"/api/topics/slug/{topic.slug}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "koreoseu"
    assert data["name"] == "코러스"


def test_get_topic_by_slug_not_found(admin_headers):
    response = client.get("/api/topics/slug/nonexistent", headers=admin_headers)
    assert response.status_code == 404


def test_get_topic_by_id_still_works(db_session, admin_headers):
    from backend.models.topic import Topic

    topic = Topic(name="Test", slug="test", description="Test topic")
    db_session.add(topic)
    db_session.commit()
    db_session.refresh(topic)

    response = client.get(f"/api/topics/{topic.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == topic.id
    assert data["slug"] == "test"
