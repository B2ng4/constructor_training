import base64
from typing import BinaryIO
import hashlib
import mimetypes
import os
import threading
import uuid
from datetime import datetime
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import configs
from core.logging_config import logger


class S3Service:
    _bucket_checked: bool = False
    _bucket_check_lock = threading.Lock()

    def __init__(
        self,
        session: Optional[AsyncSession] = None,
        aws_access_key_id: str = configs.MINIO_ROOT_USER,
        aws_secret_access_key: str = configs.MINIO_ROOT_PASSWORD,
        region_name: str = "us-east-1",
        bucket_name: str = configs.MINIO_BUCKET,
        endpoint_url: str = configs.MINIO_ENDPOINT_URL,
    ):
        import botocore.config
        s3_config = botocore.config.Config(max_pool_connections=50)
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
            config=s3_config,
        )
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url

    def _ensure_bucket_exists_once(self) -> None:
        if self.__class__._bucket_checked:
            return
        with self.__class__._bucket_check_lock:
            if self.__class__._bucket_checked:
                return
            self._ensure_bucket_exists()
            self.__class__._bucket_checked = True

    def _ensure_bucket_exists(self):
        """Проверяет существование бакета и создает его если не существует"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info("Бакет {} существует", self.bucket_name)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                try:
                    # Для VK Cloud не нужен CreateBucketConfiguration
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        ACL="public-read",  # Делаем бакет публично читаемым
                    )
                    logger.info("Бакет {} успешно создан", self.bucket_name)
                except Exception as create_error:
                    logger.error("Ошибка при создании бакета: {}", create_error)
                    raise
            else:
                logger.error("Ошибка при проверке бакета: {}", e)
                raise

    def generate_unique_filename(self, original_filename: str) -> str:
        """Генерирует уникальное имя файла на основе оригинального имени и временной метки"""
        extension = original_filename.split(".")[-1] if "." in original_filename else ""
        unique_id = str(uuid.uuid4())
        return f"photos/{unique_id}.{extension}"

    def generate_task_object_key(
        self, user_id: int, original_filename: str, prefix: str = "tasks"
    ) -> str:
        extension = (
            original_filename.split(".")[-1] if "." in original_filename else "bin"
        )
        unique_id = str(uuid.uuid4())
        return f"{prefix}/{user_id}/{unique_id}.{extension}"

    def generate_result_object_key(
        self, user_id: int, task_id: str, original_filename: str
    ) -> str:
        extension = (
            original_filename.split(".")[-1] if "." in original_filename else "bin"
        )
        return f"tasks/{user_id}/results/{task_id}.{extension}"

    def upload_bytes_sync(
        self, file_content: bytes, object_name: str, content_type: str | None = None
    ) -> str:
        self._ensure_bucket_exists_once()
        if content_type is None:
            content_type, _ = mimetypes.guess_type(object_name)
        if content_type is None:
            content_type = "application/octet-stream"
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=object_name,
            Body=file_content,
            ContentType=content_type,
            ACL="public-read",
        )
        return f"{self.endpoint_url}/{self.bucket_name}/{object_name}"

    def upload_fileobj_sync(
        self, file_obj: BinaryIO, object_name: str, content_type: str | None = None
    ) -> str:
        self._ensure_bucket_exists_once()
        if content_type is None:
            content_type, _ = mimetypes.guess_type(object_name)
        if content_type is None:
            content_type = "application/octet-stream"
        self.s3_client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=self.bucket_name,
            Key=object_name,
            ExtraArgs={"ContentType": content_type, "ACL": "public-read"},
        )
        return f"{self.endpoint_url}/{self.bucket_name}/{object_name}"

    def download_bytes_sync(self, object_key: str) -> bytes:
        self._ensure_bucket_exists_once()
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_key)
        return response["Body"].read()

    @staticmethod
    def key_from_public_url(file_url: str, bucket_name: str, endpoint_url: str) -> str:
        """Извлекает S3 key из публичного URL."""
        prefix = f"{endpoint_url.rstrip('/')}/{bucket_name}/"
        if file_url.startswith(prefix):
            return file_url[len(prefix) :]
        if f"/{bucket_name}/" in file_url:
            return file_url.split(f"/{bucket_name}/", 1)[1]
        return file_url.split("/")[-1]

    async def upload_file(
        self, file_content: bytes, object_name: str, training_uuid: UUID4
    ) -> str:
        """Загружает файл в S3, сохраняет в БД и возвращает URL"""
        import asyncio
        await asyncio.to_thread(self._ensure_bucket_exists_once)

        content_type, _ = mimetypes.guess_type(object_name)
        if content_type is None:
            content_type = "application/octet-stream"

        try:
            # Выполняем синхронный вызов boto3 в отдельном потоке
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file_content,
                ContentType=content_type,
                ACL="public-read",
            )

            file_url = f"{self.endpoint_url}/{self.bucket_name}/{object_name}"

            return file_url
        except Exception as e:
            logger.error("Ошибка при загрузке файла: {}", str(e))
            raise e

    async def delete_file(self, object_name: str):
        """Удаляет файл из S3"""
        import asyncio
        await asyncio.to_thread(self._ensure_bucket_exists_once)

        key = "/".join(object_name.split("/photos/")[-1].split("/"))
        object_name = f"photos/{key}"
        logger.debug("Удаление объекта: {}", object_name)
        try:
            response = await asyncio.to_thread(
                self.s3_client.delete_objects,
                Bucket=self.bucket_name,
                Delete={"Objects": [{"Key": object_name}]},
            )
            if "Deleted" in response:
                return True
            else:
                raise HTTPException(status_code=404, detail="Файл не удалён")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Ошибка при удалении файла: {str(e)}"
            )
