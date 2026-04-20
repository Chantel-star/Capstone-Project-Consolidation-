# News Application (News_capstone)

## Overview

This is a Django-based News Application that allows readers to view articles published by journalists and publishers. The system includes role-based access control, article approval workflows, and a RESTful API for external integration.

Users are assigned roles (Reader, Editor, Journalist), and permissions are managed using Django’s authentication system and custom user model.

---

## Features

### User Roles

- **Reader**

  - Can view approved articles
  - Subscribes to publishers and journalists

- **Editor**
  - Reviews articles
  - Approves or rejects articles

- **Journalist**
  - Creates articles
  - Updates own articles
  - Submits articles for approval

---

### Article System

- Create articles (Journalists only)
- Edit articles
- Editor approval system
- Only approved articles are visible to readers

---

### Authentication & Permissions

- Custom User model (`AUTH_USER_MODEL`)
- Role-based access control
- Group-based permissions (Reader, Editor, Journalist)

---

### REST API

Endpoint:
Returns articles based on:

- User subscriptions (publishers & journalists)
- Approved status

---

### Testing

Automated unit tests implemented using Django TestCase:

- API authentication tests
- Subscription filtering tests
- Data integrity tests

Run tests:

```bash

python manage.py test

###UI Improvements

Basic CSS styling has been added to improve:

-Layout and spacing
-Readability
-Buttons and navigation

###Future improvements:

-Bootstrap integration
-Responsive design
-Enhanced user experience

### 1. Clone the repository

```bash

git clone <https://github.com/Chantel-star/news_capstone.git>

cd news_capstone

### Create and activate virtual environment
python -m venv venv

### Activate it:
venv\Scripts\activate

### Install dependencies & Apply migrations
 pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

### Create a superuser(admin)
python manage.py createsuperuser

### Run the development server
pyhton manage.py  runserver

### Open in browser
go to:
http://127.0.0.1:8000/
