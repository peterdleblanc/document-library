"""Text extraction service using Apache Tika"""
import io
import logging
from typing import Optional, Tuple
from tika import parser as tika_parser

logger = logging.getLogger(__name__)


class TextExtractionService:
    """Service for extracting text from various document formats using Apache Tika"""

    def __init__(self):
        """Initialize the text extraction service"""
        pass

    def extract_text(self, file_data: bytes, filename: str, mime_type: str) -> Tuple[Optional[str], str]:
        """
        Extract text from a file using Apache Tika

        Args:
            file_data: Raw file bytes
            filename: Original filename (for context)
            mime_type: MIME type of the file

        Returns:
            Tuple of (extracted_text, extraction_method)
            Returns (None, error_message) if extraction fails
        """
        try:
            logger.info(f"Extracting text from {filename} ({mime_type})")

            # Use Tika to parse the file
            parsed = tika_parser.from_buffer(file_data)

            # Get extracted text
            text = parsed.get("content", "")

            if text:
                # Clean up the text
                text = text.strip()

                # Get metadata for logging
                metadata = parsed.get("metadata", {})
                logger.info(
                    f"Successfully extracted {len(text)} characters from {filename}. "
                    f"Detected type: {metadata.get('Content-Type', 'unknown')}"
                )

                return text, "apache_tika"
            else:
                logger.warning(f"No text extracted from {filename}")
                return None, "no_text_found"

        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            return None, f"error: {str(e)}"

    def get_metadata(self, file_data: bytes) -> dict:
        """
        Extract metadata from a file using Apache Tika

        Args:
            file_data: Raw file bytes

        Returns:
            Dictionary of metadata
        """
        try:
            parsed = tika_parser.from_buffer(file_data)
            return parsed.get("metadata", {})
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {}

    def is_text_based(self, mime_type: str) -> bool:
        """
        Determine if a file type typically contains extractable text

        Args:
            mime_type: MIME type of the file

        Returns:
            True if the file type typically contains text
        """
        text_based_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "text/html",
            "text/xml",
            "application/rtf",
        ]
        return mime_type in text_based_types

    def needs_ocr(self, mime_type: str, extracted_text: Optional[str]) -> bool:
        """
        Determine if a file needs OCR processing

        Args:
            mime_type: MIME type of the file
            extracted_text: Text extracted by Tika (if any)

        Returns:
            True if OCR should be applied
        """
        # Images always need OCR
        if mime_type.startswith("image/"):
            return True

        # PDFs with little or no text need OCR (likely scanned)
        if mime_type == "application/pdf":
            if not extracted_text or len(extracted_text.strip()) < 100:
                return True

        return False


# Singleton instance
text_extraction_service = TextExtractionService()
