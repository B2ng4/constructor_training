# routing/base_router.py
from typing import Generic, TypeVar, Type, List, Callable, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from models.users import User

# Generic типы
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType")


class BaseRouter(
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ResponseSchemaType,
        RepositoryType,
    ]
):
    """Базовый класс для создания CRUD роутеров"""

    def __init__(
        self,
        repository_dependency: Callable,
        auth_dependency: Callable,
        prefix: str,
        tags: List[str],
        response_schema: Type[ResponseSchemaType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        entity_name: str = "Запись",
        entity_name_plural: str = "Записи",
        pk_name: str = "id",
        pk_description: str = "ID записи",
    ):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.repository_dependency = repository_dependency
        self.auth_dependency = auth_dependency
        self.response_schema = response_schema
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.entity_name = entity_name
        self.entity_name_plural = entity_name_plural
        self.pk_name = pk_name
        self.pk_description = pk_description
        self._register_routes()

    def _register_routes(self):
        """Регистрация базовых CRUD маршрутов"""

        @self.router.post(
            "/",
            response_model=self.response_schema,
            status_code=status.HTTP_201_CREATED,
            summary=f"Создание {self.entity_name.lower()}",
            description=f"Создать новый объект {self.entity_name.lower()}",
        )
        async def create(
            data: self.create_schema = Body(...),
            repo=Depends(self.repository_dependency),
            current_user: User = Depends(self.auth_dependency),
        ):
            """Создание новой записи"""
            return await self._create(data, repo, current_user)

        # GET ALL
        @self.router.get(
            "/",
            response_model=List[self.response_schema],
            summary=f"Получение всех {self.entity_name_plural.lower()}",
            description=f"Получить список всех {self.entity_name_plural.lower()} с пагинацией",
        )
        async def get_all(
            skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
            limit: int = Query(
                100, ge=1, le=500, description="Максимальное количество записей"
            ),
            repo=Depends(self.repository_dependency),
        ):
            """Получение списка записей с пагинацией"""
            return await self._get_all(skip, limit, repo)

        # GET BY ID
        @self.router.get(
            f"/{{{self.pk_name}}}",
            response_model=self.response_schema,
            summary=f"Получение {self.entity_name.lower()} по {self.pk_name}",
            description=f"Получить {self.entity_name.lower()} по его {self.pk_description.lower()}",
        )
        async def get_by_id(
            value: int = Path(..., description=self.pk_description, alias=self.pk_name),
            repo=Depends(self.repository_dependency),
        ):
            """Получение записи по ID"""
            return await self._get_by_id(value, repo)

        @self.router.patch(
            f"/{{{self.pk_name}}}",
            response_model=self.response_schema,
            summary=f"Обновление {self.entity_name.lower()}",
            description=f"Обновить существующий {self.entity_name.lower()}",
        )
        async def update(
            value: int = Path(..., description=self.pk_description, alias=self.pk_name),
            data: self.update_schema = Body(...),
            repo=Depends(self.repository_dependency),
            current_user: User = Depends(self.auth_dependency),
        ):
            """Обновление записи"""
            return await self._update(value, data, repo, current_user)

        # DELETE
        @self.router.delete(
            f"/{{{self.pk_name}}}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary=f"Удаление {self.entity_name.lower()}",
            description=f"Удалить {self.entity_name.lower()} из системы",
        )
        async def delete(
            value: int = Path(..., description=self.pk_description, alias=self.pk_name),
            repo=Depends(self.repository_dependency),
            current_user: User = Depends(self.auth_dependency),
        ):
            """Удаление записи"""
            return await self._delete(value, repo, current_user)

    # CRUD методы
    async def _create(self, data: Any, repo: Any, current_user: User) -> Any:
        """Логика создания записи"""
        await self._before_create(data, repo, current_user)
        try:
            instance = await repo.create(**data.model_dump())
            result = self.response_schema.model_validate(instance)
            await self._after_create(result, repo, current_user)
            return result
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ошибка при создании {self.entity_name.lower()}: возможно, запись уже существует",
            )

    async def _get_all(self, skip: int, limit: int, repo: Any) -> List[Any]:
        """Логика получения всех записей"""
        instances = await repo.get_all(
            skip=skip, limit=limit, order_by=self._get_order_by()
        )
        return [self.response_schema.model_validate(instance) for instance in instances]

    async def _get_by_id(self, id: int, repo: Any) -> Any:
        """Логика получения записи по ID"""
        instance = await repo.get_by_id(id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.entity_name} с {self.pk_name} {id} не найден",
            )
        return self.response_schema.model_validate(instance)

    async def _update(self, id: int, data: Any, repo: Any, current_user: User) -> Any:
        """Логика обновления записи"""
        if not await repo.exists(id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.entity_name} с {self.pk_name} {id} не найден",
            )
        await self._before_update(id, data, repo, current_user)
        try:
            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не указаны данные для обновления",
                )
            updated = await repo.update(id, **update_data)
            result = self.response_schema.model_validate(updated)
            await self._after_update(result, repo, current_user)
            return result
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ошибка при обновлении {self.entity_name.lower()}",
            )

    async def _delete(self, id: int, repo: Any, current_user: User) -> None:
        """Логика удаления записи"""
        if not await repo.exists(id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.entity_name} с {self.pk_name} {id} не найден",
            )
        await self._before_delete(id, repo, current_user)
        success = await repo.delete(id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при удалении {self.entity_name.lower()}",
            )
        await self._after_delete(id, repo, current_user)

    # Хуки
    async def _before_create(self, data: Any, repo: Any, user: User):
        pass

    async def _after_create(self, result: Any, repo: Any, user: User):
        pass

    async def _before_update(self, id: int, data: Any, repo: Any, user: User):
        pass

    async def _after_update(self, result: Any, repo: Any, user: User):
        pass

    async def _before_delete(self, id: int, repo: Any, user: User):
        pass

    async def _after_delete(self, id: int, repo: Any, user: User):
        pass

    def _get_order_by(self) -> Optional[str]:
        return None

    def add_custom_route(self, path: str, methods: List[str], **kwargs):
        return self.router.api_route(path, methods=methods, **kwargs)
