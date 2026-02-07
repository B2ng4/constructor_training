from typing import List, Optional, Dict, Union, Any
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException, status
import requests
from PIL import Image
import io

from repositories.trainings_repository import TrainingRepository
from schemas.trainings import (
    TrainingCreate,
    TrainingResponse,
    TrainingUpdate,
    TrainingStepCreate,
    TrainingStepUpdate,
    TrainingStepResponse, TrainingListResponse, StepOrderUpdate
)

from models.trainings import Training, TrainingStep, TypesAction, Tags
from sqlalchemy.exc import IntegrityError

from services.BatchVideo_service import BatchVideoService
from services.external_services.s3_service import S3Service


class TrainingsService:
    def __init__(self, session: AsyncSession):
        self.repo = TrainingRepository(session)
        self.session = session

    async def create_training(
            self,
            training_data: TrainingCreate,
            creator_id: int
    ):
        """Создание тренинга с тегами и шагами"""
        try:
            training_dict = training_data.model_dump(
                exclude={"steps", "tag_ids"}
            )

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
                    detail="Не удалось создать тренинг"
                )

            if training_data.steps:
                for step_data in training_data.steps:
                    step = await self.create_training_step(step_data)
                    step.training_uuid = created_training.uuid
                    await self.repo.create_training_step(step)

            await self.session.commit()

            created_training = await self.repo.get_by_uuid_with_relations(created_training.uuid)

            if created_training:
                return TrainingResponse.model_validate(created_training)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось получить созданный тренинг"
            )

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка создания тренинга: {str(e)}"
            )

    async def create_training_step(
            self,
            step_data: TrainingStepCreate
    ) -> TrainingStep:
        """Создание объекта TrainingStep (без сохранения в БД)"""
        if step_data.action_type_id:
            action_type = await self.repo.get_action_type(step_data.action_type_id)
            if not action_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тип действия с ID {step_data.action_type_id} не найден"
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

    async def get_trainings_by_params(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> List[TrainingResponse]:
        """Получение списка тренингов с пагинацией"""
        trainings = await self.repo.get_all_with_relations(skip, limit)
        return [TrainingResponse.model_validate(t) for t in trainings]

    async def get_trainings_by_user_id(
            self,
            user_id: int
    ) -> List[TrainingListResponse]:
        """Получение тренингов пользователя БЕЗ шагов"""
        trainings = await self.repo.get_by_user_id(user_id)
        if not trainings:
            return None
        return [TrainingListResponse.model_validate(training) for training in trainings]

    async def patch_training(
            self,
            training_uuid: UUID4,
            training_data: TrainingUpdate
    ) -> TrainingResponse:
        """Частичное обновление тренинга и его шагов"""
        try:
            existing_training = await self.repo.get_by_uuid_with_relations(training_uuid)
            if not existing_training:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Тренинг не найден"
                )

            update_data = training_data.model_dump(
                exclude_unset=True,
                exclude={"steps", "tag_ids"}
            )
            if update_data:
                await self.repo.patch_training_fields(training_uuid, update_data)

            if hasattr(training_data, 'tag_ids') and training_data.tag_ids is not None:
                tags_result = await self.session.execute(
                    select(Tags).where(Tags.value.in_(training_data.tag_ids))
                )
                tags = tags_result.scalars().all()
                existing_training.tags = list(tags)
                await self.session.flush()

            if hasattr(training_data, 'steps') and training_data.steps is not None:
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
                detail=f"Непредвиденная ошибка: {str(e)}"
            )

    async def patch_training_steps(
            self,
            training_uuid: UUID4,
            steps_data: List[Union[TrainingStepCreate, TrainingStepUpdate]]
    ):
        """Частичное обновление шагов тренинга"""
        existing_steps = await self.repo.get_training_steps(training_uuid)
        existing_steps_dict = {step.id: step for step in existing_steps}

        for step_data in steps_data:
            step_id = getattr(step_data, 'id', None)

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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренинг не найден"
            )
        return True

    async def get_training_steps(self, training_uuid: UUID4) -> List[TrainingStep]:
        """Получение шагов тренинга"""
        return await self.repo.get_training_steps(training_uuid)

    async def create_steps_from_photos(
            self,
            training_uuid: UUID4,
            photo_urls: List[str]
    ) -> List[Dict]:
        """
        Создание шагов из фотографий с вычислением размеров.
        Этот метод делегирует сохранение в репозиторий.
        """
        try:
            # 1. Проверяем существование тренинга
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден"
                )

            steps_data_to_create = []

            existing_steps = await self.repo.get_training_steps(training_uuid)
            next_step_number = len(existing_steps) + 1

            for i, photo_url in enumerate(photo_urls):
                image_meta = self._get_image_dimensions(photo_url)

                steps_data_to_create.append({
                    "step_number": next_step_number + i,
                    "image_url": photo_url,
                    "meta": {
                        "name": "Шаг без названия",
                        "image_width": image_meta.get("width", 0),
                        "image_height": image_meta.get("height", 0),
                    }
                })

            created_steps_info = []

            for step_data in steps_data_to_create:
                new_step = TrainingStep(
                    step_number=step_data["step_number"],
                    meta=step_data["meta"],
                    training_uuid=training_uuid,
                    image_url=step_data["image_url"]
                )
                self.session.add(new_step)

                created_steps_info.append({
                    "step_number": step_data["step_number"],
                    "image_url": step_data["image_url"],
                    "dimensions": {
                        "width": step_data["meta"]["image_width"],
                        "height": step_data["meta"]["image_height"]
                    }
                })
            await self.session.commit()

            return created_steps_info

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка создания шагов из фотографий: {str(e)}"
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
            print(f"Warning: Не удалось получить размеры для {image_url}: {e}")
            return {"width": 0, "height": 0}

    async def add_step(
            self,
            training_uuid: UUID4,
            step_data: TrainingStepCreate
    ) -> TrainingStepResponse:
        """Добавление одного шага к тренингу"""
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден"
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
                detail=f"Ошибка добавления шага: {str(e)}"
            )

    async def add_steps_bulk(
            self,
            training_uuid: UUID4,
            steps_data: List[TrainingStepCreate]
    ) -> List[TrainingStepResponse]:
        """Массовое добавление шагов к тренингу"""
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден"
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
                detail=f"Ошибка добавления шагов: {str(e)}"
            )

    async def update_step(
            self,
            training_uuid: UUID4,
            step_id: int,
            step_data: TrainingStepUpdate
    ) -> TrainingStepResponse:
        """Обновление шага по UUID тренинга и ID шага"""
        try:
            existing_step = await self.repo.get_step_by_id_and_training(
                step_id, training_uuid
            )
            if not existing_step:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Шаг {step_id} не найден в тренинге {training_uuid}"
                )

            update_data = step_data.model_dump(
                exclude_unset=True,
                exclude={"id", "steps"}
            )

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
                detail=f"Ошибка обновления шага: {str(e)}"
            )

    async def delete_step(
            self,
            training_uuid: UUID4,
            step_id: int
    ) -> bool:
        """Удаление шага по UUID тренинга и ID шага"""
        try:
            existing_step = await self.repo.get_step_by_id_and_training(
                step_id, training_uuid
            )
            if not existing_step:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Шаг {step_id} не найден в тренинге {training_uuid}"
                )

            success = await self.repo.delete_training_step(step_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Шаг {step_id} не найден"
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
                detail=f"Ошибка удаления шага: {str(e)}"
            )

    async def delete_steps_bulk(
            self,
            training_uuid: UUID4,
            step_ids: List[int]
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
                "total_requested": len(step_ids)
            }

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка удаления шагов: {str(e)}"
            )

    async def reorder_steps(
            self,
            training_uuid: UUID4,
            steps_order: List[StepOrderUpdate]
    ) -> Dict[str, Any]:
        """Обновление порядка шагов в тренинге."""
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден"
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
                    detail="Один или несколько ID шагов не принадлежат указанному тренингу."
                )

            steps_to_update_dict = [step.model_dump() for step in steps_order]
            updated_count = await self.repo.bulk_update_step_numbers(steps_to_update_dict)

            await self.session.commit()

            return {
                "updated_count": updated_count,
                "total_requested": len(steps_order)
            }

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка обновления порядка шагов: {str(e)}"
            )

    async def add_steps_from_video(
            self,
            training_uuid: UUID4,
            video_file: UploadFile,
            video_service: BatchVideoService,
            s3_service: S3Service
    ) -> List[Dict]:
        """
        Обрабатывает видео: нарезает на кадры, загружает в S3, создает шаги в БД.
        """
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден"
                )
            frames_bytes = await video_service.extract_slides(video_file)

            if not frames_bytes:
                return []

            uploaded_urls = []

            # 3. Грузим в S3
            for i, frame_data in enumerate(frames_bytes):
                filename = f"video_slide_{i + 1:03d}.png"
                object_name = s3_service.generate_unique_filename(filename)

                url = await s3_service.upload_file(frame_data, object_name, training_uuid)
                uploaded_urls.append(url)
            created_steps = await self.create_steps_from_photos(training_uuid, uploaded_urls)

            return created_steps

        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка обработки видео и создания шагов: {str(e)}"
            )
