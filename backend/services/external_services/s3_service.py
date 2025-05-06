from fastapi import Depends, HTTPException
import boto3
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

    def generate_unique_filename(self, original_filename: str) -> str:
        """Генерирует уникальное имя файла на основе оригинального имени и временной метки"""
        extension = original_filename.split(".")[-1] if "." in original_filename else ""
        unique_id = str(uuid.uuid4())
        return f"photos/{unique_id}.{extension}"

    async def upload_file(self, file_content: bytes, object_name: str, training_uuid: UUID4) -> str:
        """Загружает файл в S3, сохраняет в БД и возвращает URL"""
        content_type, _ = mimetypes.guess_type(object_name)
        if content_type is None:
            content_type = "application/octet-stream"

        try:
            sha256_hash = hashlib.sha256(file_content).digest()
            sha256_hash_b64 = base64.b64encode(sha256_hash).decode("utf-8")
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file_content,
                ContentType=content_type,
                ChecksumSHA256=sha256_hash_b64,
            )
            file_url = (
                f"{self.endpoint_url.rstrip('/')}/{self.bucket_name}/{object_name}"
            )

            return file_url
        except Exception as e:
            print(f"Ошибка при загрузке файла: {str(e)}")
            raise e




    async def delete_file(self, object_name: str):
        key = "/".join(object_name.split("/photos/")[-1].split("/"))
        object_name = f"photos/{key}"
        print(f"Attempting to delete object: {object_name}")
        try:
            response = self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': [{'Key': object_name}]}
            )
            if 'Deleted' in response:
                return True
            else:
                raise HTTPException(status_code=404, detail="Файл не удалён")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении файла: {str(e)}")



