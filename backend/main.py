"""
Точка входа в backend
"""

from fastapi import FastAPI, APIRouter
from routing import (
    tags_router,
    levels_router,
    actions_router,
    auth_router,
    training_router,
)
from core.config import configs
from core.create_base_app import create_base_app

app = create_base_app(configs)

app.include_router(auth_router.router)
app.include_router(training_router.router)
app.include_router(tags_router.router)
app.include_router(levels_router.router)
app.include_router(actions_router.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=configs.HOST, port=configs.PORT, reload=True)
