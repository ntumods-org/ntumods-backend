<div align="center">
  <img src="./static/logo.png" alt="NTUMods logo" width="75">
  <h1>NTUMods</h1>
</div>

Backend repository for [NTUMods](https://www.ntumods.org), a course schedule planner for Nanyang Technological University students.

## Development Guide

This section will guide you through setting up the project on your local machine without using Docker.

> This method is more preferrable for backend developers as you can make use of the automatic reloads provided by Django's `runserver`. 

### Prerequisites
Please ensure you have the following installed on your machine:

- [Python 3.11](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
  
### Cloning the Repository
Use the following command to clone the repository to your local machine:
```bash
git clone https://github.com/ntumods-org/ntumods-backend.git
cd ntumods-backend
```

### Using Virtual Environments
#### Creating a Virtual Environment

```bash
python3 -m venv venv
```

#### Activating the Virtual Environment
##### Linux
```bash
source venv/bin/activate
```
##### Windows
```bash
venv\Scripts\activate
```

#### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Loading Environment Variables
#### Copy `.env.example` to `.env`
```bash
cp .env.example .env
```

### Running Database Migrations
```bash
python manage.py migrate
```

### Loading Sample Data
```bash
python manage.py loaddata sample_data.json
```
This should allow you to login as superuser (admin) with the following credentials:
- Username: `superuser`
- Password: `123`
  
### Running the development server
```bash
python manage.py runserver
```

## Using Docker

This section will guide you through setting up the project on your local machine using Docker. It is recommended to use Docker for development to ensure consistency across different environments.

1. Install Docker Desktop based on your operating system ([MAC](https://docs.docker.com/desktop/install/mac-install/) / [Windows](https://docs.docker.com/desktop/install/windows-install/) / [Linux](https://docs.docker.com/desktop/install/linux-install/)) and launch the application.

2. Clone this repository and move into the project directory where `docker-compose.yml` file is located.

    ```bash
    git clone https://github.com/ntumods-org/ntumods-backend.git
    cd ntumods-backend
    ```

3. Install the server using Docker

    ```bash
    docker compose up --build -d
    ```

    Stop using `Ctrl+C`. Re-run this command when you want to start the server again in your local development environment. Your server should be up at `localhost:8000`. Migration should be done automatically when the server is started.

4. Load sample data

    ```bash
    docker exec -ti ntumods_api python manage.py loaddata sample_data.json
    ```

    If this is the first time you are running the server, please execute this command to load sample data. This should allow you to login as superuser (admin) with the following credentials:
    - Username: `superuser`
    - Password: `123`

    You can execute other utility commands by running `docker exec -ti ntumods_api python manage.py <command>`, such as making migrations, executing tests, etc.

### Setting up PostgreSQL using Docker (optional)
#### Using Docker

Make sure you have Docker installed. 

```bash
docker pull postgres
docker run --name postgres-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  -d postgres
```


## Features
- 📆 Timetable
- 📖 Course Information
- 🚀 Schedule Optimizer (WIP)

## Contributing
If you want to contribute to NTUMods, please read [CONTRIBUTING.md](./docs/CONTRIBUTING.md) to get started.

## License
NTUMods is open source and available under the [AGPL-3.0-or-later](./LICENSE) license.
