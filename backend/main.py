"""
Точка входа в backend
"""
#


from fastapi import FastAPI, APIRouter
from routing import books_router
from routing import auth_router
from core.config import configs
from core.create_base_app import create_base_app



app = create_base_app(configs)
app.include_router(auth_router.router)
app.include_router(books_router.router)

#feec3ca171c7

# docker run -p 8001:8001 feec3ca171c7

