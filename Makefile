.PHONY: sync deps build up up-d down stop restart ps exec pull migrate loaddata superuser

deps:
	.venv/bin/python -m pip install -e .

sync: deps up-d

build: ## Сборка образов
	docker compose build

up: ## Запуск контейнеров с выводом логов
	docker compose up --build

up-d: ## Запуск контейнеров в фоновом режиме
	docker compose up -d --build

down: ## Остановка и удаление контейнеров
	docker compose down

stop: ## Остановка контейнеров
	docker compose stop

restart: ## Перезапуск
	docker compose restart

ps: ## Статус
	docker compose ps

exec: ## Войти в терминал запущенного  приложения
	docker compose exec app sh

pull: ## Скачивание  образов
	docker compose pull

migrate: ## Применить миграции
	docker compose exec app python manage.py migrate

loaddata: ## Загрузить  фикстуры
	docker compose exec app python manage.py loaddata initial

superuser: ## Создать админа
	docker compose exec app python manage.py createsuperuser