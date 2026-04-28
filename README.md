# News Application

This is a Django news application where users can register and interact with the system based on their roles.

## Features

- User registration and login
- Role-based access
- Journalists can create articles
- Publishers can manage publishing-related content
- Readers can view approved articles
- Optional publisher assignment for articles
- API endpoint for approved subscribed content

## User Roles

### Reader
- Can register and log in
- Can view approved articles
- Can subscribe to publishers and journalists

### Journalist
- Can register and log in
- Can create articles independently
- Does not need to belong to a publisher before creating an article

### Publisher
- Can register and log in
- Can manage publisher-related content
- Can approve articles if your app includes this feature

## Important Business Rule

Journalists are allowed to create articles **without being assigned to a publisher**.

The `publisher` field on articles is optional, so articles can be created independently.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Chantel-star/news_capstone.git

2.Enter the project folder
cd news_capstone

3.Create a virtual environment
python -m venv venv

4. Activate the virtual environment
Windows
venv\Scripts\activate
macOS/Linux
source venv/bin/activate

4. Install dependencies
pip install -r requirements.txt

6. Create the MariaDB/MySQL database
Log into MySQL:
mysql -u root -p
CREATE DATABASE news_db;
EXIT;


7. Run migrations
python manage.py makemigrations
python manage.py migrate

8. Create a superuser
python manage.py createsuperuser

9. Start the development server
python manage.py runserver

10. Open the application

Go to:

http://127.0.0.1:8000/

Run tests with:

python manage.py test