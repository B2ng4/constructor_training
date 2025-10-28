# routing/levels_router.py
from backend.routing.base_router import BaseRouter
from backend.repositories.levels_repository import LevelsRepository
from backend.depends import get_levels_repository, get_current_user
from backend.models.trainings import Levels
from backend.schemas.levels import LevelResponse, LevelCreate, LevelUpdate


class LevelsRouter(BaseRouter[Levels, LevelCreate, LevelUpdate, LevelResponse, LevelsRepository]):
    """Роутер для управления уровнями сложности"""

    def __init__(self):
        super().__init__(
            repository_dependency=get_levels_repository,
            auth_dependency=get_current_user,
            prefix="/levels",
            tags=["Уровни"],
            response_schema=LevelResponse,
            create_schema=LevelCreate,
            update_schema=LevelUpdate,
            entity_name="Уровень",
            entity_name_plural="Уровни",
            pk_name="value",
            pk_description="ID уровня (value)"
        )

    def _get_order_by(self) -> str:
        return "value"


levels_router_instance = LevelsRouter()
router = levels_router_instance.router
