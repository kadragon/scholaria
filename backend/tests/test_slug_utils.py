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


def test_ensure_unique_slug_with_max_length_base(db_session: Session):
    from backend.models.topic import Topic

    long_slug = "a" * 50
    t1 = Topic(name="Long 1", description="Long 1")
    t1.slug = long_slug
    db_session.add(t1)
    db_session.flush()

    new_slug = ensure_unique_slug(long_slug, db_session)
    assert len(new_slug) <= 50
    assert new_slug == ("a" * 46) + "-2"


def test_ensure_unique_slug_with_max_length_multiple_collisions(db_session: Session):
    from backend.models.topic import Topic

    long_slug = "b" * 50

    t1 = Topic(name="L1", description="L1")
    t1.slug = long_slug
    t2 = Topic(name="L2", description="L2")
    t2.slug = long_slug[:46] + "-2"
    t3 = Topic(name="L3", description="L3")
    t3.slug = long_slug[:46] + "-3"

    db_session.add_all([t1, t2, t3])
    db_session.flush()

    new_slug = ensure_unique_slug(long_slug, db_session)
    assert len(new_slug) <= 50
    assert new_slug == long_slug[:46] + "-4"


def test_ensure_unique_slug_with_49_char_base(db_session: Session):
    from backend.models.topic import Topic

    slug_49 = "c" * 49
    t1 = Topic(name="C1", description="C1")
    t1.slug = slug_49
    db_session.add(t1)
    db_session.flush()

    new_slug = ensure_unique_slug(slug_49, db_session)
    assert len(new_slug) <= 50
    assert new_slug == ("c" * 46) + "-2"
