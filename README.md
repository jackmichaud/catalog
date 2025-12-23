# CataLog

A modern catalog application built with Django that allows users to browse, search, and manage items in a categorized system. Also supports chats and posts for users to interact with each other and collaborate on sustainability efforts.

Live demo: https://cs3240-a21-12d856f83fd4.herokuapp.com/ (taken down)

## Features

- User authentication and authorization
- Category and item management
- Search functionality
- Responsive design
- Admin dashboard for content management
- User posts and discussion threads
- Real-time or asynchronous chat between users

## Tech Stack

- Backend: Django 4.2
- Frontend: HTML5, CSS3, JavaScript
- Database: SQLite (Development), PostgreSQL (Production)
- Deployment: Heroku

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/catalog.git
cd catalog
```

2. Set up a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the database:

```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: Create admin user
```

### Running the Development Server

```bash
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) in your browser to view the application.

### Accessing Admin Panel

The admin panel is available at [http://localhost:8000/admin](http://localhost:8000/admin). Use the superuser credentials you created during setup.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


