from typing import Any, Dict, List, Optional

from pydantic import UUID4
from sqlalchemy import and_, case, delete, exists, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from models.trainings import (
    Training,
    TrainingPassageAttempt,
    TrainingPublication,
    TrainingStep,
    TypesAction,
)


class TrainingRepository:
    """
    Репозиторий тренингов
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _get_eager_load_options(self):
        """
        Правильная рекурсивная загрузка вложенных steps
        Нельзя цеплять разные relationship друг за другом!
        """
        from sqlalchemy.orm import selectinload

        steps_with_action = selectinload(Training.steps).selectinload(
            TrainingStep.action_type
        )

        nested_steps = (
            selectinload(Training.steps)
            .selectinload(TrainingStep.steps)
            .selectinload(TrainingStep.action_type)
        )

        nested_steps2 = (
            selectinload(Training.steps)
            .selectinload(TrainingStep.steps)
            .selectinload(TrainingStep.steps)
            .selectinload(TrainingStep.action_type)
        )

        return [
            selectinload(Training.tags),
            selectinload(Training.level),
            steps_with_action,
            nested_steps,
            nested_steps2,
        ]

    def _get_step_eager_load_options(self, depth: int = 3):
        """
        Рекурсивная загрузка вложенных подшагов
        """

        step_loader = selectinload(TrainingStep.action_type)

        current = selectinload(TrainingStep.steps).selectinload(
            TrainingStep.action_type
        )
        for _ in range(depth - 1):
            current = current.selectinload(TrainingStep.steps).selectinload(
                TrainingStep.action_type
            )

        return [step_loader, current]

    async def create(self, training: Training) -> Training:
        """Создание тренинга"""
        self.session.add(training)
        await self.session.flush()
        await self.session.refresh(training)
        return training

    async def get_by_uuid(self, training_uuid: UUID4) -> Optional[Training]:
        """Получение тренинга по uuid БЕЗ relationships (базовый метод)"""
        query = select(Training).where(Training.uuid == training_uuid)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_uuid_with_relations(
        self, training_uuid: UUID4
    ) -> Optional[Training]:
        """Получение тренинга по uuid СО ВСЕМИ relationships"""
        query = (
            select(Training)
            .options(*self._get_eager_load_options())
            .where(Training.uuid == training_uuid)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> List[Training]:
        """Получение всех тренингов пользователя БЕЗ relationships"""
        query = select(Training).where(Training.creator_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_user_id_with_relations(self, user_id: int) -> List[Training]:
        """Получение всех тренингов пользователя СО ВСЕМИ relationships"""
        query = (
            select(Training)
            .options(*self._get_eager_load_options())
            .where(Training.creator_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Training]:
        """Получение тренингов по фильтрам БЕЗ relationships"""
        query = select(Training).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_with_relations(
        self, skip: int = 0, limit: int = 100
    ) -> List[Training]:
        """Получение тренингов по фильтрам СО ВСЕМИ relationships"""
        query = (
            select(Training)
            .options(*self._get_eager_load_options())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def patch_training_fields(
        self, training_uuid: UUID4, update_data: Dict
    ) -> bool:
        """Частичное обновление полей тренинга"""
        if not update_data:
            return False

        query = (
            update(Training).where(Training.uuid == training_uuid).values(**update_data)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def create_training_step(self, step: TrainingStep) -> TrainingStep:
        """Создание шага тренинга БЕЗ загрузки relationships"""
        self.session.add(step)
        await self.session.flush()

        query = (
            select(TrainingStep)
            .options(selectinload(TrainingStep.action_type))
            .where(TrainingStep.id == step.id)
        )
        result = await self.session.execute(query)
        return result.scalars().unique().one()

    def _get_step_eager_load_options(self, depth: int = 3):
        """
        БЕЗ selectinload для steps - только action_type
        """
        return [selectinload(TrainingStep.action_type)]

    def _get_eager_load_options(self):
        """
        Упрощенная версия - загружаем только действия, БЕЗ вложенных steps
        """
        return [
            selectinload(Training.tags),
            selectinload(Training.level),
            selectinload(Training.steps).selectinload(TrainingStep.action_type),
        ]

    async def get_training_steps(self, training_uuid: UUID4) -> List[TrainingStep]:
        """Получение всех корневых шагов тренинга с вложенными подшагами"""
        query = (
            select(TrainingStep)
            .options(*self._get_step_eager_load_options(depth=5))
            .where(TrainingStep.training_uuid == training_uuid)
            .where(TrainingStep.parent_step_id.is_(None))  # Только корневые шаги
            .order_by(TrainingStep.step_number)
        )

        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def update_training_step(self, step_id: int, update_data: Dict) -> bool:
        """Обновить шаг тренинга по id шага"""
        if not update_data:
            return False

        query = (
            update(TrainingStep).where(TrainingStep.id == step_id).values(**update_data)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def delete_training_step(self, step_id: int) -> bool:
        """Удалить шаг тренинга по id шага"""
        query = delete(TrainingStep).where(TrainingStep.id == step_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0

    async def delete(self, training_uuid: UUID4) -> bool:
        """Удаление тренинга"""
        query = delete(Training).where(Training.uuid == training_uuid)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_action_type(self, action_type_id: int) -> Optional[TypesAction]:
        """Получение типа шага тренинга по его id"""
        return await self.session.get(TypesAction, action_type_id)

    async def create_steps_from_photos(
        self, training_uuid: UUID4, photo_urls: List[str]
    ) -> List[Dict]:
        """Создание шагов тренинга из фотографий (скриншотов)"""

        existing_steps = await self.get_training_steps(training_uuid)
        next_step_number = len(existing_steps) + 1

        created_steps_info = []

        for i, photo_url in enumerate(photo_urls):
            step_number = next_step_number + i

            new_step = TrainingStep(
                step_number=step_number,
                meta={"name": f"Шаг {step_number}"},
                training_uuid=training_uuid,
                image_url=photo_url,
            )

            self.session.add(new_step)
            created_steps_info.append(
                {"step_number": step_number, "image_url": photo_url}
            )
        await self.session.flush()
        await self.session.commit()

        return created_steps_info

    async def check_training_exists(self, training_uuid: UUID4) -> bool:
        """Проверка существования тренинга по uuid"""
        query = select(exists().where(Training.uuid == training_uuid))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_step_by_id(self, step_id: int) -> Optional[TrainingStep]:
        """Получение шага по ID с загрузкой relationships"""
        query = (
            select(TrainingStep)
            .options(*self._get_step_eager_load_options(depth=3))
            .where(TrainingStep.id == step_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_step_by_id_and_training(
        self, step_id: int, training_uuid: UUID4
    ) -> Optional[TrainingStep]:
        """Получение шага по ID с проверкой принадлежности к тренингу"""
        query = (
            select(TrainingStep)
            .where(
                TrainingStep.id == step_id, TrainingStep.training_uuid == training_uuid
            )
            .options(selectinload(TrainingStep.action_type))
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_steps_in_training(
        self, training_uuid: UUID4, step_ids: List[int]
    ) -> int:
        """Подсчет количества шагов из списка, принадлежащих тренингу."""
        if not step_ids:
            return 0
        query = select(func.count(TrainingStep.id)).where(
            TrainingStep.training_uuid == training_uuid, TrainingStep.id.in_(step_ids)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def bulk_update_step_numbers(self, steps_data: List[Dict[str, Any]]) -> int:
        """
        Массовое обновление step_number для списка шагов.
        """
        if not steps_data:
            return 0

        await self.session.execute(update(TrainingStep), steps_data)
        await self.session.flush()
        return len(steps_data)

    async def create_or_update_publication(
        self, training_uuid: UUID4, access_token: str, snapshot_data: Dict
    ) -> TrainingPublication:
        """
        Создает новую публикацию или обновляет существующую для данного тренинга.
        При обновлении задаётся новый access_token и is_active=True (повторная публикация после снятия).
        """
        query = select(TrainingPublication).where(
            TrainingPublication.training_uuid == training_uuid
        )
        result = await self.session.execute(query)
        publication = result.scalar_one_or_none()

        if publication:
            publication.access_token = access_token
            publication.data_snapshot = snapshot_data
            publication.is_active = True
        else:
            publication = TrainingPublication(
                training_uuid=training_uuid,
                access_token=access_token,
                data_snapshot=snapshot_data,
            )
            self.session.add(publication)

        await self.session.flush()
        return publication

    async def get_publication_by_token(
        self, access_token: str
    ) -> Optional[TrainingPublication]:
        """
        Получает публикацию по токену. Это очень быстрый запрос.
        """
        query = select(TrainingPublication).where(
            TrainingPublication.access_token == access_token,
            TrainingPublication.is_active == True,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def deactivate_publication(self, training_uuid: UUID4) -> bool:
        """
        Деактивирует все активные публикации тренинга.
        Возвращает True, если хотя бы одна публикация была деактивирована.
        """
        query = select(TrainingPublication).where(
            TrainingPublication.training_uuid == training_uuid,
            TrainingPublication.is_active == True,
        )
        result = await self.session.execute(query)
        publications = result.scalars().all()

        if not publications:
            return False

        for pub in publications:
            pub.is_active = False

        await self.session.flush()
        return True

    async def increment_publication_views(self, publication_id: int):
        """
        Атомарно увеличивает счетчик просмотров
        """
        stmt = (
            update(TrainingPublication)
            .where(TrainingPublication.id == publication_id)
            .values(views_count=TrainingPublication.views_count + 1)
        )
        await self.session.execute(stmt)

    async def create_passage_attempt(
        self, publication_id: int
    ) -> TrainingPassageAttempt:
        att = TrainingPassageAttempt(publication_id=publication_id)
        self.session.add(att)
        await self.session.flush()
        await self.session.refresh(att)
        return att

    async def complete_passage_attempt(
        self,
        attempt_id: int,
        publication_id: int,
        is_completed: bool,
        duration_seconds: Optional[int],
        wrong_attempts_total: Optional[int],
    ) -> bool:
        stmt = (
            update(TrainingPassageAttempt)
            .where(
                TrainingPassageAttempt.id == attempt_id,
                TrainingPassageAttempt.publication_id == publication_id,
                TrainingPassageAttempt.finished_at.is_(None),
            )
            .values(
                finished_at=func.now(),
                is_completed=is_completed,
                duration_seconds=duration_seconds,
                wrong_attempts_total=wrong_attempts_total,
            )
        )
        res = await self.session.execute(stmt)
        return res.rowcount > 0

    async def get_passage_stats_for_training(
        self, training_uuid: UUID4
    ) -> Dict[str, Any]:
        total_starts = func.count(TrainingPassageAttempt.id)
        total_completions = func.coalesce(
            func.sum(case((TrainingPassageAttempt.is_completed.is_(True), 1), else_=0)),
            0,
        )
        avg_duration = func.avg(
            case(
                (
                    and_(
                        TrainingPassageAttempt.is_completed.is_(True),
                        TrainingPassageAttempt.duration_seconds.isnot(None),
                    ),
                    TrainingPassageAttempt.duration_seconds,
                ),
                else_=None,
            )
        )
        q = (
            select(total_starts, total_completions, avg_duration)
            .select_from(TrainingPassageAttempt)
            .join(
                TrainingPublication,
                TrainingPublication.id == TrainingPassageAttempt.publication_id,
            )
            .where(TrainingPublication.training_uuid == training_uuid)
        )
        result = await self.session.execute(q)
        row = result.one()
        starts = int(row[0] or 0)
        completions = int(row[1] or 0)
        avg_d = row[2]
        return {
            "total_starts": starts,
            "total_completions": completions,
            "avg_duration_seconds": float(avg_d) if avg_d is not None else None,
            "completion_rate": (completions / starts) if starts else 0.0,
        }

    async def list_passage_attempts_for_training(
        self, training_uuid: UUID4, skip: int = 0, limit: int = 20
    ) -> List[TrainingPassageAttempt]:
        q = (
            select(TrainingPassageAttempt)
            .join(
                TrainingPublication,
                TrainingPublication.id == TrainingPassageAttempt.publication_id,
            )
            .where(TrainingPublication.training_uuid == training_uuid)
            .order_by(TrainingPassageAttempt.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(q)
        return list(result.scalars().all())
