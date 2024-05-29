# Creato Backend (Identity Service)

This is the backend microservice of Creato, a social media management software developed using Django (python framework).

### Frontend Source Code: [Click Here](https://github.com/Abhisek0721/creato-frontend)

## Features

- **Authentication:** User registration, login, and session based authentication.
- **User Management:** CRUD operations for user.
- **Team Management:** CRUD operations for team.
- **Workspace Management:** CRUD operations for workspace (for project management).

## Technologies Used

- **Django:** Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **DRF:** Django REST Framework is a powerful and flexible toolkit for building Web APIs.
- **PostgreSQL:** A SQL database for storing data.
- **Redis:** Used for storing sessions and cache.

## Installation

1. Clone the repository: `git clone https://github.com/Abhisek0721/identity-service-creato`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables: Create a `.env` file and define the following variables:
   ```
    DEBUG=True
    SECRET_KEY=your-secret-key
    DB_NAME=identity_creato
    DB_USER=postgres
    DB_PASSWORD=root
    DB_HOST=localhost
    DB_PORT=5432
   ```
4. Run the server: `python manage.py runserver`

## License

This project is licensed under the MIT License - see the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Abhisek0721/identity-service-creato/blob/main/LICENSE)
 file for details.

</br></br>
Feel free to contact me: abhisek0721@gmail.com
