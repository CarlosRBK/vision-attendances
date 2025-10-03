# Makefile para facilitar comandos de Docker
# Uso: make <comando>

.PHONY: help build up down restart logs clean ps exec-backend exec-frontend

help: ## Muestra esta ayuda
	@echo "Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Configuración inicial (copia .env.example)
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "✅ backend/.env creado. Por favor edita con tus credenciales."; \
	else \
		echo "✅ backend/.env ya existe."; \
	fi

build: ## Construye las imágenes Docker
	docker-compose build

up: ## Inicia los servicios
	docker-compose up -d

down: ## Detiene los servicios
	docker-compose down

restart: ## Reinicia los servicios
	docker-compose restart

logs: ## Muestra los logs de todos los servicios
	docker-compose logs -f

logs-backend: ## Muestra los logs del backend
	docker-compose logs -f backend

logs-frontend: ## Muestra los logs del frontend
	docker-compose logs -f frontend

ps: ## Muestra el estado de los servicios
	docker-compose ps

clean: ## Detiene y elimina contenedores, redes e imágenes
	docker-compose down --rmi all -v

clean-volumes: ## ⚠️  Detiene y elimina TODO incluyendo volúmenes (datos persistentes)
	docker-compose down -v --rmi all

exec-backend: ## Accede al shell del backend
	docker-compose exec backend sh

exec-frontend: ## Accede al shell del frontend
	docker-compose exec frontend sh

rebuild-backend: ## Reconstruye solo el backend
	docker-compose build backend
	docker-compose up -d backend

rebuild-frontend: ## Reconstruye solo el frontend
	docker-compose build frontend
	docker-compose up -d frontend

prod-build: ## Construye las imágenes para producción
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Inicia los servicios en modo producción
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

dev: setup build up ## Setup completo y inicio en desarrollo

health: ## Verifica el estado de salud de los servicios
	@echo "Backend health:"
	@curl -f http://localhost:8000/health || echo "❌ Backend no responde"
	@echo "\nFrontend health:"
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "✅ Frontend OK" || echo "❌ Frontend no responde"
