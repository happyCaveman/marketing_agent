from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    VectorParams,
)

from marketing_agent.config.settings import settings
from marketing_agent.utils.logger import get_logger


logger = get_logger(__name__)


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url
        )

        self.collection_name = settings.qdrant_collection

    def ensure_collection(
        self,
        vector_size: int,
    ) -> None:
        if self.client.collection_exists(
            self.collection_name
        ):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

        logger.info(
            "Created Qdrant collection: %s",
            self.collection_name,
        )

    def add_chunks(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict,
    ) -> None:
        points = []

        file_id = metadata["file_id"]

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            point_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{file_id}:{index}",
                )
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        **metadata,
                        "chunk_index": index,
                        "text": chunk,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        logger.info(
            "Stored %s chunks in Qdrant: %s",
            len(points),
            metadata["file_name"],
        )

    def get_file_metadata(
        self,
        file_id: str,
    ) -> dict | None:
        if not self.client.collection_exists(
            self.collection_name
        ):
            return None

        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="file_id",
                        match=MatchValue(value=file_id),
                    )
                ]
            ),
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if not points:
            return None

        return points[0].payload

    def get_indexed_file_ids(
        self,
        team: str,
    ) -> set[str]:
        if not self.client.collection_exists(
            self.collection_name
        ):
            return set()

        file_ids = set()
        offset = None

        while True:
            points, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="team",
                            match=MatchValue(value=team),
                        )
                    ]
                ),
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            for point in points:
                file_id = point.payload.get("file_id")

                if file_id:
                    file_ids.add(file_id)

            if next_offset is None:
                break

            offset = next_offset

        return file_ids

    def delete_file_chunks(
        self,
        file_id: str,
    ) -> None:
        if not self.client.collection_exists(
            self.collection_name
        ):
            return

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="file_id",
                            match=MatchValue(value=file_id),
                        )
                    ]
                )
            ),
        )

        logger.info(
            "Deleted existing chunks: file_id=%s",
            file_id,
        )

    def search(
        self,
        query_vector: list[float],
        team: str,
        limit: int = 5,
        score_threshold: float = 0.65,
    ) -> list[dict]:
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="team",
                        match=MatchValue(value=team),
                    )
                ]
            ),
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )

        return [
            {
                "score": round(point.score, 4),
                "text": point.payload.get("text"),
                "source": {
                    "file_name": point.payload.get("file_name"),
                    "file_id": point.payload.get("file_id"),
                    "modified_time": point.payload.get(
                        "modified_time"
                    ),
                    "chunk_index": point.payload.get(
                        "chunk_index"
                    ),
                },
            }
            for point in results.points
        ]