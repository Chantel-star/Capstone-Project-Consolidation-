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

### 
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
## Virtual Environment Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Run the server:

```bash
python manage.py runserver
```

## Docker Setup

Build the Docker image:

```bash
docker build -t news-capstone-app .
```

Run the Docker container:

```bash
docker run -p 8000:8000 news-capstone-app
```

## Documentation

Sphinx documentation is included in the `docs` folder.

