"""Schema serialization utilities."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from django.conf import settings

_LOCAL_ZONE = ZoneInfo(settings.TIME_ZONE)


def to_local_iso(dt: datetime) -> str:
    """Convert datetime to ISO format in project local timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(_LOCAL_ZONE).isoformat()
