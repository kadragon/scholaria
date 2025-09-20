from __future__ import annotations

import logging
from io import BytesIO
from typing import TYPE_CHECKING

from django.conf import settings
from minio import Minio
from minio.error import S3Error

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


class MinIOStorage:
    """MinIO storage service for file operations."""

    # Class-level tracking of bucket existence to avoid repeated API calls
    _bucket_verified: dict[str, bool] = {}

    def __init__(self) -> None:
        """Initialize MinIO client with configuration from Django settings."""
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    def upload_file(self, object_name: str, file_data: BytesIO) -> str:
        """Upload a file to MinIO bucket.

        Args:
            object_name: Name of the object in MinIO
            file_data: BytesIO object containing file data

        Returns:
            Object name if successful

        Raises:
            S3Error: If upload fails
        """
        try:
            file_data.seek(0)
            length = len(file_data.getvalue())

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=length,
            )

            logger.info(f"Successfully uploaded {object_name} to {self.bucket_name}")
            return object_name

        except S3Error as e:
            logger.error(f"Failed to upload {object_name}: {e}")
            raise

    def download_file(self, object_name: str) -> bytes:
        """Download a file from MinIO bucket.

        Args:
            object_name: Name of the object in MinIO

        Returns:
            File content as bytes

        Raises:
            S3Error: If download fails
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            logger.info(
                f"Successfully downloaded {object_name} from {self.bucket_name}"
            )
            return data

        except S3Error as e:
            logger.error(f"Failed to download {object_name}: {e}")
            raise

    def file_exists(self, object_name: str) -> bool:
        """Check if a file exists in MinIO bucket.

        Args:
            object_name: Name of the object in MinIO

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    def delete_file(self, object_name: str) -> bool:
        """Delete a file from MinIO bucket.

        Args:
            object_name: Name of the object in MinIO

        Returns:
            True if successful, False if file not found
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Successfully deleted {object_name} from {self.bucket_name}")
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                logger.warning(f"File {object_name} not found for deletion")
                return False
            logger.error(f"Failed to delete {object_name}: {e}")
            raise

    def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """Generate a presigned URL for file access.

        Args:
            object_name: Name of the object in MinIO
            expires: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL for file access

        Raises:
            S3Error: If URL generation fails
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name, object_name, expires=expires
            )
            logger.info(f"Generated presigned URL for {object_name}")
            return url

        except S3Error as e:
            logger.error(f"Failed to generate URL for {object_name}: {e}")
            raise

    def upload_django_file(self, uploaded_file: UploadedFile) -> str | None:
        """Upload a Django UploadedFile to MinIO.

        Args:
            uploaded_file: Django UploadedFile instance

        Returns:
            Object name if successful

        Raises:
            S3Error: If upload fails
        """
        try:
            if not uploaded_file.name:
                logger.error("Cannot upload file without name")
                return None

            uploaded_file.seek(0)
            file_size = uploaded_file.size or 0

            # Handle content_type for FieldFile vs UploadedFile
            content_type = getattr(uploaded_file, "content_type", None)
            if not content_type and uploaded_file.name:
                # Infer content type from file extension
                if uploaded_file.name.lower().endswith(".pdf"):
                    content_type = "application/pdf"
                elif uploaded_file.name.lower().endswith((".md", ".markdown")):
                    content_type = "text/markdown"
                elif uploaded_file.name.lower().endswith(".txt"):
                    content_type = "text/plain"
                else:
                    content_type = "application/octet-stream"

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=uploaded_file.name,
                data=uploaded_file,
                length=file_size,
                content_type=content_type,
            )

            logger.info(f"Successfully uploaded Django file {uploaded_file.name}")
            return uploaded_file.name

        except S3Error as e:
            logger.error(f"Failed to upload Django file {uploaded_file.name}: {e}")
            raise

    def list_files(self, prefix: str = "") -> list[str]:
        """List files in MinIO bucket with optional prefix filter.

        Args:
            prefix: Optional prefix to filter objects

        Returns:
            List of object names
        """
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix)
            file_names = [obj.object_name for obj in objects]
            logger.info(f"Listed {len(file_names)} files with prefix '{prefix}'")
            return file_names

        except S3Error as e:
            logger.error(f"Failed to list files: {e}")
            raise

    def ensure_bucket_exists(self) -> None:
        """Ensure the configured bucket exists, create if it doesn't.

        Uses class-level caching to avoid repeated API calls.

        Raises:
            S3Error: If bucket creation fails
        """
        # Use endpoint + bucket_name as key to handle multiple MinIO configurations
        cache_key = f"{settings.MINIO_ENDPOINT}:{self.bucket_name}"

        if cache_key in self._bucket_verified:
            return

        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket {self.bucket_name}")
            else:
                logger.debug(f"Bucket {self.bucket_name} already exists")

            # Mark as verified
            self._bucket_verified[cache_key] = True

        except S3Error as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise
