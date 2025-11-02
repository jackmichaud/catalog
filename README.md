[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/k4pNZww7)


# Development

Step 1: Install virtual environment and dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Step 2: Run the development server
```bash
python manage.py runserver
```

Step 3: Open http://localhost:8000 in your browser
Step 4 (optional): open the Django admin panel at http://localhost:8000/admin

If you get an error with migrations:

```bash
python manage.py migrate
```
