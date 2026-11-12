import asyncio
import io
import uuid
from typing import Any, Dict, List, Optional, Union

import requests
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status
from PIL import Image
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.config import configs, public_passage_link
from core.logging_config import logger
from models.trainings import (
    Tags,
    Training,
    TrainingPublication,
    TrainingStep,
    TypesAction,
)
from models.users import User
from repositories.trainings_repository import TrainingRepository
from schemas.trainings import (
    PassageAnalyticsResponse,
    PassageCompleteRequest,
    PassageHistoryItemResponse,
    ScenarioGraphResponse,
    ScenarioGraphUpdate,
    ScenarioTransitionResponse,
    StepOrderUpdate,
    TrainingCreate,
    TrainingListResponse,
    TrainingResponse,
    TrainingStepCreate,
    TrainingStepResponse,
    TrainingStepUpdate,
    TrainingUpdate,
)
from services.external_services.s3_service import S3Service
from services.video_ai_service import VideoAIService
from services.pdf_ai_service import PdfAiService

# ID типа действия «Нажатие клавиши» — область хранит только metaKeywords
ACTION_TYPE_KEY_PRESS_ID = 6
ACTION_TYPE_INPUT_TEXT_ID = 5

_AREA_COORD_KEYS = frozenset({"x", "y", "width", "height", "actions"})


def _sanitize_area_for_action_type(
    area: Optional[Dict], action_type_id: Optional[int]
) -> Optional[Dict]:
    """Убирает metaText с шагов-кликов — иначе прохождение требует ввод текста."""
    if not isinstance(area, dict):
        return area
    if action_type_id == ACTION_TYPE_KEY_PRESS_ID:
        keywords = area.get("metaKeywords")
        return {
            "metaKeywords": keywords if isinstance(keywords, list) else [],
        }
    if action_type_id == ACTION_TYPE_INPUT_TEXT_ID:
        return area
    return {
        k: v
        for k, v in area.items()
        if k in _AREA_COORD_KEYS and v is not None
    }

# Ключи из VideoAIService → id в typesactions (create_initial_actions.py)
ACTION_TYPE_KEY_TO_ID = {
    "left_click": 1,
    "right_click": 2,
    "double_click": 3,
    "hover": 4,
    "text_input": 5,
    "key_chord": 6,
}


