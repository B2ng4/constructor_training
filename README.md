# Конструктор Тренингов


## Содержание 
1. [Про проект](#About)
2. [Как запустить проект?](#Start)
3. [Backend](#Backend)
4. [Frontend](#Frontend)


## About

## Start

### Для настройки frontend


### Для настройки backend

cd backend
uv sync
alembic revision --autogenerate -m "Add training_publications table"
uv run alembic upgrade head 
uv run main.py         


## Backend 
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)


## Frontend

vue
vite
vue-router
quasar
prettier
eslint
