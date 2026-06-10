# Pingout — Django Chat Application

A real-time one-to-one chat application built with Django, Django Channels, PostgreSQL, and Redis. Users register, search for other users, and chat in real time over a single persistent WebSocket connection per user.

See [django_chat_project_plan.md](django_chat_project_plan.md) for the full design doc.

## Tech Stack

- Backend: Django + Django REST Framework
- Real-time: Django Channels (Daphne ASGI server)
- Database: PostgreSQL
- Channel layer: Redis
- Frontend: HTML + vanilla JS

## Project Structure

- `pingout/` — Django project settings, URLs, ASGI config
- `users/` — registration, login, logout, user profiles
- `chat/` — conversations, messages, WebSocket consumers, HTTP chat API

(Note: the plan doc refers to the users app as `accounts` and the project as `django_chat` — the actual app/project names in this repo are `pingout` and `users`.)

## Core Concepts

- **Models**: `Profile` (extends User with avatar/online status), `Conversation` (M2M between two users), `Message` (UUID-keyed, FK to conversation/sender)
- **WebSocket**: a single `MainConsumer` per logged-in user, joined to a personal group `user_{id}`, handles new messages, send confirmations, online/offline presence, and unread counts
- **HTTP vs WebSocket split**: messages are sent/saved via HTTP POST; WebSocket is used only to push real-time events (new messages, presence, unread badges) to the recipient/sender
- **Conversation lookup**: always queried by both user IDs regardless of order, to avoid duplicate conversations
- **Message IDs**: UUIDs, to avoid duplicate rendering when a message arrives via both the HTTP response and the WebSocket push

## Status

Early setup stage — `users` and `chat` apps scaffolded; models, views, consumers, and frontend templates are still being built out per the project plan.

## Working Agreement

The user is learning Django backend development and wants to implement the backend (models, views, serializers, consumers, URLs, etc.) themselves. Limit assistance to UI/frontend work — HTML templates, CSS, and JavaScript (including WebSocket client code). Do not write or edit backend Python code unless explicitly asked; explanations and guidance on backend concepts are fine.
