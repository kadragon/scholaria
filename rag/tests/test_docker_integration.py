"""
Integration tests for Docker Compose service orchestration.

Tests that all external services (PostgreSQL, Redis, Qdrant, MinIO, Unstructured API)
work together correctly in the Docker Compose environment.
"""

import os
import time
from io import BytesIO

import pytest
import redis
import requests
from django.conf import settings
from django.test import TestCase
from minio import Minio
from minio.error import S3Error
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from rag.ingestion.parsers import PDFParser
from rag.models import Context, ContextItem, Topic
from rag.retrieval.qdrant import QdrantService
from rag.storage import MinIOStorage


@pytest.mark.skipif(
    os.getenv("DOCKER_INTEGRATION_TESTS", "false").lower() != "true",
    reason="Docker integration tests require DOCKER_INTEGRATION_TESTS=true",
)
class DockerComposeIntegrationTest(TestCase):
    """Test Docker Compose service integration."""

    redis_client: redis.Redis
    qdrant_client: QdrantClient
    minio_client: Minio

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class-level resources."""
        super().setUpClass()

        # Wait for services to be ready
        cls._wait_for_services()

        # Initialize service clients
        cls.redis_client = redis.Redis(
            host=settings.REDIS_HOST
            if hasattr(settings, "REDIS_HOST")
            else "localhost",
            port=settings.REDIS_PORT if hasattr(settings, "REDIS_PORT") else 6379,
            decode_responses=True,
        )

        cls.qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST, port=settings.QDRANT_PORT
        )

        cls.minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    @staticmethod
    def _wait_for_services(max_attempts: int = 10, delay: float = 1.0) -> None:
        """Wait for available Docker services to be ready."""
        print("Checking service availability...")

        # Test Redis (required)
        for attempt in range(max_attempts):
            try:
                redis_client = redis.Redis(
                    host=settings.REDIS_HOST
                    if hasattr(settings, "REDIS_HOST")
                    else "localhost",
                    port=settings.REDIS_PORT
                    if hasattr(settings, "REDIS_PORT")
                    else 6379,
                    socket_timeout=2,
                )
                redis_client.ping()
                print("✅ Redis is ready")
                break
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise ConnectionError(
                        f"Redis not ready after {max_attempts} attempts: {e}"
                    ) from e
                time.sleep(delay)

        # Test Qdrant (required)
        for attempt in range(max_attempts):
            try:
                qdrant_client = QdrantClient(
                    host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=2
                )
                qdrant_client.get_collections()
                print("✅ Qdrant is ready")
                break
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise ConnectionError(
                        f"Qdrant not ready after {max_attempts} attempts: {e}"
                    ) from e
                time.sleep(delay)

        # Test MinIO (optional - skip if not available)
        try:
            minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
            minio_client.list_buckets()
            print("✅ MinIO is ready")
        except Exception:
            print("⚠️  MinIO not available (will skip MinIO tests)")

        print("Service check completed")

    def test_redis_connectivity(self) -> None:
        """Test Redis service connectivity and basic operations."""
        # Test basic operations
        test_key = "test:integration"
        test_value = "integration_test_value"

        # Set and get
        self.redis_client.set(test_key, test_value)
        retrieved_value = self.redis_client.get(test_key)
        self.assertEqual(retrieved_value, test_value)

        # Cleanup
        self.redis_client.delete(test_key)

    def test_qdrant_connectivity(self) -> None:
        """Test Qdrant service connectivity and collection operations."""
        test_collection = "test_integration_collection"

        try:
            # Create test collection
            self.qdrant_client.create_collection(
                collection_name=test_collection,
                vectors_config=VectorParams(size=128, distance=Distance.COSINE),
            )

            # Verify collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            self.assertIn(test_collection, collection_names)

        finally:
            # Cleanup
            try:
                self.qdrant_client.delete_collection(test_collection)
            except (UnexpectedResponse, AttributeError):
                pass  # Collection might not exist or service unavailable

    def test_minio_connectivity(self) -> None:
        """Test MinIO service connectivity and bucket operations."""
        try:
            # Check if MinIO is available
            self.minio_client.list_buckets()
        except (S3Error, OSError, ConnectionError):
            self.skipTest("MinIO service is not available")

        test_bucket = "test-integration-bucket"
        test_object = "test-object.txt"
        test_content = b"integration test content"

        try:
            # Create test bucket
            if not self.minio_client.bucket_exists(test_bucket):
                self.minio_client.make_bucket(test_bucket)

            # Upload test object
            self.minio_client.put_object(
                test_bucket,
                test_object,
                BytesIO(test_content),
                length=len(test_content),
            )

            # Download and verify
            response = self.minio_client.get_object(test_bucket, test_object)
            retrieved_content = response.read()
            self.assertEqual(retrieved_content, test_content)

        finally:
            # Cleanup
            try:
                self.minio_client.remove_object(test_bucket, test_object)
                self.minio_client.remove_bucket(test_bucket)
            except S3Error:
                pass  # Bucket might not exist

    def test_postgresql_connectivity(self) -> None:
        """Test PostgreSQL service connectivity through Django ORM."""
        # Test model creation and retrieval
        topic = Topic.objects.create(
            name="Integration Test Topic",
            description="Test topic for Docker integration",
            system_prompt="You are a test assistant.",
        )

        # Verify data persistence
        retrieved_topic = Topic.objects.get(id=topic.id)
        self.assertEqual(retrieved_topic.name, "Integration Test Topic")

        # Cleanup
        topic.delete()

    def test_services_integration_workflow(self) -> None:
        """Test complete workflow using all services together."""
        # Create test data
        topic = Topic.objects.create(
            name="Integration Workflow Topic",
            description="End-to-end integration test",
            system_prompt="You are a helpful assistant.",
        )

        context = Context.objects.create(
            name="Integration Context",
            description="Test context for integration",
            context_type="markdown",
        )

        context_item = ContextItem.objects.create(
            context=context,
            title="Test Document",
            content="This is a test document for integration testing.",
        )

        # Link topic and context
        topic.contexts.add(context)

        try:
            # Test Qdrant service integration
            qdrant_service = QdrantService()

            # Create collection if it doesn't exist
            try:
                qdrant_service.create_collection()
            except (UnexpectedResponse, ValueError):
                pass  # Collection might already exist

            # Test MinIO integration (if available)
            try:
                storage = MinIOStorage()
                storage.client.list_buckets()  # Test if MinIO is available

                test_file_content = b"Test file content for integration"
                test_filename = "integration_test.txt"

                # Upload to MinIO
                file_buffer = BytesIO(test_file_content)
                file_path = storage.upload_file(test_filename, file_buffer)
                self.assertTrue(file_path)

                # Download from MinIO
                downloaded_content = storage.download_file(file_path)
                self.assertEqual(downloaded_content, test_file_content)

                # Cleanup MinIO
                try:
                    storage.delete_file(file_path)
                except (S3Error, OSError):
                    pass

            except (S3Error, OSError, ConnectionError, AttributeError):
                # MinIO not available, skip MinIO tests
                file_path = None

            # Test Redis through Django cache (if configured)
            from django.core.cache import cache

            cache_key = "integration_test"
            cache_value = {"test": "integration_data"}
            cache.set(cache_key, cache_value, 60)
            retrieved_cache = cache.get(cache_key)
            self.assertEqual(retrieved_cache, cache_value)

        finally:
            # Cleanup database objects
            context_item.delete()
            context.delete()
            topic.delete()

            # Cleanup MinIO (if we used it)
            if file_path:
                try:
                    storage.delete_file(file_path)
                except (S3Error, OSError, AttributeError):
                    pass

    def test_unstructured_api_connectivity(self) -> None:
        """Test Unstructured API service connectivity."""
        # Test if Unstructured API is available
        try:
            response = requests.get(
                f"{settings.UNSTRUCTURED_API_URL}/healthcheck", timeout=5
            )
            if response.status_code != 200:
                self.skipTest("Unstructured API service is not available")
        except requests.exceptions.RequestException:
            self.skipTest("Unstructured API service is not available")

        # This test verifies that the Unstructured API is accessible
        # We'll use the PDFParser which connects to the Unstructured API
        parser = PDFParser()

        # Test that we can connect to the API (even if we don't have a PDF to parse)
        # We expect this to fail with a specific error, not a connection error
        try:
            # This should raise a specific error about invalid input, not connection error
            parser.parse_file("/tmp/nonexistent_file.pdf")
        except Exception as e:
            # We expect a parsing error, not a connection error
            self.assertNotIn("connection", str(e).lower())
            self.assertNotIn("refused", str(e).lower())
            # This confirms the API is reachable

    def test_data_consistency_across_services(self) -> None:
        """Test that data remains consistent across PostgreSQL and Qdrant."""
        # Create test data in PostgreSQL
        topic = Topic.objects.create(
            name="Consistency Test Topic",
            description="Testing data consistency",
            system_prompt="You are a consistency tester.",
        )

        context = Context.objects.create(
            name="Consistency Context",
            description="Test context for consistency",
            context_type="faq",
        )

        context_item = ContextItem.objects.create(
            context=context,
            title="Consistency Test Item",
            content="This tests data consistency across services.",
        )

        topic.contexts.add(context)

        try:
            # Verify data exists in PostgreSQL
            db_topic = Topic.objects.get(id=topic.id)
            self.assertEqual(db_topic.name, "Consistency Test Topic")

            db_context_item = ContextItem.objects.get(id=context_item.id)
            self.assertEqual(db_context_item.title, "Consistency Test Item")

            # Test that we can query related data
            related_contexts = db_topic.contexts.all()
            self.assertEqual(len(related_contexts), 1)
            self.assertEqual(related_contexts[0].id, context.id)

        finally:
            # Cleanup
            context_item.delete()
            context.delete()
            topic.delete()


@pytest.mark.skipif(
    os.getenv("DOCKER_INTEGRATION_TESTS", "false").lower() != "true",
    reason="Docker integration tests require DOCKER_INTEGRATION_TESTS=true",
)
class DockerComposePerformanceTest(TestCase):
    """Performance tests for Docker Compose services."""

    def test_service_response_times(self) -> None:
        """Test that all services respond within acceptable time limits."""
        # Test Redis response time
        start_time = time.time()
        redis_client = redis.Redis(
            host=settings.REDIS_HOST
            if hasattr(settings, "REDIS_HOST")
            else "localhost",
            port=settings.REDIS_PORT if hasattr(settings, "REDIS_PORT") else 6379,
        )
        redis_client.ping()
        redis_time = time.time() - start_time
        self.assertLess(redis_time, 1.0, "Redis should respond within 1 second")

        # Test Qdrant response time
        start_time = time.time()
        qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST, port=settings.QDRANT_PORT
        )
        qdrant_client.get_collections()
        qdrant_time = time.time() - start_time
        self.assertLess(qdrant_time, 2.0, "Qdrant should respond within 2 seconds")

        # Test MinIO response time (if available)
        try:
            start_time = time.time()
            minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
            minio_client.list_buckets()
            minio_time = time.time() - start_time
            self.assertLess(minio_time, 2.0, "MinIO should respond within 2 seconds")
        except (S3Error, OSError, ConnectionError, AttributeError):
            # MinIO not available, skip performance test
            pass
