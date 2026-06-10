# PingOut 🏓

A real-time personal chat application built with Django and WebSockets.

---

## About

PingOut lets you find anyone by username and start a conversation instantly. Messages are delivered in real time — no refreshing, no delays.

---

## Features

- User registration and login
- Find other users by username
- Real-time one-to-one messaging
- Conversation history on home screen

---

## Tech Stack

- **Backend** — Django
- **Real-time** — Django Channels (WebSockets)
- **Database** — PostgreSQL
- **Channel Layer** — Redis
- **Server** — Daphne (ASGI)

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis

### Installation

```bash
# clone the repo
git clone https://github.com/yourusername/pingout.git
cd pingout

# create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# install dependencies
pip install -r requirements.txt
```

### Run

```bash
# apply migrations
python manage.py migrate

# start the server
daphne pingout.asgi:application
```

Open `http://localhost:8000` in your browser.

---

## Project Status

🚧 Under development
