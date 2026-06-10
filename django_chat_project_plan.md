# Django Chat Application — Project Plan

---

## Overview

A real-time one-to-one chat application built with Django, Django Channels, PostgreSQL, and Redis. Users can register, find others by username, and chat in real time with a single persistent WebSocket connection per user.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django |
| Real-time | Django Channels |
| ASGI Server | Daphne |
| Database | PostgreSQL |
| Channel Layer | Redis |
| Frontend | HTML + Vanilla JS |

---

## Features

- User registration and login
- Search other users by username
- Home screen showing list of previous conversations
- Real-time messaging
- Unread message count and last message preview
- Online / offline presence indicator
- Single WebSocket connection per user (personal consumer)

---

## Database Models

### User
Standard Django `AbstractUser` — no changes needed.

### Profile (extends User)
| Field | Type | Purpose |
|---|---|---|
| user | OneToOne → User | link to auth user |
| avatar | ImageField | profile picture |
| is_online | BooleanField | online status |
| last_seen | DateTimeField | last active time |

### Conversation
Represents a unique chat between two users.

| Field | Type | Purpose |
|---|---|---|
| id | UUID | unique conversation ID |
| participants | ManyToMany → User | exactly two users |
| created_at | DateTimeField | when conversation started |
| last_message_at | DateTimeField | for sorting in home screen |

### Message
| Field | Type | Purpose |
|---|---|---|
| id | UUID | unique message ID (used for deduplication) |
| conversation | FK → Conversation | which conversation |
| sender | FK → User | who sent it |
| content | TextField | message text |
| is_read | BooleanField | read receipt |
| created_at | DateTimeField | timestamp |

---

## WebSocket Architecture

### Single Connection Per User — MainConsumer

One WebSocket connection opened when the user logs in. Stays open for the entire session regardless of which screen the user is on.

```
User logs in
      ↓
Frontend opens ws://example.com/ws/main/
      ↓
MainConsumer instance created
      ↓
Joins personal group "user_{id}"
      ↓
Stays open until logout / tab close
```

### What MainConsumer handles

| Event | Direction | Purpose |
|---|---|---|
| new_message | Server → Client | deliver incoming message |
| message_sent | Server → Client | echo back to sender |
| user_online | Server → Client | contact came online |
| user_offline | Server → Client | contact went offline |
| unread_count | Server → Client | update badge count |

### Groups in Redis

| Group Name | Who joins | Purpose |
|---|---|---|
| user_{id} | That specific user | personal notifications and messages |

No separate chat room groups needed — everything flows through personal groups.

---

## API Endpoints (HTTP)

| Method | URL | Purpose |
|---|---|---|
| POST | /api/auth/register/ | register new user |
| POST | /api/auth/login/ | login, get session |
| POST | /api/auth/logout/ | logout |
| GET | /api/users/search/?q=username | search users by username |
| GET | /api/conversations/ | list all conversations (home screen) |
| GET | /api/conversations/{id}/messages/ | load chat history |
| POST | /api/conversations/{id}/messages/ | send a message (saves to DB) |
| PATCH | /api/conversations/{id}/read/ | mark messages as read |

### Responsibilities split

| HTTP API | WebSocket |
|---|---|
| Load conversation list | Deliver new messages in real time |
| Load message history | Update unread badge |
| Send and save message to DB | Show online / offline status |
| Search users | Typing indicator (optional) |
| Mark as read | |

---

## Message Flow

### Sending a message

```
User A types message and hits send
        ↓
Frontend POST → /api/conversations/{id}/messages/
        ↓
Django view saves message to PostgreSQL
        ↓
View calls channel_layer.group_send → "user_{B_id}"
        ↓
Also calls channel_layer.group_send → "user_{A_id}"  (echo back to sender)
        ↓
User B's MainConsumer new_message() fires
        ↓
WebSocket pushes message to User B's browser
        ↓
Frontend checks current screen
    ↙                       ↘
chat is open            home screen
show message            show notification + badge
```

### User comes online

```
User A logs in and opens app
        ↓
MainConsumer connect() fires
        ↓
Fetch all contacts of User A from DB
        ↓
group_send → "user_{contact_id}" for each contact
        ↓
Each contact's MainConsumer user_online() fires
        ↓
Green dot appears next to User A in their contact list
```

---

## Project Folder Structure

```
django_chat/
    django_chat/
        settings.py
        urls.py
        asgi.py             ← ProtocolTypeRouter setup
    
    accounts/               ← registration, login, logout, profile
        models.py           ← Profile model
        views.py
        urls.py
        serializers.py
    
    chat/                   ← conversations and messages
        models.py           ← Conversation, Message models
        views.py            ← HTTP API views
        urls.py
        serializers.py
        consumers.py        ← MainConsumer
        routing.py          ← WebSocket URL routing
    
    templates/
        base.html
        home.html           ← conversation list
        chat.html           ← individual chat screen
    
    static/
        js/
            socket.js       ← WebSocket connection and handlers
            chat.js         ← chat UI logic
            home.js         ← home screen UI logic

    requirements.txt
    manage.py
```

---

## Frontend Screens

### Login / Register Screen
- Standard form
- On success → redirect to home screen
- On load → open WebSocket connection

### Home Screen
- Load conversation list via HTTP API on open
- Show last message preview and unread count per conversation
- Show online / offline dot per contact
- Search bar → calls /api/users/search/
- Real time updates via WebSocket (new messages, badges, online status)

### Chat Screen
- Load message history via HTTP API on open
- Send messages via HTTP POST
- Receive new messages via WebSocket
- Scroll to latest message on open
- Mark messages as read on open

---

## WebSocket Connection Lifecycle

```
App opens           → connect WebSocket, join "user_{id}" group
Contact comes online → receive user_online event, show green dot
Message received    → receive new_message event, update UI
App goes background → connection may drop
App comes back      → auto reconnect with exponential backoff
User logs out       → close WebSocket, leave group
```

### Reconnect strategy

```
Disconnect detected
        ↓
Wait 2 seconds → retry
        ↓
Wait 4 seconds → retry
        ↓
Wait 8 seconds → retry
        ↓
Max 30 seconds between retries
```

---

## Key Design Decisions

### One WebSocket per user (not per chat)
All real time events flow through a single personal consumer. The frontend decides what to do based on which screen is currently open. Keeps server-side logic simple and avoids managing multiple connections.

### HTTP for sending, WebSocket for receiving
Messages are saved to PostgreSQL via HTTP POST. This gives a clean confirmation the message was saved. WebSocket is only used to push events to recipients. This separation avoids duplicates and keeps each layer responsible for one thing.

### UUID for message IDs
Using UUID instead of auto-increment integer for message IDs. Prevents duplicate rendering when the same message arrives via both HTTP response and WebSocket push.

### Sorted user IDs for conversation lookup
When finding or creating a conversation between two users, always query by both user IDs regardless of order. Prevents duplicate conversations being created.

---

## Requirements

```
django
djangorestframework
channels
channels-redis
psycopg2-binary
daphne
pillow
python-decouple
```

---

## Environment Variables

```
SECRET_KEY=
DEBUG=
DATABASE_URL=
REDIS_URL=
ALLOWED_HOSTS=
```

---
