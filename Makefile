-include .env
export

.PHONY: help build sonar-up sonar-down run clean sonar-scan nuke

# Use token from command line or from .env/environment
SCAN_TOKEN ?= $(SONAR_TOKEN)
ifneq ($(token),)
	SCAN_TOKEN := $(token)
endif

# Default target
help:
	@echo "Sherlock Docker Automation"
	@echo "-------------------------"
	@echo "Usage:"
	@echo "  make build          Build the Sherlock image"
	@echo "  make sonar-up       Start SonarQube (http://localhost:9000)"
	@echo "  make sonar-down     Stop SonarQube"
	@echo "  make sonar-scan     Run SonarQube analysis (uses SONAR_TOKEN from .env)"
	@echo "  make run user=NAME  Run Sherlock for a specific username"
	@echo "  make clean          Stop all services and remove volumes"
	@echo "  make nuke           Stop all services, remove volumes, networks and images"

build:
	docker-compose build sherlock

sonar-up:
	@echo "Ensuring SonarQube requirements are met..."
	docker-compose up -d sonarqube
	@echo "SonarQube is starting. Access it at http://localhost:9000"
	@echo "Default credentials: admin / admin"

sonar-down:
	docker-compose stop sonarqube

sonar-scan:
	@if [ -z "$(SCAN_TOKEN)" ] || [ "$(SCAN_TOKEN)" = "your_token_here" ]; then \
		echo "Error: Please provide a SonarQube token."; \
		echo "Option 1: Create a .env file with SONAR_TOKEN=your_token"; \
		echo "Option 2: Pass it manually: make sonar-scan token=YOUR_TOKEN"; \
		echo "1. Go to http://localhost:9000"; \
		echo "2. Log in (admin/admin)"; \
		echo "3. Create a project and generate a token."; \
		exit 1; \
	fi
	docker-compose run --rm \
		-e SONAR_LOGIN="$(SCAN_TOKEN)" \
		sonar-scanner

run:
	@if [ -z "$(user)" ]; then \
		echo "Error: Please provide a username. Usage: make run user=USERNAME"; \
		exit 1; \
	fi
	mkdir -p results
	docker-compose run --rm sherlock --folderoutput /sherlock/results $(user)

clean:
	docker-compose down -v

nuke:
	docker-compose down -v --remove-orphans --rmi all
