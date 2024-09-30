docker build -f deployments/prod/Dockerfile -t ntumods_api_prod .
docker run -d -p 8080:8080 --env-file .env --name ntumods_api_prod ntumods_api_prod
