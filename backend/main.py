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



if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8001)
    # uvicorn.run("main:app", host="localhost", port=8000, reload=True)
