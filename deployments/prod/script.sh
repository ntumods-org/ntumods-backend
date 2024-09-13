docker build -f deployments/prod/Dockerfile -t ntumods_prod_backend .
docker run -d -p 8000:8000 --env-file .env ntumods_prod_backend
