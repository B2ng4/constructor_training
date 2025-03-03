# Переменные для удобства
PYTHON = python3
PIP = pip3
DOCKER = docker
DOCKER_COMPOSE = docker-compose
PORT = 8001


.PHONY: dev
 dev:
	$(DOCKER_COMPOSE) build ; $(DOCKER_COMPOSE) up -d

 stop:
	$(DOCKER_COMPOSE) down