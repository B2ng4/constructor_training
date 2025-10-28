# routing/levels_router.py
from backend.routing.base_router import BaseRouter
from backend.depends import get_current_user, get_actions_repository
from backend.models.trainings import TypesAction

from backend.repositories.actions_repository import ActionsRepository
from backend.schemas.actions import ActionResponse, ActionCreate, ActionUpdate


class ActionsRouter(BaseRouter[TypesAction, ActionCreate, ActionUpdate, ActionResponse, ActionsRepository]):
    """Роутер для управления действиями"""

    def __init__(self):
        super().__init__(
            repository_dependency=get_actions_repository,
            auth_dependency=get_current_user,
            prefix="/actions",
            tags=["Действия"],
            response_schema=ActionResponse,
            create_schema=ActionCreate,
            update_schema=ActionUpdate,
            entity_name="Действие",
            entity_name_plural="Действия",
            pk_name="value",
            pk_description="ID действия (value)"
        )

    def _get_order_by(self) -> str:
        return "value"


Actions_router_instance = ActionsRouter()
router = Actions_router_instance.router