def _s3_object_key_from_public_url(image_url: str) -> Optional[str]:
    """Из публичного URL объекта (как после upload_file) получить S3 key."""
    from urllib.parse import unquote, urlparse

    raw = (image_url or "").strip()
    if not raw:
        return None
    ep = (configs.MINIO_ENDPOINT_URL or "").strip().rstrip("/")
    bn = (configs.MINIO_BUCKET or "").strip()
    if not ep or not bn:
        return None
    prefix = f"{ep}/{bn}/"
    if raw.startswith(prefix):
        return unquote(raw[len(prefix) :])
    try:
        path = unquote(urlparse(raw).path or "")
    except Exception:
        return None
    marker = f"/{bn}/"
    if marker in path:
        return path.split(marker, 1)[1]
    return None


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

    def _validate_scenario_graph(
        self,
        step_ids: set[int],
        start_step_id: Optional[int],
        transitions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        if step_ids and start_step_id not in step_ids:
            errors.append("Выберите стартовый шаг сценария")

        outgoing: Dict[int, List[Dict[str, Any]]] = {step_id: [] for step_id in step_ids}
        incoming: Dict[int, int] = {step_id: 0 for step_id in step_ids}
        route_keys: set[tuple[int, Optional[int], str]] = set()
        for item in transitions:
            source = item.get("source_step_id")
            target = item.get("target_step_id")
            route_key = (source, target, item.get("trigger_type", "success"))
            if route_key in route_keys:
                errors.append("Обнаружены дублирующиеся переходы")
                continue
            route_keys.add(route_key)
            if source not in step_ids:
                errors.append(f"Переход ссылается на неизвестный исходный шаг {source}")
                continue
            if target is not None and target not in step_ids:
                errors.append(f"Переход ссылается на неизвестный целевой шаг {target}")
                continue
            outgoing[source].append(item)
            if target is not None:
                incoming[target] += 1

        if start_step_id in step_ids:
            reachable: set[int] = set()
            stack = [start_step_id]
            while stack:
                current = stack.pop()
                if current in reachable:
                    continue
                reachable.add(current)
                stack.extend(
                    item["target_step_id"]
                    for item in outgoing[current]
                    if item.get("target_step_id") is not None
                )
            unreachable = step_ids - reachable
            if unreachable:
                warnings.append(
                    "Недостижимые шаги: " + ", ".join(map(str, sorted(unreachable)))
                )

        dead_ends = [step_id for step_id, routes in outgoing.items() if not routes]
        if dead_ends:
            warnings.append(
                "Шаги без перехода к завершению: "
                + ", ".join(map(str, sorted(dead_ends)))
            )

        return {
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "nodes_count": len(step_ids),
            "transitions_count": len(transitions),
        }

    async def get_scenario_graph(self, training_uuid: UUID4) -> ScenarioGraphResponse:
        training = await self.repo.get_by_uuid(training_uuid)
        if not training:
            raise HTTPException(status_code=404, detail="Тренинг не найден")
        steps = await self.repo.get_training_steps(training_uuid)
        transitions = await self.repo.get_transitions(training_uuid)
        data = [
            ScenarioTransitionResponse.model_validate(item) for item in transitions
        ]
        validation = self._validate_scenario_graph(
            {step.id for step in steps},
            training.scenario_start_step_id,
            [item.model_dump() for item in data],
        )
        return ScenarioGraphResponse(
            start_step_id=training.scenario_start_step_id,
            transitions=data,
            validation=validation,
        )

    async def update_scenario_graph(
        self, training_uuid: UUID4, graph: ScenarioGraphUpdate, user_id: int
    ) -> ScenarioGraphResponse:
        training = await self._require_training_owner(training_uuid, user_id)
        steps = await self.repo.get_training_steps(training_uuid)
        step_ids = {step.id for step in steps}
        transitions_data = [item.model_dump() for item in graph.transitions]
        validation = self._validate_scenario_graph(
            step_ids, graph.start_step_id, transitions_data
        )
        if not validation["valid"]:
            raise HTTPException(status_code=422, detail=validation)

        training.scenario_start_step_id = graph.start_step_id
        await self.repo.replace_transitions(training_uuid, transitions_data)
        await self.session.commit()
        return await self.get_scenario_graph(training_uuid)

    async def publish_training(
        self, training_uuid: UUID4, requires_auth: bool = False
    ) -> str:
        """
        Публикует тренинг: ставит publish=True, создаёт/обновляет публикацию.
        requires_auth=True — проходить могут только авторизованные пользователи
        (в истории попыток будет видно, кто проходил).
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
            requires_auth=requires_auth,
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

        data = TrainingResponse.model_validate(training).model_dump(mode="json")
        data["requires_auth"] = bool(getattr(publication, "requires_auth", False))
        return data

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
                item.public_link = public_passage_link(active_pub.access_token)
            item.steps_count = len(training.steps) if training.steps else 0
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
        self,
        training_uuid: UUID4,
        photo_urls: List[str],
        detect_ui_elements: bool = True,
    ) -> List[Dict]:
        """
        Создание шагов из фотографий с вычислением размеров.
        Этот метод делегирует сохранение в репозиторий.
        """
        try:
            from utils.pg_sequences import sync_training_steps_id_sequence

            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден",
                )

            await sync_training_steps_id_sequence(self.session)

            steps_data_to_create = []

            existing_steps = await self.repo.get_training_steps(training_uuid)
            next_step_number = len(existing_steps) + 1

            for i, photo_url in enumerate(photo_urls):
                image_bytes = await asyncio.to_thread(
                    self._fetch_image_bytes, photo_url
                )
                image_meta = self._image_dimensions_from_bytes(image_bytes)
                ui_detections = (
                    await self._detect_ui_elements_safe(image_bytes)
                    if detect_ui_elements
                    else []
                )
                sn = next_step_number + i

                steps_data_to_create.append(
                    {
                        "step_number": sn,
                        "image_url": photo_url,
                        "meta": {
                            "name": f"Шаг {sn}",
                            "ui_detections": ui_detections,
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

    def _fetch_image_bytes(self, image_url: str) -> Optional[bytes]:
        """Скачивает картинку по URL и возвращает её байты."""
        try:
            img_response = requests.get(image_url, timeout=15)
            img_response.raise_for_status()
            return img_response.content
        except Exception as e:
            logger.warning(
                "Не удалось загрузить изображение {} анонимно: {}", image_url, e
            )
        # Фолбэк: приватный бакет (MinIO без public policy) — качаем через S3 API
        key = _s3_object_key_from_public_url(image_url)
        if not key:
            return None
        try:
            s3 = S3Service()
            return s3.download_bytes_sync(key)
        except Exception as e2:
            logger.warning("Не удалось получить объект {} из S3: {}", key, e2)
            return None

    def _image_dimensions_from_bytes(
        self, image_bytes: Optional[bytes]
    ) -> Dict[str, int]:
        """Размеры картинки по её байтам."""
        if not image_bytes:
            return {"width": 0, "height": 0}
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return {
                "width": img.width,
                "height": img.height,
            }
        except Exception as e:
            logger.warning("Не удалось получить размеры изображения: {}", e)
            return {"width": 0, "height": 0}

    async def _detect_ui_elements_safe(
        self, image_bytes: Optional[bytes]
    ) -> List[Dict]:
        """YOLO-детекция UI-элементов. Никогда не роняет основной сценарий."""
        if not image_bytes:
            return []
        try:
            from services.ui_detection_service import ui_detection_service

            return await asyncio.to_thread(
                ui_detection_service.detect_elements, image_bytes
            )
        except Exception as e:
            logger.warning("UI-детекция недоступна: {}", e)
            return []

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

            area_patch = update_data.get("area") if "area" in update_data else None
            if isinstance(area_patch, dict):
                existing_area = existing_step.area or {}
                if isinstance(existing_area, dict):
                    merged_area = {**existing_area, **area_patch}
                    # Если клиент прислал area без actions, это явный переход к одиночному шагу.
                    # Иначе старые actions "призраками" остаются в прохождении.
                    if "actions" not in area_patch:
                        merged_area.pop("actions", None)
                    update_data["area"] = merged_area

            final_action_type_id = update_data.get(
                "action_type_id", existing_step.action_type_id
            )

            # keyPress: область только metaKeywords, без координат
            if final_action_type_id == ACTION_TYPE_KEY_PRESS_ID:
                area_src = update_data.get("area") or existing_step.area or {}
                update_data["area"] = {
                    "metaKeywords": (
                        area_src.get("metaKeywords")
                        if isinstance(area_src.get("metaKeywords"), list)
                        else []
                    )
                }
            elif "area" in update_data and update_data["area"] is not None:
                update_data["area"] = _sanitize_area_for_action_type(
                    update_data["area"], final_action_type_id
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
                detail=f"Ошибка обновления шага: {str(e)}",
            )

    async def replace_step_screenshot(
        self,
        training_uuid: UUID4,
        step_id: int,
        creator_id: int,
        file_content: bytes,
        original_filename: str,
        s3_service: S3Service,
    ) -> TrainingStepResponse:
        if len(file_content) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл больше 25 МБ",
            )
        await self._require_training_owner(training_uuid, creator_id)
        existing_step = await self.repo.get_step_by_id_and_training(
            step_id, training_uuid
        )
        if not existing_step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Шаг не найден",
            )
        try:
            im = Image.open(io.BytesIO(file_content))
            im.load()
            w, h = im.size
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось прочитать изображение",
            )

        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
        else:
            im = im.convert("RGB")

        buf = io.BytesIO()
        im.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        object_name = s3_service.generate_unique_filename("step_edit.png")
        image_url = await s3_service.upload_file(png_bytes, object_name, training_uuid)

        # Скриншот изменился — пересчитываем детекции UI-элементов
        ui_detections = await self._detect_ui_elements_safe(png_bytes)

        return await self.update_step(
            training_uuid,
            step_id,
            TrainingStepUpdate(
                image_url=image_url,
                photo_dimensions={"width": w, "height": h},
                meta={"ui_detections": ui_detections},
            ),
        )

    async def detect_step_ui_elements(
        self,
        training_uuid: UUID4,
        step_id: int,
        creator_id: int,
        s3_service: S3Service,
    ) -> TrainingStepResponse:
        """Повторная YOLO-детекция UI-элементов на скриншоте шага."""
        content, _media_type = await self.get_step_screenshot_bytes(
            training_uuid, step_id, creator_id, s3_service
        )
        ui_detections = await self._detect_ui_elements_safe(content)
        return await self.update_step(
            training_uuid,
            step_id,
            TrainingStepUpdate(meta={"ui_detections": ui_detections}),
        )

    async def get_step_screenshot_bytes(
        self,
        training_uuid: UUID4,
        step_id: int,
        creator_id: int,
        s3_service: S3Service,
    ) -> tuple[bytes, str]:
        """Байты скриншота шага из S3 (для редактора без CORS в браузере)."""
        await self._require_training_owner(training_uuid, creator_id)
        step = await self.repo.get_step_by_id_and_training(step_id, training_uuid)
        if not step or not step.image_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="У шага нет изображения",
            )
        key = _s3_object_key_from_public_url(str(step.image_url).strip())
        if not key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL изображения не совпадает с настроенным S3",
            )
        try:
            obj = s3_service.s3_client.get_object(
                Bucket=s3_service.bucket_name, Key=key
            )
        except ClientError as e:
            code = (e.response or {}).get("Error", {}).get("Code", "")
            if code in ("NoSuchKey", "404"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Файл в хранилище не найден",
                ) from e
            logger.exception("S3 get_object для скриншота шага")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Ошибка чтения из хранилища",
            ) from e

        body: bytes = obj["Body"].read()
        if len(body) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл слишком большой",
            )
        ct = obj.get("ContentType") or "image/png"
        if isinstance(ct, str) and ";" in ct:
            ct = ct.split(";")[0].strip()
        if not str(ct).startswith("image/"):
            ct = "image/png"
        return body, ct

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

    async def start_async_video_processing(
        self,
        training_uuid: UUID4,
        user_id: int,
        video_file: UploadFile,
        s3_service: S3Service,
    ):
        """Загружает видео в S3, создаёт задачу и ставит в очередь Celery."""
        from models.tasks import TaskStatus, TaskType
        from repositories.tasks_repository import TasksRepository
        from schemas.tasks import TaskCreateResponse, TaskStatusEnum
        from core.redis_pubsub import publish_task_notification
        from schemas.tasks import TaskNotificationPayload
        await self._require_training_owner(training_uuid, user_id)

        if not video_file.filename:
            raise HTTPException(status_code=400, detail="Имя файла обязательно")

        if video_file.file is None:
            raise HTTPException(status_code=400, detail="Пустой файл")

        import asyncio

        object_key = s3_service.generate_task_object_key(
            user_id, video_file.filename, prefix=f"trainings/{training_uuid}/video"
        )
        content_type = video_file.content_type or "video/mp4"

        # Потоковая загрузка файла в S3 без чтения всего видео в память web-процесса.
        try:
            await asyncio.to_thread(video_file.file.seek, 0)
            file_url = await asyncio.to_thread(
                s3_service.upload_fileobj_sync, video_file.file, object_key, content_type
            )
        finally:
            await video_file.close()

        tasks_repo = TasksRepository(self.session)
        task = await tasks_repo.create(
            user_id=user_id,
            file_url=file_url,
            task_type=TaskType.VIDEO_PROCESSING.value,
            status=TaskStatus.PENDING.value,
            progress=0,
            original_filename=video_file.filename,
            training_uuid=training_uuid,
        )

        # Ставим задачу в очередь без импорта worker-модулей в web-процесс.
        from core.task_queue import enqueue_process_training_video

        await asyncio.to_thread(enqueue_process_training_video, str(task.id))

        await asyncio.to_thread(
            publish_task_notification,
            user_id,
            TaskNotificationPayload(
                type="task_update",
                task_id=str(task.id),
                status=TaskStatus.PENDING.value,
                progress=0,
                message="Видео принято в обработку. Можно продолжать работу — шаги появятся автоматически.",
                training_uuid=str(training_uuid),
                task_type=TaskType.VIDEO_PROCESSING.value,
            ),
        )

        return TaskCreateResponse(
            task_id=task.id,
            status=TaskStatusEnum.PENDING,
            message="Видео принято в обработку",
            training_uuid=training_uuid,
        )

    async def add_steps_from_video(
        self,
        training_uuid: UUID4,
        video_file: UploadFile,
        video_ai_service: VideoAIService,
        s3_service: S3Service,
        creator_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Синхронная обработка (legacy). Предпочтительно start_async_video_processing.
        """
        try:
            if creator_id is not None:
                await self._require_training_owner(training_uuid, creator_id)
            else:
                training_exists = await self.repo.check_training_exists(training_uuid)
                if not training_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Тренинг с UUID {training_uuid} не найден",
                    )

            ai_steps = await video_ai_service.analyze_video(video_file)
            return await self.create_steps_from_ai_steps(
                training_uuid=training_uuid,
                ai_steps=ai_steps,
                s3_service=s3_service,
                creator_id=creator_id,
            )
        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.exception("Ошибка AI-анализа видео и создания шагов")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка AI-анализа видео и создания шагов: {str(e)}",
            )

    @staticmethod
    def _iou(a: Dict[str, float], b: Dict[str, float]) -> float:
        ax1, ay1 = a["x"], a["y"]
        ax2, ay2 = ax1 + a["width"], ay1 + a["height"]
        bx1, by1 = b["x"], b["y"]
        bx2, by2 = bx1 + b["width"], by1 + b["height"]
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
        inter = iw * ih
        if inter <= 0:
            return 0.0
        union = a["width"] * a["height"] + b["width"] * b["height"] - inter
        return inter / union if union > 0 else 0.0

    def _resolve_ai_bbox_area(
        self,
        bbox: List[float],
        fw: float,
        fh: float,
        ui_detections: List[Dict],
    ) -> Dict[str, Any]:
        """
        Превращает bbox модели в пиксельную область скриншота.

        Модель может вернуть координаты в неизвестной шкале (0..1, 0..1000,
        абсолютные пиксели её внутреннего кадра). Поэтому строим кандидатов
        и выбираем интерпретацию, которая лучше всего совпадает (IoU) с
        YOLO-детекциями — они гарантированно в пикселях скриншота.
        Без детекций — абсолютные пиксели (так просит промт).
        """
        b0, b1, b2, b3 = [float(v) for v in bbox]

        def norm_area(x1, y1, x2, y2) -> Dict[str, float]:
            return {
                "x": max(0.0, min(fw, min(x1, x2))),
                "y": max(0.0, min(fh, min(y1, y2))),
                "width": max(1.0, min(fw, abs(x2 - x1))),
                "height": max(1.0, min(fh, abs(y2 - y1))),
            }

        def px(x1, y1, x2, y2) -> Dict[str, float]:
            xa, xb = min(x1, x2), max(x1, x2)
            ya, yb = min(y1, y2), max(y1, y2)
            return {
                "x": max(0.0, min(fw, xa)),
                "y": max(0.0, min(fh, ya)),
                "width": max(1.0, min(fw, xb) - max(0.0, min(fw, xa))),
                "height": max(1.0, min(fh, yb) - max(0.0, min(fh, ya))),
            }

        candidates: List[Dict[str, float]] = []
        if max(b0, b1, b2, b3) <= 1.0:
            candidates.append(norm_area(b0 * fw, b1 * fh, b2 * fw, b3 * fh))
        candidates.append(px(b0, b1, b2, b3))
        # Шкала 0..1000 (тысячные доли) — частый формат VLM
        candidates.append(norm_area(b0 / 1000 * fw, b1 / 1000 * fh, b2 / 1000 * fw, b3 / 1000 * fh))

        best = None
        best_score = -1.0
        best_det = None
        detections = [d for d in ui_detections if d.get("width") and d.get("height")]
        if not detections:
            best = candidates[0]
        for cand in candidates:
            for d in detections:
                score = self._iou(cand, d)
                if score > best_score:
                    best_score = score
                    best = cand
                    best_det = d

        if detections and best_score >= 0.4 and best_det is not None:
            # Хорошее совпадение — привязываем область к реальному элементу
            best = {
                "x": float(best_det["x"]),
                "y": float(best_det["y"]),
                "width": float(best_det["width"]),
                "height": float(best_det["height"]),
            }
            logger.info(
                "AI bbox {} привязан к элементу '{}' ({}) IoU {:.2f}",
                bbox,
                best_det.get("class_ru") or best_det.get("class_name"),
                {k: round(v, 1) for k, v in best.items()},
                best_score,
            )
        elif detections and best_score < 0.15:
            # Ни одна интерпретация не совпала с реальными элементами — берём пиксели
            best = px(b0, b1, b2, b3)
            logger.warning(
                "AI bbox {} не совпал ни с одной YOLO-детекцией (best IoU {:.2f}), "
                "используются пиксели как есть",
                bbox,
                best_score,
            )
        elif detections:
            logger.info(
                "AI bbox {} -> область {} (IoU {:.2f})",
                bbox,
                {k: round(v, 1) for k, v in best.items()},
                best_score,
            )
        return best

    async def create_steps_from_ai_steps(
        self,
        training_uuid: UUID4,
        ai_steps: list,
        s3_service: S3Service,
        creator_id: Optional[int] = None,
    ) -> List[Dict]:
        """Создаёт шаги тренинга из результата AI-анализа видео."""
        import asyncio

        if creator_id is not None:
            await self._require_training_owner(training_uuid, creator_id)
        elif not await self.repo.check_training_exists(training_uuid):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Тренинг с UUID {training_uuid} не найден",
            )

        if not ai_steps:
            return []

        from utils.pg_sequences import sync_training_steps_id_sequence

        await sync_training_steps_id_sequence(self.session)

        try:
            DEFAULT_ACTION_TYPE_ID = 1

            existing_steps = await self.repo.get_training_steps(training_uuid)
            next_step_number = len(existing_steps) + 1

            created_steps_info = []

            for i, step_data in enumerate(ai_steps):
                filename = f"video_ai_step_{i + 1:03d}.png"
                object_name = s3_service.generate_unique_filename(filename)

                # Загружаем в S3 в отдельном потоке
                image_url = await asyncio.to_thread(
                    s3_service.upload_bytes_sync,
                    step_data.frame_bytes,
                    object_name,
                    "image/png",
                )
                image_url = (
                    f"{s3_service.endpoint_url}/{s3_service.bucket_name}/{object_name}"
                )

                image_url_after: Optional[str] = None
                if step_data.after_frame_bytes:
                    after_name = s3_service.generate_unique_filename(
                        f"video_ai_step_{i + 1:03d}_after.png"
                    )
                    await asyncio.to_thread(
                        s3_service.upload_bytes_sync,
                        step_data.after_frame_bytes,
                        after_name,
                        "image/png",
                    )
                    image_url_after = f"{s3_service.endpoint_url}/{s3_service.bucket_name}/{after_name}"

                bbox = step_data.bbox
                fw = float(step_data.frame_width or 1)
                fh = float(step_data.frame_height or 1)

                # YOLO-детекции на этом же кадре — эталон в пикселях скриншота.
                ui_detections = await self._detect_ui_elements_safe(
                    step_data.frame_bytes
                )

                area = self._resolve_ai_bbox_area(bbox, fw, fh, ui_detections)

                # Жёсткая защита от аномалий размера (слишком крупная/слишком мелкая область)
                max_w = fw * 0.7
                max_h = fh * 0.7
                area["width"] = max(1.0, min(float(area["width"]), max_w))
                area["height"] = max(1.0, min(float(area["height"]), max_h))

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
                    "ui_detections": ui_detections,
                    "ai_timecode": step_data.timecode,
                    "ai_timecode_before": step_data.timecode_before
                    or step_data.timecode,
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
        except IntegrityError as exc:
            await self.session.rollback()
            err = str(getattr(exc, "orig", exc))
            if "training_steps_pkey" in err or "UniqueViolation" in err:
                await sync_training_steps_id_sequence(self.session)
                await self.session.commit()
                logger.error(
                    "Конфликт id training_steps после синхронизации sequence: {}",
                    err,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=(
                        "Ошибка создания шагов: конфликт идентификаторов в базе данных. "
                        "Обновите backend (alembic upgrade head) и повторите загрузку видео."
                    ),
                )
            raise
        except Exception as e:
            await self.session.rollback()
            logger.exception("Ошибка создания шагов из AI-анализа")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка создания шагов: {str(e)}",
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

    async def start_public_passage_attempt(
        self, access_token: str, user: Optional[User] = None
    ) -> dict:
        publication = await self.repo.get_publication_by_token(access_token)
        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренинг не найден или доступ закрыт",
            )
        if getattr(publication, "requires_auth", False) and user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Для прохождения этого тренинга нужно войти в аккаунт",
            )
        att = await self.repo.create_passage_attempt(
            publication.id, user_id=user.id if user else None
        )
        await self.session.commit()
        return {"attempt_id": att.id}

    async def complete_public_passage_attempt(
        self,
        access_token: str,
        body: PassageCompleteRequest,
        user: Optional[User] = None,
    ) -> dict:
        publication = await self.repo.get_publication_by_token(access_token)
        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренинг не найден или доступ закрыт",
            )
        if getattr(publication, "requires_auth", False) and user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Для прохождения этого тренинга нужно войти в аккаунт",
            )
        ok = await self.repo.complete_passage_attempt(
            body.attempt_id,
            publication.id,
            body.is_completed,
            body.duration_seconds,
            body.wrong_attempts_total,
            user_id=user.id if user else None,
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
        items = []
        for r in rows:
            u = getattr(r, "user", None)
            name = (
                f"{u.first_name or ''} {u.last_name or ''}".strip() if u else ""
            ) or None
            items.append(
                PassageHistoryItemResponse(
                    started_at=r.started_at,
                    finished_at=r.finished_at,
                    is_completed=r.is_completed,
                    duration_seconds=r.duration_seconds,
                    wrong_attempts_total=r.wrong_attempts_total,
                    user_email=u.email if u else None,
                    user_name=name,
                )
            )
        return items

    async def add_steps_from_pdf(
        self,
        training_uuid: UUID4,
        pdf_bytes: bytes,
        pdf_ai_service: PdfAiService,
        s3_service: S3Service,
    ) -> List[Dict]:
        """
        Обрабатывает PDF-инструкцию через VLM-модель:
        1. Каждая страница рендерится в PNG
        2. VLM определяет кликабельную область по тексту страницы
        3. PNG загружается в S3
        4. Создаётся шаг тренинга с областью, описанием и скрином
        """
        try:
            training_exists = await self.repo.check_training_exists(training_uuid)
            if not training_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Тренинг с UUID {training_uuid} не найден",
                )

            # Анализируем PDF через VLM
            pdf_steps = await pdf_ai_service.analyze_pdf(pdf_bytes)

            if not pdf_steps:
                return []

            DEFAULT_ACTION_TYPE_ID = 1

            existing_steps = await self.repo.get_training_steps(training_uuid)
            next_step_number = len(existing_steps) + 1

            created_steps_info = []

            # Параллельная загрузка PNG страниц в S3
            import asyncio
            async def _upload_step_image(idx, data):
                filename = f"pdf_step_{data.page_number:03d}.png"
                object_name = s3_service.generate_unique_filename(filename)
                url = await s3_service.upload_file(data.page_bytes, object_name, training_uuid)
                return idx, url

            upload_tasks = [_upload_step_image(i, step) for i, step in enumerate(pdf_steps)]
            upload_results = await asyncio.gather(*upload_tasks)
            upload_results.sort(key=lambda x: x[0])
            image_urls = [res[1] for res in upload_results]

            for i, step_data in enumerate(pdf_steps):
                image_url = image_urls[i]

                bbox = step_data.bbox
                # bbox уже нормализован 0..1 в PdfAiService
                x1, y1, x2, y2 = bbox
                x_min, x_max = min(x1, x2), max(x1, x2)
                y_min, y_max = min(y1, y2), max(y1, y2)
                area: Dict[str, Any] = {
                    "x": x_min * step_data.page_width,
                    "y": y_min * step_data.page_height,
                    "width": max(1.0, (x_max - x_min) * step_data.page_width),
                    "height": max(1.0, (y_max - y_min) * step_data.page_height),
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
                    "source": "pdf_ai",
                    "pdf_page": step_data.page_number,
                }

                new_step = TrainingStep(
                    step_number=next_step_number + i,
                    meta=step_meta,
                    training_uuid=training_uuid,
                    image_url=image_url,
                    photo_dimensions={
                        "width": step_data.page_width,
                        "height": step_data.page_height,
                    },
                    area=area,
                    action_type_id=action_type_id,
                    annotation=step_data.instruction_md,
                )
                self.session.add(new_step)

                created_steps_info.append(
                    {
                        "step_number": next_step_number + i,
                        "pdf_page": step_data.page_number,
                        "image_url": image_url,
                        "name": step_data.step_title,
                        "area": area,
                        "action_type_id": action_type_id,
                        "action_type_key": action_key,
                        "dimensions": {
                            "width": step_data.page_width,
                            "height": step_data.page_height,
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
                detail=f"Ошибка AI-анализа PDF и создания шагов: {str(e)}",
            )
