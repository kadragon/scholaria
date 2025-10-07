from sqlalchemy.orm import Session

from backend.services.slug_utils import ensure_unique_slug, generate_slug


def test_generate_slug_korean():
    assert generate_slug("코러스") == "koreoseu"


def test_generate_slug_english():
    assert generate_slug("AI Chat") == "ai-chat"


def test_generate_slug_mixed():
    assert generate_slug("AI 챗봇") == "ai-chaetbot"


def test_generate_slug_special_chars():
    assert generate_slug("Hello@World!") == "hello-world"


def test_generate_slug_empty():
    assert generate_slug("") == "untitled"


def test_generate_slug_only_special_chars():
    assert generate_slug("@#$%") == "untitled"


def test_generate_slug_max_length():
    long_name = "a" * 100
    slug = generate_slug(long_name)
    assert len(slug) <= 50


def test_ensure_unique_slug_no_collision(db_session: Session):
    slug = ensure_unique_slug("test-slug", db_session)
    assert slug == "test-slug"


def test_ensure_unique_slug_with_collision(db_session: Session):
    from backend.models.topic import Topic

    db_session.add(Topic(name="Test", slug="test-slug", description="Test"))
    db_session.commit()

    slug = ensure_unique_slug("test-slug", db_session)
    assert slug == "test-slug-2"


def test_ensure_unique_slug_multiple_collisions(db_session: Session):
    from backend.models.topic import Topic

    db_session.add(Topic(name="Test 1", slug="test-slug", description="Test 1"))
    db_session.add(Topic(name="Test 2", slug="test-slug-2", description="Test 2"))
    db_session.commit()

    slug = ensure_unique_slug("test-slug", db_session)
    assert slug == "test-slug-3"
