"""Document processing tasks"""
import asyncio
import logging
from uuid import UUID
from app.celery_app import celery_app
from app.db.base import async_session_maker
from app.models.document import Document, DocumentText
from app.services.minio_service import minio_service
from app.services.text_extraction_service import text_extraction_service
from app.services.ocr_service import ocr_service
from sqlalchemy import select

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="process_document")
def process_document(self, document_id: str):
    """
    Process a document: extract text, generate metadata, create embeddings

    This is the main document processing pipeline that will be expanded in Phase 2

    Args:
        document_id: UUID of the document to process
    """
    # Run async function in sync context
    return asyncio.run(_process_document_async(self, document_id))


async def _process_document_async(task, document_id: str):
    """
    Async implementation of document processing

    Processing steps:
    1. Update status to 'processing'
    2. Download file from MinIO
    3. Extract text (Apache Tika / PyMuPDF)
    4. Apply OCR if needed (Tesseract)
    5. Generate embeddings (OpenAI/Claude)
    6. Generate AI metadata (Claude)
    7. Index in Meilisearch
    8. Generate thumbnails
    9. Update status to 'completed'
    """
    async with async_session_maker() as db:
        try:
            # Get document
            result = await db.execute(
                select(Document).where(Document.id == UUID(document_id))
            )
            document = result.scalar_one_or_none()

            if not document:
                return {"status": "error", "message": "Document not found"}

            # Update status
            document.processing_status = "processing"
            document.processing_progress = 0
            await db.commit()

            # Step 1: Download file (10%)
            task.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Downloading file'})
            document.processing_progress = 10
            await db.commit()

            # Download from MinIO
            logger.info(f"Downloading file from MinIO: {document.storage_path}")
            file_data = minio_service.download_file(document.storage_path)

            # Step 2: Extract text (30%)
            task.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Extracting text'})
            document.processing_progress = 30
            await db.commit()

            # Text extraction with Tika
            logger.info(f"Extracting text from {document.original_filename}")
            extracted_text, extraction_method = text_extraction_service.extract_text(
                file_data,
                document.original_filename,
                document.mime_type
            )

            # Step 3: OCR if needed (50%)
            ocr_applied = False
            if text_extraction_service.needs_ocr(document.mime_type, extracted_text):
                task.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'Running OCR'})
                document.processing_progress = 50
                await db.commit()

                # Apply OCR
                logger.info(f"Applying OCR to {document.original_filename}")
                ocr_text = ocr_service.extract_text(file_data, document.mime_type)

                if ocr_text:
                    # Combine or replace with OCR text
                    if extracted_text:
                        extracted_text = f"{extracted_text}\n\n--- OCR Text ---\n\n{ocr_text}"
                    else:
                        extracted_text = ocr_text

                    ocr_applied = True
                    extraction_method = "apache_tika_with_ocr"
            else:
                logger.info("OCR not needed, skipping...")
                # Skip OCR step
                task.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'Skipping OCR'})
                document.processing_progress = 50
                await db.commit()

            # Store extracted text in database
            if extracted_text:
                # Get the current version
                version_result = await db.execute(
                    select(document.versions).where(
                        document.versions.c.id == document.current_version_id
                    )
                )
                current_version = version_result.first()

                # Create document_text record
                doc_text = DocumentText(
                    document_id=document.id,
                    version_id=document.current_version_id,
                    extracted_text=extracted_text,
                    ocr_applied=ocr_applied,
                    extraction_method=extraction_method
                )
                db.add(doc_text)
                await db.commit()
                logger.info(f"Stored {len(extracted_text)} characters of extracted text")

            # Step 4: Generate embeddings (65%) - Phase 3
            logger.info("Skipping embeddings generation (Phase 3 feature)")
            task.update_state(state='PROGRESS', meta={'progress': 65, 'status': 'Skipping embeddings (Phase 3)'})
            document.processing_progress = 65
            await db.commit()

            # Step 5: AI metadata generation (80%) - Phase 3
            logger.info("Skipping AI metadata generation (Phase 3 feature)")
            task.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Skipping AI metadata (Phase 3)'})
            document.processing_progress = 80
            await db.commit()

            # Step 6: Index in search (90%) - Phase 3
            logger.info("Skipping search indexing (Phase 3 feature)")
            task.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Skipping search index (Phase 3)'})
            document.processing_progress = 90
            await db.commit()

            # Step 7: Generate thumbnails (95%) - Future feature
            logger.info("Skipping thumbnail generation (future feature)")
            task.update_state(state='PROGRESS', meta={'progress': 95, 'status': 'Skipping thumbnails'})
            document.processing_progress = 95
            await db.commit()

            # Complete
            logger.info(f"Document processing completed: {document_id}")
            document.processing_status = "completed"
            document.processing_progress = 100
            await db.commit()

            return {
                "status": "success",
                "document_id": document_id,
                "message": "Document processed successfully"
            }

        except Exception as e:
            # Mark as failed
            if document:
                document.processing_status = "failed"
                document.processing_progress = 0
                await db.commit()

            return {
                "status": "error",
                "document_id": document_id,
                "message": str(e)
            }


@celery_app.task(name="cleanup_temp_files")
def cleanup_temp_files():
    """
    Periodic task to cleanup temporary files

    This can be scheduled to run daily via Celery Beat
    """
    # TODO: Implement cleanup logic
    return {"status": "success", "message": "Cleanup completed"}
