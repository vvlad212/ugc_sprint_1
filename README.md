## Installation
docker-compose up --build

## Init db
flask db upgrade

## Flask auth api OpenAPI Specification
localhost:8000/auth_api/doc/

## FastApi online cinema api OpenAPI Specification
localhost:8000/movies_api/openapi

## Create admin user
flask createsuperuser <email> <password>

## clickhouse initialization
Execute code for nodes (node1, node3, node5) from clickhouse.ddl file
  
## Sources
https://github.com/vvlad212/ugc_sprint_1
