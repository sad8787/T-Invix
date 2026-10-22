import asyncio
import io
import uuid
from minio import Minio
from app.core.config import settings

class ImageStorage:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_bucket

    async def ensure_bucket(self):
        # MinIO may still be starting when the API container launches.
        for attempt in range(30):
            try:
                exists = await asyncio.to_thread(self.client.bucket_exists, self.bucket)
                if not exists:
                    await asyncio.to_thread(self.client.make_bucket, self.bucket)
                # Catalog images are public; never expose MinIO credentials to the frontend.
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                    }],
                }
                import json
                await asyncio.to_thread(self.client.set_bucket_policy, self.bucket, json.dumps(policy))
                return
            except Exception:
                if attempt == 29:
                    raise
                await asyncio.sleep(2)

    async def upload(self, content: bytes, content_type: str) -> str:
        ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[content_type]
        key = f"products/{uuid.uuid4().hex}{ext}"
        await asyncio.to_thread(
            self.client.put_object, self.bucket, key, io.BytesIO(content), len(content),
            content_type=content_type,
        )
        return key

    async def delete(self, key: str):
        try:
            await asyncio.to_thread(self.client.remove_object, self.bucket, key)
        except Exception:
            # Preserve the original DB exception; orphan cleanup can be handled separately.
            pass

storage = ImageStorage()
