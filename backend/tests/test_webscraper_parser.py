from unittest.mock import MagicMock, patch

import pytest

from backend.ingestion.parsers import WebScraperParser


@pytest.fixture
def parser():
    return WebScraperParser()


def test_parse_url_success(parser):
    mock_page = MagicMock()
    mock_page.locator.return_value.count.return_value = 0
    mock_page.locator.return_value.all.return_value = []
    mock_page.evaluate.return_value = "Extracted content from web page"

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    with patch("playwright.sync_api.sync_playwright") as mock_sync_playwright:
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

        result = parser.parse_url("https://example.com")

    assert result == "Extracted content from web page"
    mock_page.goto.assert_called()
    mock_browser.close.assert_called_once()


def test_parse_url_invalid_url(parser):
    with pytest.raises(ValueError, match="Invalid URL"):
        parser.parse_url("not-a-url")

    with pytest.raises(ValueError, match="Invalid URL"):
        parser.parse_url("")


def test_parse_url_with_iframe(parser):
    mock_page = MagicMock()
    mock_page.locator.return_value.count.return_value = 1
    mock_page.evaluate.side_effect = [
        "https://example.com/iframe",
        None,
        "Content from iframe",
    ]
    mock_page.locator.return_value.all.return_value = []

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    with patch("playwright.sync_api.sync_playwright") as mock_sync_playwright:
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

        result = parser.parse_url("https://example.com")

    assert result == "Content from iframe"
    assert mock_page.goto.call_count == 2


def test_parse_url_timeout(parser):
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

    mock_page = MagicMock()
    mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout 180000ms exceeded")

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    with patch("playwright.sync_api.sync_playwright") as mock_sync_playwright:
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

        with pytest.raises(TimeoutError, match="Browser timeout"):
            parser.parse_url("https://example.com")


def test_parse_url_no_text_extracted(parser):
    mock_page = MagicMock()
    mock_page.locator.return_value.count.return_value = 0
    mock_page.locator.return_value.all.return_value = []
    mock_page.evaluate.return_value = ""

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    with patch("playwright.sync_api.sync_playwright") as mock_sync_playwright:
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

        with pytest.raises(ValueError, match="No text extracted from URL"):
            parser.parse_url("https://example.com")


def test_parse_url_with_selector_nodes(parser):
    mock_node1 = MagicMock()
    mock_node1.inner_text.return_value = "Page 1 content"
    mock_node2 = MagicMock()
    mock_node2.inner_text.return_value = "Page 2 content"

    mock_page = MagicMock()
    mock_page.locator.return_value.count.return_value = 0
    mock_page.locator.return_value.all.return_value = [mock_node1, mock_node2]

    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    with patch("playwright.sync_api.sync_playwright") as mock_sync_playwright:
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright

        result = parser.parse_url("https://example.com")

    assert "Page 1 content" in result
    assert "Page 2 content" in result
