from google import genai

from marketing_agent.config.settings import settings


class EmbeddingService:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = settings.gemini_embedding_model

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )

        return [
            embedding.values
            for embedding in response.embeddings
        ]

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        response = self.client.models.embed_content(
            model=self.model,
            contents=query,
        )

        return response.embeddings[0].values