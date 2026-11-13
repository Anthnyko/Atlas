# Atlas

Atlas is a full-stack spaced-repetition learning app for creating decks, managing cards, and building a consistent study practice.

## Features

- Account registration and JWT-based authentication
- Deck and card creation, editing, and deletion
- Tags and search across cards, decks, and tags
- Spaced-repetition study sessions with progress tracking
- PostgreSQL persistence and Alembic database migrations
- Responsive React interface

## Tech stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, Axios
- Backend: FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL
- Development environment: Docker Compose

## Project structure

```text
atlas/
├── backend/       # FastAPI application and Alembic migrations
├── frontend/      # React + TypeScript application
├── docker-compose.yml
└── README.md
```