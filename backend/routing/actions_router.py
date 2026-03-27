# routing/levels_router.py
from depends import get_actions_repository, get_current_user
from models.trainings import TypesAction
from repositories.actions_repository import ActionsRepository
from routing.base_router import BaseRouter
from schemas.actions import ActionCreate, ActionResponse, ActionUpdate


class ActionsRouter(
    BaseRouter[
        TypesAction, ActionCreate, ActionUpdate, ActionResponse, ActionsRepository
    ]
):
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
            pk_name="id",
        )

    def _get_order_by(self) -> str:
        return "id"


Actions_router_instance = ActionsRouter()
router = Actions_router_instance.router
