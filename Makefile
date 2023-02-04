build:
	docker-compose build
run:
	docker-compose up -d
stop:
	docker-compose down
db-init:
	docker-compose exec db psql -U postgres -f /sql_scripts/db_init.sql
