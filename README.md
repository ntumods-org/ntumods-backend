<div align="center">
  <img src="./static/logo.png" alt="NTUMods logo" width="75">
  <h1>NTUMods</h1>
</div>

Backend repository for [NTUMods](https://www.ntumods.org), a course schedule planner for Nanyang Technological University students.

## Development Guide

This section will guide you through setting up the project on your local machine.

### Prerequisites
Please ensure you have the following installed on your machine:

- [Python 3 (>=3.6)](https://www.python.org/downloads/)
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
pip install -r requirements/development.txt
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

## Features
- 📆 Timetable
- 📖 Course Information
- 🚀 Schedule Optimizer (WIP)

## Contributing
If you want to contribute to NTUMods, please read [CONTRIBUTING.md](./docs/CONTRIBUTING.md) to get started.

## License
NTUMods is open source and available under the [AGPL-3.0-or-later](./LICENSE) license.
