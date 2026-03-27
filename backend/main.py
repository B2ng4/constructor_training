"""
Точка входа в backend
"""

from core.config import configs
from core.create_base_app import create_base_app
from core.logging_config import setup_logging
from routing import (
    actions_router,
    auth_router,
    course_router,
    levels_router,
    tags_router,
    training_router,
)

setup_logging(level=configs.LOG_LEVEL)

app = create_base_app(configs)

app.include_router(auth_router.router)
app.include_router(training_router.router)
app.include_router(course_router.router)
app.include_router(tags_router.router)
app.include_router(levels_router.router)
app.include_router(actions_router.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=configs.HOST, port=configs.PORT, reload=True)
