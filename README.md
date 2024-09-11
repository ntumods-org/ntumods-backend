<div align="center">
  <img src="./static/logo.png" alt="NTUMods logo" width="75">
  <h1>NTUMods</h1>
</div>

Backend repository for [NTUMods](https://www.ntumods.org), a course schedule planner for Nanyang Technological University students.

## Getting Started

This section will guide you through setting up the project on your local machine.

1. Prerequisites: please ensure you have the following installed on your machine:
    - [Python 3 (>=3.6)](https://www.python.org/downloads/)
    - [Git](https://git-scm.com/downloads)
  
2. Clone the repository and navigate to the project directory:
    ```bash
    git clone https://github.com/ntumods-org/ntumods-backend.git
    cd ntumods-backend
    ```

3. Create virtual environment and install dependencies:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements/development.txt
    ```

4. Set up environment variables:
    ```bash
    cp .env.example .env
    ```

5. Run migrations:
    ```bash
    python manage.py migrate
    ```

6. Load fixtures (sample data):
    ```bash
    python manage.py loaddata sample_data.json
    ```
    This should allow you to login with the following credentials:
    - Username: `superuser`
    - Password: `123`
  
7. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Features
- 📆 Timetable
- 📖 Course Information
- 🚀 Schedule Optimizer (WIP)

## Contributing
If you want to contribute to NTUMods, please read [CONTRIBUTING.md](./docs/CONTRIBUTING.md) to get started.

## License
NTUMods is open source and available under the [AGPL-3.0-or-later](./LICENSE) license.
