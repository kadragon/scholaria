import re

from korean_romanizer.romanizer import Romanizer
from sqlalchemy.orm import Session


def generate_slug(name: str) -> str:
    if not name or not name.strip():
        return "untitled"

    slug = name.strip()

    romanized = Romanizer(slug).romanize()
    slug = romanized.lower()

    slug = re.sub(r"[^\w\s-]", " ", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    slug = slug.strip("-")

    if not slug:
        return "untitled"

    max_length = 50
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")

    return slug


def ensure_unique_slug(base_slug: str, db: Session) -> str:
    from backend.models.topic import Topic

    slug = base_slug
    counter = 2

    while db.query(Topic).filter(Topic.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
