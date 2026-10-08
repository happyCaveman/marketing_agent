from marketing_agent.services.supabase_storage_service import (
    SupabaseStorageService,
)


class MediaUrlService:
    def __init__(self):
        self.storage = (
            SupabaseStorageService()
        )

    def create_public_url(
        self,
        request_id: str,
        local_path: str,
    ) -> str:
        return self.storage.upload_image(
            request_id=request_id,
            local_path=local_path,
        )