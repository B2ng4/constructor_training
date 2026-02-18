from fastapi import Depends, HTTPException
import boto3
from botocore.exceptions import ClientError

from core.logging_config import logger
import uuid
from datetime import datetime
from botocore.config import Config
import os
from typing import Optional

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import configs
import mimetypes
import hashlib
import base64


class S3Service:
    def __init__(
        self,
        session: AsyncSession,
        aws_access_key_id: str = configs.AWS_ACCESS_KEY_ID,
        aws_secret_access_key: str = configs.AWS_SECRET_ACCESS_KEY,
        region_name: str = configs.S3_REGION_NAME,
        bucket_name: str = configs.S3_BUCKET_NAME,
        endpoint_url: str = configs.S3_ENDPOINT_URL,
    ):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url

        # Проверка и создание бакета при инициализации
        self._ensure_bucket_exists()

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

    async def upload_file(
        self, file_content: bytes, object_name: str, training_uuid: UUID4
    ) -> str:
        """Загружает файл в S3, сохраняет в БД и возвращает URL"""
        content_type, _ = mimetypes.guess_type(object_name)
        if content_type is None:
            content_type = "application/octet-stream"

        try:
            self.s3_client.put_object(
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
        key = "/".join(object_name.split("/photos/")[-1].split("/"))
        object_name = f"photos/{key}"
        logger.debug("Удаление объекта: {}", object_name)
        try:
            response = self.s3_client.delete_objects(
                Bucket=self.bucket_name, Delete={"Objects": [{"Key": object_name}]}
            )
            if "Deleted" in response:
                return True
            else:
                raise HTTPException(status_code=404, detail="Файл не удалён")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Ошибка при удалении файла: {str(e)}"
            )
