import re

from korean_romanizer.romanizer import Romanizer
from sqlalchemy.orm import Session

SLUG_MAX_LENGTH = 50


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

    if len(slug) > SLUG_MAX_LENGTH:
        slug = slug[:SLUG_MAX_LENGTH].rstrip("-")

    return slug


def ensure_unique_slug(base_slug: str, db: Session) -> str:
    from backend.models.topic import Topic

    search_prefix = base_slug[:40] if len(base_slug) >= 40 else base_slug
    existing = db.query(Topic.slug).filter(Topic.slug.startswith(search_prefix)).all()

    existing_slugs = {row[0] for row in existing}
    if base_slug not in existing_slugs:
        return base_slug

    MAX_ATTEMPTS = 1000

    for counter in range(2, MAX_ATTEMPTS + 2):
        suffix = f"-{counter}"
        max_base_len = SLUG_MAX_LENGTH - len(suffix)
        safe_base = base_slug[:max_base_len].rstrip("-")
        candidate = f"{safe_base}{suffix}"

        if len(candidate) > SLUG_MAX_LENGTH:
            raise ValueError(
                f"Cannot generate unique slug: base '{safe_base}' too long"
            )
        if candidate not in existing_slugs:
            return candidate

    raise ValueError(f"Cannot generate unique slug after {MAX_ATTEMPTS} attempts")
