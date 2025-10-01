from __future__ import annotations


def test_celery_app_creation() -> None:
    from backend.celery_app import celery_app

    assert celery_app is not None
    assert celery_app.conf.broker_url.startswith("redis://")


def test_celery_app_result_backend() -> None:
    from backend.celery_app import celery_app

    assert celery_app.conf.result_backend.startswith("redis://")
