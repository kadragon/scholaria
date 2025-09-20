"""Tests for API documentation (OpenAPI/Swagger)."""

from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIClient


class APIDocumentationTest(TestCase):
    """Test cases for API documentation endpoints."""

    def setUp(self) -> None:
        """Set up test client."""
        self.client = APIClient()

    def test_openapi_schema_endpoint_exists(self) -> None:
        """Test that OpenAPI schema endpoint is accessible."""
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/vnd.oai.openapi", response["Content-Type"])

    def test_swagger_ui_endpoint_exists(self) -> None:
        """Test that Swagger UI endpoint is accessible."""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])

    def test_redoc_endpoint_exists(self) -> None:
        """Test that ReDoc endpoint is accessible."""
        response = self.client.get("/api/redoc/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])

    def test_openapi_schema_contains_api_info(self) -> None:
        """Test that OpenAPI schema contains basic API information."""
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)

        # Parse the schema
        import yaml

        schema = yaml.safe_load(response.content)

        # Check basic schema structure
        self.assertIn("openapi", schema)
        self.assertIn("info", schema)
        self.assertIn("paths", schema)

        # Check API info
        info = schema["info"]
        self.assertIn("title", info)
        self.assertIn("version", info)
        self.assertIn("description", info)

    def test_openapi_schema_contains_topic_endpoints(self) -> None:
        """Test that OpenAPI schema contains topic endpoints."""
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)

        import yaml

        schema = yaml.safe_load(response.content)
        paths = schema["paths"]

        # Check topic endpoints exist
        self.assertIn("/api/topics/", paths)
        self.assertIn("/api/topics/{id}/", paths)

        # Check HTTP methods for topic list
        topic_list = paths["/api/topics/"]
        self.assertIn("get", topic_list)

        # Check HTTP methods for topic detail
        topic_detail = paths["/api/topics/{id}/"]
        self.assertIn("get", topic_detail)

    def test_openapi_schema_contains_ask_endpoint(self) -> None:
        """Test that OpenAPI schema contains the ask endpoint."""
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)

        import yaml

        schema = yaml.safe_load(response.content)
        paths = schema["paths"]

        # Check ask endpoint exists
        self.assertIn("/api/ask/", paths)

        # Check HTTP methods for ask endpoint
        ask_endpoint = paths["/api/ask/"]
        self.assertIn("post", ask_endpoint)

    def test_openapi_schema_contains_models(self) -> None:
        """Test that OpenAPI schema contains model definitions."""
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)

        import yaml

        schema = yaml.safe_load(response.content)

        # Check components section exists
        self.assertIn("components", schema)
        components = schema["components"]
        self.assertIn("schemas", components)

        schemas = components["schemas"]

        # Check for Topic serializer schema
        topic_schema_found = any(
            "Topic" in schema_name for schema_name in schemas.keys()
        )
        self.assertTrue(topic_schema_found, "Topic schema not found in OpenAPI spec")

        # Check for Question serializer schema
        question_schema_found = any(
            "Question" in schema_name for schema_name in schemas.keys()
        )
        self.assertTrue(
            question_schema_found, "Question schema not found in OpenAPI spec"
        )

    def test_openapi_schema_has_proper_tags(self) -> None:
        """Test that OpenAPI schema has proper tags for organization."""
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)

        import yaml

        schema = yaml.safe_load(response.content)
        paths = schema["paths"]

        # Check that endpoints have tags
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "patch", "delete"]:
                    self.assertIn(
                        "tags", details, f"No tags found for {method.upper()} {path}"
                    )

    def test_swagger_ui_contains_api_title(self) -> None:
        """Test that Swagger UI contains the API title."""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()
        # Should contain the API title in the HTML
        self.assertIn("RAG", content.upper())

    def test_redoc_contains_api_title(self) -> None:
        """Test that ReDoc contains the API title."""
        response = self.client.get("/api/redoc/")
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()
        # Should contain the API title in the HTML
        self.assertIn("RAG", content.upper())
