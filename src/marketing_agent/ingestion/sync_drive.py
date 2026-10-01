from marketing_agent.config.settings import settings
from marketing_agent.ingestion.chunker import split_text
from marketing_agent.ingestion.document_loader import (
    extract_text,
)
from marketing_agent.services.embedding_service import (
    EmbeddingService,
)
from marketing_agent.services.google_drive_service import (
    GoogleDriveService,
)
from marketing_agent.services.qdrant_service import (
    QdrantService,
)
from marketing_agent.utils.logger import get_logger

logger = get_logger(__name__)


def sync_drive() -> None:
    drive_service = GoogleDriveService()
    embedding_service = EmbeddingService()
    qdrant_service = QdrantService()

    files = drive_service.list_files(
        settings.google_drive_folder_id
    )

    drive_file_ids = {
        file["id"]
        for file in files
    }

    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        modified_time = file["modifiedTime"]

        logger.info(
            "Checking file: %s",
            file_name,
        )

        existing_metadata = (
            qdrant_service.get_file_metadata(
                file_id=file_id
            )
        )

        if existing_metadata:
            existing_modified_time = (
                existing_metadata.get(
                    "modified_time"
                )
            )

            if (
                existing_modified_time
                == modified_time
            ):
                logger.info(
                    "Skipped unchanged file: %s",
                    file_name,
                )
                continue

            logger.info(
                "File changed, re-indexing: %s",
                file_name,
            )

            qdrant_service.delete_file_chunks(
                file_id=file_id
            )

        else:
            logger.info(
                "New file detected: %s",
                file_name,
            )

        content = drive_service.download_file(
            file_id=file_id,
            mime_type=file["mimeType"],
        )

        text = extract_text(
            content=content,
            mime_type=file["mimeType"],
        )

        chunks = split_text(text)

        if not chunks:
            logger.warning(
                "No text extracted: %s",
                file_name,
            )
            continue

        embeddings = (
            embedding_service.embed_documents(
                chunks
            )
        )

        qdrant_service.ensure_collection(
            vector_size=len(
                embeddings[0]
            )
        )

        qdrant_service.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
            metadata={
                "team": "learning",
                "file_id": file_id,
                "file_name": file_name,
                "modified_time": modified_time,
            },
        )

        logger.info(
            "Indexed file: %s (%s chunks)",
            file_name,
            len(chunks),
        )

    remove_deleted_files(
        drive_file_ids=drive_file_ids,
        qdrant_service=qdrant_service,
    )


def remove_deleted_files(
    drive_file_ids: set[str],
    qdrant_service: QdrantService,
) -> None:
    indexed_file_ids = (
        qdrant_service.get_indexed_file_ids(
            team="learning"
        )
    )

    deleted_file_ids = (
        indexed_file_ids - drive_file_ids
    )

    for file_id in deleted_file_ids:
        logger.info(
            "Deleted file detected: %s",
            file_id,
        )

        qdrant_service.delete_file_chunks(
            file_id=file_id
        )


def main() -> None:
    sync_drive()


if __name__ == "__main__":
    main()