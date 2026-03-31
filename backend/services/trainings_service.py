import io
import uuid
from typing import Any, Dict, List, Optional, Union

import requests
from fastapi import HTTPException, UploadFile, status
from PIL import Image
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.logging_config import logger
from models.trainings import (
    Tags,
    Training,
    TrainingPublication,
    TrainingStep,
    TypesAction,
)
from repositories.trainings_repository import TrainingRepository
from schemas.trainings import (
    PassageAnalyticsResponse,
    PassageCompleteRequest,
    PassageHistoryItemResponse,
    StepOrderUpdate,
    TrainingCreate,
    TrainingListResponse,
    TrainingResponse,
    TrainingStepCreate,
    TrainingStepResponse,
    TrainingStepUpdate,
    TrainingUpdate,
)
from services.BatchVideo_service import BatchVideoService
from services.external_services.s3_service import S3Service
from services.video_ai_service import VideoAIService

# ID типа действия «Нажатие клавиши» — область хранит только metaKeywords
ACTION_TYPE_KEY_PRESS_ID = 6

# Ключи из VideoAIService → id в typesactions (create_initial_actions.py)
ACTION_TYPE_KEY_TO_ID = {
    "left_click": 1,
    "right_click": 2,
    "double_click": 3,
    "hover": 4,
    "text_input": 5,
    "key_chord": 6,
}


