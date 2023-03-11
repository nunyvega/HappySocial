# HappySocial

[![Python](https://img.shields.io/badge/Python-3.9-blue)](https://www.python.org/downloads/release/python-390/)
[![Django](https://img.shields.io/badge/Django-3.2.9-green)](https://docs.djangoproject.com/en/3.2/releases/3.2/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-4.3.1-purple)](https://getbootstrap.com/docs/4.3/getting-started/introduction/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

HappySocial is a social network web application built with Django and Bootstrap. It allows users to create profiles, connect with friends, post messages, and participate in chat rooms.

## Features

- User registration and login
- User profile with profile picture, bio, and location
- Friend system for connecting with other users
- Newsfeed for viewing posts by friends
- Post creation with text and image upload
- Chat rooms for real-time messaging with other users

## Installation

1. Clone the repository or download the zip with the code:

```bash
git clone https://github.com/nunyvega/social.git
```

2. Create a virtual environment and activate it:

```bash
cd src
pip install virtualenvwrapper
mkvirtualenv env1
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Run the migrations:
```bash
python manage.py makemigrations
python manage.py migrate
````

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Install and start Redis
```bash
For mac:
brew install redis
For windows:
sudo apt-get install redis
redis-server
```
8. Open a web browser and go to http://localhost:8000/ to access the application.


## Credit
This project was developed by Alvaro Vega as part of Advanced Web Development from the University of London, March 2023.

## License
This project is licensed under the MIT License



