from unittest.mock import Mock, patch

import pytest

from backend.ingestion.parsers import WebScraperParser


@pytest.fixture
def parser():
    return WebScraperParser(puppeteer_url="http://test-puppeteer:3000")


def test_parse_url_success(parser):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "text": "Extracted content from web page",
        "metadata": {"url": "https://example.com"},
    }

    with patch("requests.post", return_value=mock_response):
        result = parser.parse_url("https://example.com")

    assert result == "Extracted content from web page"


def test_parse_url_invalid_url(parser):
    with pytest.raises(ValueError, match="Invalid URL"):
        parser.parse_url("not-a-url")

    with pytest.raises(ValueError, match="Invalid URL"):
        parser.parse_url("")


def test_parse_url_puppeteer_error(parser):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"error": "Scraping failed"}

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(ValueError, match="Puppeteer scraping failed"):
            parser.parse_url("https://example.com")


def test_parse_url_timeout(parser):
    import requests

    with patch("requests.post", side_effect=requests.Timeout):
        with pytest.raises(TimeoutError, match="Puppeteer service timeout"):
            parser.parse_url("https://example.com")


def test_parse_url_no_text_extracted(parser):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"text": "", "metadata": {}}

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(ValueError, match="No text extracted from URL"):
            parser.parse_url("https://example.com")


def test_parse_url_connection_error(parser):
    import requests

    with patch("requests.post", side_effect=requests.ConnectionError):
        with pytest.raises(ValueError, match="Failed to connect to Puppeteer service"):
            parser.parse_url("https://example.com")
