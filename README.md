# Employee Management System

Desktop application for employee registration, login, attendance, and face-based monitoring.

## Setup

Install the packages in `requirements.txt`, create the MySQL database with `database_schema.sql`, and configure local credentials in `.env` using `.env.example` as a template. Start the application with `python welcome.py`.

## Project files

- `welcome.py`: application entry point.
- `register.py`, `login.py`, `loginAI.py`: registration, login, and camera monitoring.
- `mainadmin.py`: administrative dashboard.
- `app_utils.py`: shared database configuration and helpers.
- `record.py`: webcam recording utility.
- `testConn.py`: database connectivity check.

Face samples, trained models, recordings, and `.env` are private local data and are excluded by `.gitignore`. The original SQL dump remains outside this folder because it contains employee data and password hashes.

## Security note

Passwords currently use legacy MD5 hashing. Replace it with a salted, adaptive password hash before production use.
