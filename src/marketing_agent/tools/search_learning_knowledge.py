import argparse
import json

from marketing_agent.services.embedding_service import (
    EmbeddingService,
)
from marketing_agent.services.qdrant_service import (
    QdrantService,
)


def search_learning_knowledge(
    query: str,
    limit: int = 5,
    score_threshold: float = 0.65,
) -> list[dict]:
    embedding_service = EmbeddingService()
    qdrant_service = QdrantService()

    query_vector = embedding_service.embed_query(query)

    return qdrant_service.search(
        query_vector=query_vector,
        team="learning",
        limit=limit,
        score_threshold=score_threshold,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search Learning knowledge from Qdrant"
    )

    parser.add_argument(
        "query",
        type=str,
        help="Search query",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of results",
    )

    parser.add_argument(
        "--score-threshold",
        type=float,
        default=0.65,
        help="Minimum similarity score",
    )

    args = parser.parse_args()

    results = search_learning_knowledge(
        query=args.query,
        limit=args.limit,
        score_threshold=args.score_threshold,
    )

    print(
        json.dumps(
            {
                "query": args.query,
                "count": len(results),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()