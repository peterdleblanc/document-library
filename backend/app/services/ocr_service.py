"""OCR service using Tesseract"""
import io
import logging
from typing import Optional
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

logger = logging.getLogger(__name__)


class OCRService:
    """Service for extracting text from images and scanned documents using Tesseract OCR"""

    def __init__(self):
        """Initialize the OCR service"""
        # Configure Tesseract if needed
        # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        pass

    def extract_text_from_image(self, image_data: bytes, mime_type: str) -> Optional[str]:
        """
        Extract text from an image using Tesseract OCR

        Args:
            image_data: Raw image bytes
            mime_type: MIME type of the image

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            logger.info(f"Performing OCR on image ({mime_type})")

            # Load image
            image = Image.open(io.BytesIO(image_data))

            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')

            if text:
                text = text.strip()
                logger.info(f"OCR extracted {len(text)} characters from image")
                return text
            else:
                logger.warning("No text extracted from image via OCR")
                return None

        except Exception as e:
            logger.error(f"Error during OCR processing: {str(e)}")
            return None

    def extract_text_from_pdf(self, pdf_data: bytes) -> Optional[str]:
        """
        Extract text from a PDF using OCR (for scanned PDFs)

        Args:
            pdf_data: Raw PDF bytes

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            logger.info("Performing OCR on PDF")

            # Convert PDF pages to images
            images = convert_from_bytes(pdf_data)

            # Extract text from each page
            all_text = []
            for page_num, image in enumerate(images, 1):
                logger.debug(f"OCR processing PDF page {page_num}/{len(images)}")

                # Perform OCR on page
                page_text = pytesseract.image_to_string(image, lang='eng')

                if page_text:
                    all_text.append(page_text.strip())

            # Combine all pages
            combined_text = "\n\n".join(all_text)

            if combined_text:
                logger.info(f"OCR extracted {len(combined_text)} characters from {len(images)} PDF pages")
                return combined_text
            else:
                logger.warning("No text extracted from PDF via OCR")
                return None

        except Exception as e:
            logger.error(f"Error during PDF OCR processing: {str(e)}")
            return None

    def extract_text(self, file_data: bytes, mime_type: str) -> Optional[str]:
        """
        Extract text from file using OCR (routes to appropriate method)

        Args:
            file_data: Raw file bytes
            mime_type: MIME type of the file

        Returns:
            Extracted text or None if extraction fails
        """
        if mime_type == "application/pdf":
            return self.extract_text_from_pdf(file_data)
        elif mime_type.startswith("image/"):
            return self.extract_text_from_image(file_data, mime_type)
        else:
            logger.warning(f"Unsupported MIME type for OCR: {mime_type}")
            return None

    def get_text_confidence(self, image_data: bytes) -> float:
        """
        Get OCR confidence score for an image

        Args:
            image_data: Raw image bytes

        Returns:
            Confidence score (0-100)
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            if confidences:
                return sum(confidences) / len(confidences)
            return 0.0

        except Exception as e:
            logger.error(f"Error calculating OCR confidence: {str(e)}")
            return 0.0


# Singleton instance
ocr_service = OCRService()
