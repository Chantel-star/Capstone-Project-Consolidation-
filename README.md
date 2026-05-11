# News Application

This is a Django news application where users can register and interact with the system based on their roles.

## Features

* User registration and login
* Role-based access
* Journalists can create articles
* Editors can approve articles and newsletters
* Readers can view approved articles
* Subscription system for publishers and journalists
* REST API endpoint for approved subscribed content
* Docker support
* Sphinx documentation

---

# User Roles

## Reader

* Can register and log in
* Can view approved articles
* Can subscribe to publishers and journalists

## Journalist

* Can register and log in
* Can create articles independently
* Does not need to belong to a publisher before creating an article

## Editor

* Can register and log in
* Can approve articles and newsletters

---

# Important Business Rule

Journalists are allowed to create articles **without being assigned to a publisher**.

The `publisher` field on articles is optional, so articles can be created independently.

---

# Installation and Setup

## 1. Clone the repository

```bash
git clone https://github.com/Chantel-star/Capstone-Project-Consolidation-.git
```

---

## 2. Enter the project folder

```bash
cd news_capstone
```

---

## 3. Create and activate a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Create the MySQL database

Before running migrations, create the database and database user in MySQL.

Log into MySQL:

```bash
mysql -u root -p
```

Run the following SQL commands:

```sql
CREATE DATABASE news_db;

CREATE USER 'news_user'@'localhost'
IDENTIFIED BY 'your_password_here';

GRANT ALL PRIVILEGES ON news_db.* TO
'news_user'@'localhost';

FLUSH PRIVILEGES;
EXIT;
```

---

## 6. Update database settings

Open:

```bash
news_project/settings.py
```

Update the database configuration:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "news_db",
        "USER": "news_user",
        "PASSWORD": "your_password_here",
        "HOST": "localhost",
        "PORT": "3306",
    }
}
```

---

## 7. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 8. Create a superuser

```bash
python manage.py createsuperuser
```

---

## 9. Run the server

```bash
python manage.py runserver
```

Open the browser at:

```text
http://127.0.0.1:8000/
```

---

# Docker Setup

## Build the Docker image

```bash
docker build -t news-capstone-app .
```

## Run the Docker container

```bash
docker run -p 8000:8000 news-capstone-app
```

---

# Documentation

Sphinx documentation is included in the `docs` folder.

To rebuild the documentation:

```bash
cd docs
.\make.bat html
```

Generated HTML files are located in:

```text
docs/_build/html
```

Open `index.html` in a browser to view the documentation.

---

# API Endpoint

```text
/api/articles/
```

---

# Technologies Used

* Python
* Django
* Django REST Framework
* MySQL
* Docker
* Sphinx

---

