"""Schema serialization utilities."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

_LOCAL_ZONE = ZoneInfo("UTC")


def to_local_iso(dt: datetime) -> str:
    """Convert datetime to ISO format in project local timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(_LOCAL_ZONE).isoformat()