class TrainingsService:
    def __init__(self, session: AsyncSession):
        self.repo = TrainingRepository(session)
        self.session = session

    async def create_training(self, training_data: TrainingCreate, creator_id: int):
        """Создание тренинга с тегами и шагами"""
        try:
            training_dict = training_data.model_dump(exclude={"steps", "tag_ids"})

            training = Training(**training_dict, creator_id=creator_id)

            if training_data.tag_ids:
                tags_result = await self.session.execute(
                    select(Tags).where(Tags.value.in_(training_data.tag_ids))
                )
                tags = tags_result.scalars().all()
                training.tags = list(tags)

            created_training = await self.repo.create(training)
            if not created_training:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Не удалось создать тренинг",
                )

            if training_data.steps:
                for step_data in training_data.steps:
                    step = await self.create_training_step(step_data)
                    step.training_uuid = created_training.uuid
                    await self.repo.create_training_step(step)

            await self.session.commit()

            created_training = await self.repo.get_by_uuid_with_relations(
                created_training.uuid
            )

            if created_training:
                return TrainingResponse.model_validate(created_training)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось получить созданный тренинг",
            )

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка создания тренинга: {str(e)}",
            )

    async def create_training_step(self, step_data: TrainingStepCreate) -> TrainingStep:
        """Создание объекта TrainingStep (без сохранения в БД)"""
        if step_data.action_type_id:
            action_type = await self.repo.get_action_type(step_data.action_type_id)
            if not action_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тип действия с ID {step_data.action_type_id} не найден",
                )

            step_dict = step_data.model_dump(exclude={"action_type_id"})
            return TrainingStep(**step_dict, action_type=action_type)
        else:
            step_dict = step_data.model_dump(exclude={"action_type_id"})
            return TrainingStep(**step_dict)

    async def get_training(self, training_uuid: UUID4) -> Optional[TrainingResponse]:
        """Получение тренинга по UUID с загрузкой всех relationships"""
        training = await self.repo.get_by_uuid_with_relations(training_uuid)
        if not training:
            return None
        return TrainingResponse.model_validate(training)

    async def publish_training(self, training_uuid: UUID4) -> str:
        """
        Публикует тренинг: ставит publish=True, создаёт/обновляет публикацию.
        Возвращает публичный access_token.
        """
        training = await self.repo.get_by_uuid_with_relations(training_uuid)
        if not training:
            raise HTTPException(status_code=404, detail="Тренинг не найден")

        training.publish = True

        training_data = TrainingResponse.model_validate(training).model_dump(
            mode="json"
        )
        access_token = str(uuid.uuid4())

        await self.repo.create_or_update_publication(
            training_uuid=training.uuid,
            access_token=access_token,
            snapshot_data=training_data,
        )

        await self.session.commit()

        return access_token

    async def unpublish_training(self, training_uuid: UUID4) -> None:
        """
        Снимает тренинг с публикации: ставит publish=False,
        деактивирует все активные публикации.
        """
        training = await self.repo.get_by_uuid_with_relations(training_uuid)
        if not training:
            raise HTTPException(status_code=404, detail="Тренинг не найден")

        training.publish = False
        await self.repo.deactivate_publication(training_uuid)
        await self.session.commit()

    async def get_public_training_data(self, access_token: str):
        """
        Получает данные тренинга для прохождения (для анонимного пользователя).
        Возвращает те же данные, что и GET /training/{uuid} — по training_uuid из публикации.
        """
        publication = await self.repo.get_publication_by_token(access_token)

        if not publication:
            raise HTTPException(
                status_code=404, detail="Тренинг не найден или доступ закрыт"
            )

        await self.repo.increment_publication_views(publication.id)
        await self.session.commit()

        training = await self.repo.get_by_uuid_with_relations(publication.training_uuid)
        if not training:
            raise HTTPException(
                status_code=404, detail="Тренинг не найден или доступ закрыт"
            )

        return TrainingResponse.model_validate(training)

    async def get_trainings_by_params(
        self, skip: int = 0, limit: int = 100
    ) -> List[TrainingResponse]:
        """Получение списка тренингов с пагинацией"""
        trainings = await self.repo.get_all_with_relations(skip, limit)
        return [TrainingResponse.model_validate(t) for t in trainings]

    async def get_trainings_by_user_id(
        self, user_id: int
    ) -> List[TrainingListResponse]:
        """Получение тренингов пользователя БЕЗ шагов"""
        trainings = await self.repo.get_by_user_id(user_id)
        if not trainings:
            return None

        result = []
        for training in trainings:
            item = TrainingListResponse.model_validate(training)
            active_pub = next((p for p in training.publications if p.is_active), None)
            if active_pub:
                item.public_link = f"/training/passage/{active_pub.access_token}"
            result.append(item)
        return result

    async def patch_training(
        self, training_uuid: UUID4, training_data: TrainingUpdate
    ) -> TrainingResponse:
        """Частичное обновление тренинга и его шагов"""
        try:
            existing_training = await self.repo.get_by_uuid_with_relations(
                training_uuid
            )
            if not existing_training:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Тренинг не найден"
                )

            update_data = training_data.model_dump(
                exclude_unset=True, exclude={"steps", "tag_ids"}
            )
            if update_data:
                await self.repo.patch_training_fields(training_uuid, update_data)

            if hasattr(training_data, "tag_ids") and training_data.tag_ids is not None:
                tags_result = await self.session.execute(
                    select(Tags).where(Tags.value.in_(training_data.tag_ids))
                )
                tags = tags_result.scalars().all()
                existing_training.tags = list(tags)
                await self.session.flush()

            if hasattr(training_data, "steps") and training_data.steps is not None:
                await self.patch_training_steps(training_uuid, training_data.steps)

            await self.session.commit()

            updated_training = await self.repo.get_by_uuid_with_relations(training_uuid)
            return TrainingResponse.model_validate(updated_training)

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Непредвиденная ошибка: {str(e)}",
            )

    async def patch_training_steps(
        self,
        training_uuid: UUID4,
        steps_data: List[Union[TrainingStepCreate, TrainingStepUpdate]],
    ):
        """Частичное обновление шагов тренинга"""
        existing_steps = await self.repo.get_training_steps(training_uuid)
        existing_steps_dict = {step.id: step for step in existing_steps}

        for step_data in steps_data:
            step_id = getattr(step_data, "id", None)

            if step_id and step_id in existing_steps_dict:
                update_data = step_data.model_dump(exclude_unset=True, exclude={"id"})
                if update_data:
                    await self.repo.update_training_step(step_id, update_data)
            elif not step_id:
                step = await self.create_training_step(step_data)
                step.training_uuid = training_uuid
                await self.repo.create_training_step(step)

    async def delete_training(self, training_uuid: UUID4) -> bool:
        """Удаление тренинга"""
        success = await self.repo.delete(training_uuid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Тренинг не найден"
            )
        return True

    async def get_training_steps(self, training_uuid: UUID4) -> List[TrainingStep]:
        """Получение шагов тренинга"""
        return await self.repo.get_training_steps(training_uuid)

    async def create_steps_from_photos(
        self, training_uuid: UUID4, photo_urls: List[str]
    ) -> List[Dict]:
        """
        Создание шагов из фотографий с вычислением размеров.
        Этот метод делегирует сохранение в репозиторий.
        """
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден",
                )

            steps_data_to_create = []

            existing_steps = await self.repo.get_training_steps(training_uuid)
            next_step_number = len(existing_steps) + 1

            for i, photo_url in enumerate(photo_urls):
                image_meta = self._get_image_dimensions(photo_url)
                sn = next_step_number + i

                steps_data_to_create.append(
                    {
                        "step_number": sn,
                        "image_url": photo_url,
                        "meta": {
                            "name": f"Шаг {sn}",
                        },
                        "photo_dimensions": {
                            "width": image_meta.get("width", 0),
                            "height": image_meta.get("height", 0),
                        },
                    }
                )

            created_steps_info = []

            for step_data in steps_data_to_create:
                new_step = TrainingStep(
                    step_number=step_data["step_number"],
                    meta=step_data["meta"],
                    training_uuid=training_uuid,
                    image_url=step_data["image_url"],
                    photo_dimensions=step_data["photo_dimensions"],
                )
                self.session.add(new_step)

                created_steps_info.append(
                    {
                        "step_number": step_data["step_number"],
                        "image_url": step_data["image_url"],
                        "dimensions": {
                            "width": step_data["photo_dimensions"]["width"],
                            "height": step_data["photo_dimensions"]["height"],
                        },
                    }
                )
            await self.session.commit()
            return created_steps_info

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка создания шагов из фотографий: {str(e)}",
            )

    def _get_image_dimensions(self, image_url: str) -> Dict[str, int]:
        """
        Загружает картинку из S3 и возвращает размеры.
        """
        try:
            img_response = requests.get(image_url, stream=True, timeout=5)
            img_response.raise_for_status()
            img = Image.open(io.BytesIO(img_response.content))
            return {
                "width": img.width,
                "height": img.height,
            }
        except Exception as e:
            logger.warning("Не удалось получить размеры для {}: {}", image_url, e)
            return {"width": 0, "height": 0}

    async def add_step(
        self, training_uuid: UUID4, step_data: TrainingStepCreate
    ) -> TrainingStepResponse:
        """Добавление одного шага к тренингу"""
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден",
                )

            step = await self.create_training_step(step_data)
            step.training_uuid = training_uuid
            created_step = await self.repo.create_training_step(step)

            await self.session.commit()
            await self.session.refresh(created_step)

            return TrainingStepResponse.model_validate(created_step)

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка добавления шага: {str(e)}",
            )

    async def add_steps_bulk(
        self, training_uuid: UUID4, steps_data: List[TrainingStepCreate]
    ) -> List[TrainingStepResponse]:
        """Массовое добавление шагов к тренингу"""
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден",
                )

            created_steps = []
            for step_data in steps_data:
                step = await self.create_training_step(step_data)
                step.training_uuid = training_uuid
                created_step = await self.repo.create_training_step(step)
                created_steps.append(created_step)

            await self.session.commit()

            for step in created_steps:
                await self.session.refresh(step)

            return [TrainingStepResponse.model_validate(step) for step in created_steps]

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка добавления шагов: {str(e)}",
            )

    async def update_step(
        self, training_uuid: UUID4, step_id: int, step_data: TrainingStepUpdate
    ) -> TrainingStepResponse:
        """Обновление шага по UUID тренинга и ID шага"""
        try:
            existing_step = await self.repo.get_step_by_id_and_training(
                step_id, training_uuid
            )
            if not existing_step:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Шаг {step_id} не найден в тренинге {training_uuid}",
                )

            update_data = step_data.model_dump(
                exclude_unset=True, exclude={"id", "steps"}
            )

            # Merge meta and area for partial updates (preserve existing keys)
            if "meta" in update_data and update_data["meta"] is not None:
                existing_meta = existing_step.meta or {}
                if isinstance(existing_meta, dict):
                    update_data["meta"] = {**existing_meta, **update_data["meta"]}

            if "area" in update_data and update_data["area"] is not None:
                existing_area = existing_step.area or {}
                if isinstance(existing_area, dict):
                    update_data["area"] = {**existing_area, **update_data["area"]}

            # keyPress: область только metaKeywords, без координат
            if update_data.get("action_type_id") == ACTION_TYPE_KEY_PRESS_ID:
                area_src = update_data.get("area") or {}
                update_data["area"] = {
                    "metaKeywords": (
                        area_src.get("metaKeywords")
                        if isinstance(area_src.get("metaKeywords"), list)
                        else []
                    )
                }

            if update_data:
                await self.repo.update_training_step(step_id, update_data)

            await self.session.commit()

            updated_step = await self.repo.get_step_by_id(step_id)
            return TrainingStepResponse.model_validate(updated_step)

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка обновления шага: {str(e)}",
            )

    async def delete_step(self, training_uuid: UUID4, step_id: int) -> bool:
        """Удаление шага по UUID тренинга и ID шага"""
        try:
            existing_step = await self.repo.get_step_by_id_and_training(
                step_id, training_uuid
            )
            if not existing_step:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Шаг {step_id} не найден в тренинге {training_uuid}",
                )

            success = await self.repo.delete_training_step(step_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Шаг {step_id} не найден",
                )

            await self.session.commit()
            return True

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка удаления шага: {str(e)}",
            )

    async def delete_steps_bulk(
        self, training_uuid: UUID4, step_ids: List[int]
    ) -> Dict[str, Any]:
        """Массовое удаление шагов по UUID тренинга и списку ID"""
        try:
            deleted_count = 0
            not_found = []

            for step_id in step_ids:
                existing_step = await self.repo.get_step_by_id_and_training(
                    step_id, training_uuid
                )
                if not existing_step:
                    not_found.append(step_id)
                    continue

                success = await self.repo.delete_training_step(step_id)
                if success:
                    deleted_count += 1
                else:
                    not_found.append(step_id)

            await self.session.commit()

            return {
                "deleted": deleted_count,
                "not_found": not_found,
                "total_requested": len(step_ids),
            }

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка удаления шагов: {str(e)}",
            )

    async def reorder_steps(
        self, training_uuid: UUID4, steps_order: List[StepOrderUpdate]
    ) -> Dict[str, Any]:
        """Обновление порядка шагов в тренинге."""
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден",
                )

            if not steps_order:
                return {"updated_count": 0, "total_requested": 0}

            step_ids_to_update = [step.id for step in steps_order]
            validated_steps_count = await self.repo.count_steps_in_training(
                training_uuid, step_ids_to_update
            )

            if validated_steps_count != len(step_ids_to_update):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Один или несколько ID шагов не принадлежат указанному тренингу.",
                )

            steps_to_update_dict = [step.model_dump() for step in steps_order]
            updated_count = await self.repo.bulk_update_step_numbers(
                steps_to_update_dict
            )

            await self.session.commit()

            return {"updated_count": updated_count, "total_requested": len(steps_order)}

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка обновления порядка шагов: {str(e)}",
            )

    async def add_steps_from_video(
        self,
        training_uuid: UUID4,
        video_file: UploadFile,
        video_ai_service: VideoAIService,
        s3_service: S3Service,
    ) -> List[Dict]:
        """
        Обрабатывает видео через AI-модель:
        1. Отправляет видео в AI для анализа действий
        2. Извлекает кадры по таймкодам
        3. Загружает кадры в S3
        4. Создаёт шаги с описанием и координатами области действия
        """
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден",
                )

            ai_steps = await video_ai_service.analyze_video(video_file)

            if not ai_steps:
                return []

            DEFAULT_ACTION_TYPE_ID = 1

            existing_steps = await self.repo.get_training_steps(training_uuid)
            next_step_number = len(existing_steps) + 1

            created_steps_info = []

            for i, step_data in enumerate(ai_steps):
                filename = f"video_ai_step_{i + 1:03d}.png"
                object_name = s3_service.generate_unique_filename(filename)
                image_url = await s3_service.upload_file(
                    step_data.frame_bytes, object_name, training_uuid
                )

                image_url_after: Optional[str] = None
                if step_data.after_frame_bytes:
                    after_name = s3_service.generate_unique_filename(
                        f"video_ai_step_{i + 1:03d}_after.png"
                    )
                    image_url_after = await s3_service.upload_file(
                        step_data.after_frame_bytes, after_name, training_uuid
                    )

                bbox = step_data.bbox
                # Нормализованные (0..1) и пиксельные bbox (legacy/шум модели).
                # Если значения > 1 — трактуем как абсолютные пиксели кадра.
                if max(bbox) > 1.0:
                    x1 = max(0.0, min(float(step_data.frame_width), float(bbox[0])))
                    y1 = max(0.0, min(float(step_data.frame_height), float(bbox[1])))
                    x2 = max(0.0, min(float(step_data.frame_width), float(bbox[2])))
                    y2 = max(0.0, min(float(step_data.frame_height), float(bbox[3])))
                    x_min, x_max = min(x1, x2), max(x1, x2)
                    y_min, y_max = min(y1, y2), max(y1, y2)
                    area: Dict[str, Any] = {
                        "x": x_min,
                        "y": y_min,
                        "width": max(1.0, x_max - x_min),
                        "height": max(1.0, y_max - y_min),
                    }
                else:
                    x1 = max(0.0, min(1.0, float(bbox[0])))
                    y1 = max(0.0, min(1.0, float(bbox[1])))
                    x2 = max(0.0, min(1.0, float(bbox[2])))
                    y2 = max(0.0, min(1.0, float(bbox[3])))
                    x_min, x_max = min(x1, x2), max(x1, x2)
                    y_min, y_max = min(y1, y2), max(y1, y2)
                    area = {
                        "x": x_min * step_data.frame_width,
                        "y": y_min * step_data.frame_height,
                        "width": max(1.0, (x_max - x_min) * step_data.frame_width),
                        "height": max(1.0, (y_max - y_min) * step_data.frame_height),
                    }

                action_key = (step_data.action_type_key or "left_click").lower()
                action_type_id = ACTION_TYPE_KEY_TO_ID.get(
                    action_key, DEFAULT_ACTION_TYPE_ID
                )

                if action_key == "text_input" and step_data.expected_text:
                    area["metaText"] = step_data.expected_text
                if action_key == "key_chord" and step_data.key_chord:
                    area["metaKeywords"] = list(step_data.key_chord)

                step_meta: Dict[str, Any] = {
                    "name": step_data.step_title,
                    "source": "video_ai",
                    "ai_timecode": step_data.timecode,
                    "ai_timecode_before": step_data.timecode_before or step_data.timecode,
                    "ai_timecode_after": step_data.timecode_after,
                }
                if image_url_after:
                    step_meta["image_url_after"] = image_url_after

                new_step = TrainingStep(
                    step_number=next_step_number + i,
                    meta=step_meta,
                    training_uuid=training_uuid,
                    image_url=image_url,
                    photo_dimensions={
                        "width": step_data.frame_width,
                        "height": step_data.frame_height,
                    },
                    area=area,
                    action_type_id=action_type_id,
                    annotation=step_data.instruction_md,
                )
                self.session.add(new_step)

                created_steps_info.append(
                    {
                        "step_number": next_step_number + i,
                        "image_url": image_url,
                        "image_url_after": image_url_after,
                        "name": step_data.step_title,
                        "timecode": step_data.timecode,
                        "timecode_before": step_data.timecode_before,
                        "timecode_after": step_data.timecode_after,
                        "area": area,
                        "action_type_id": action_type_id,
                        "action_type_key": action_key,
                        "dimensions": {
                            "width": step_data.frame_width,
                            "height": step_data.frame_height,
                        },
                    }
                )

            await self.session.commit()
            return created_steps_info

        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка AI-анализа видео и создания шагов: {str(e)}",
            )

    async def _require_training_owner(
        self, training_uuid: UUID4, creator_id: int
    ) -> Training:
        training = await self.repo.get_by_uuid(training_uuid)
        if not training or training.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этому тренингу",
            )
        return training

    async def start_public_passage_attempt(self, access_token: str) -> dict:
        publication = await self.repo.get_publication_by_token(access_token)
        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренинг не найден или доступ закрыт",
            )
        att = await self.repo.create_passage_attempt(publication.id)
        await self.session.commit()
        return {"attempt_id": att.id}

    async def complete_public_passage_attempt(
        self, access_token: str, body: PassageCompleteRequest
    ) -> dict:
        publication = await self.repo.get_publication_by_token(access_token)
        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренинг не найден или доступ закрыт",
            )
        ok = await self.repo.complete_passage_attempt(
            body.attempt_id,
            publication.id,
            body.is_completed,
            body.duration_seconds,
            body.wrong_attempts_total,
        )
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Попытка не найдена или уже завершена",
            )
        await self.session.commit()
        return {"success": True}

    async def get_passage_analytics_for_creator(
        self, training_uuid: UUID4, creator_id: int
    ) -> PassageAnalyticsResponse:
        await self._require_training_owner(training_uuid, creator_id)
        stats = await self.repo.get_passage_stats_for_training(training_uuid)
        return PassageAnalyticsResponse(**stats)

    async def get_passage_history_for_creator(
        self,
        training_uuid: UUID4,
        creator_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[PassageHistoryItemResponse]:
        await self._require_training_owner(training_uuid, creator_id)
        rows = await self.repo.list_passage_attempts_for_training(
            training_uuid, skip=skip, limit=min(limit, 100)
        )
        return [PassageHistoryItemResponse.model_validate(r) for r in rows]
