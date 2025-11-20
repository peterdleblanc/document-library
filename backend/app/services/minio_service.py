"""MinIO service for object storage operations"""
import io
import hashlib
from typing import BinaryIO, Optional
from minio import Minio
from minio.error import S3Error
from app.core.config import settings


class MinIOService:
    """Service for interacting with MinIO object storage"""

    def __init__(self):
        """Initialize MinIO client"""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET_DOCUMENTS
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                print(f"Created bucket: {self.bucket}")
        except S3Error as e:
            print(f"Error checking/creating bucket: {e}")
            raise

    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str,
        file_size: int
    ) -> str:
        """
        Upload a file to MinIO

        Args:
            file_data: File data as binary stream
            object_name: Path/name for the object in MinIO
            content_type: MIME type of the file
            file_size: Size of the file in bytes

        Returns:
            str: Path to the uploaded object
        """
        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            print(f"Error uploading file to MinIO: {e}")
            raise

    def download_file(self, object_name: str) -> bytes:
        """
        Download a file from MinIO

        Args:
            object_name: Path/name of the object in MinIO

        Returns:
            bytes: File content as bytes
        """
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error downloading file from MinIO: {e}")
            raise

    def download_file_stream(self, object_name: str):
        """
        Download a file from MinIO as a stream (for large files)

        Args:
            object_name: Path/name of the object in MinIO

        Returns:
            Stream response
        """
        try:
            return self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
        except S3Error as e:
            print(f"Error streaming file from MinIO: {e}")
            raise

    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from MinIO

        Args:
            object_name: Path/name of the object in MinIO

        Returns:
            bool: True if successful
        """
        try:
            self.client.remove_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
            return True
        except S3Error as e:
            print(f"Error deleting file from MinIO: {e}")
            raise

    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in MinIO

        Args:
            object_name: Path/name of the object in MinIO

        Returns:
            bool: True if file exists
        """
        try:
            self.client.stat_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
            return True
        except S3Error:
            return False

    def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """
        Generate a presigned URL for downloading a file

        Args:
            object_name: Path/name of the object in MinIO
            expires: URL expiration time in seconds (default 1 hour)

        Returns:
            str: Presigned URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            raise


def calculate_file_hash(file_data: BinaryIO) -> tuple[str, int]:
    """
    Calculate SHA-256 hash and size of a file

    Args:
        file_data: File data as binary stream

    Returns:
        tuple: (hash_string, file_size)
    """
    sha256_hash = hashlib.sha256()
    file_size = 0

    # Read file in chunks to handle large files
    chunk_size = 8192
    while chunk := file_data.read(chunk_size):
        sha256_hash.update(chunk)
        file_size += len(chunk)

    # Reset file pointer to beginning
    file_data.seek(0)

    return sha256_hash.hexdigest(), file_size


# Singleton instance
minio_service = MinIOService()
