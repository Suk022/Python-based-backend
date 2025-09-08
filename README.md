# Backend Assignment

A production-ready but lightweight backend for paragraph indexing and search, built with FastAPI, SQLAlchemy, and Celery.

## Features

- **User Authentication**: JWT-based auth with register/login/logout
- **Paragraph Management**: Submit multiple paragraphs in a single request
- **Word Indexing**: Automatic background indexing with word frequency tracking
- **Search**: Find top 10 paragraphs by word frequency for authenticated users
- **Dual Mode**: SQLite for development, PostgreSQL + Redis + Celery for production
- **Containerized**: Docker setup with lightweight images

## Quick Start

### Development Mode (SQLite - No Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
USE_SQLITE=true uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode (Docker)

```bash
# Start all services (web + worker + postgres + redis)
docker-compose up --build

# Or use make
make up
```

### Development Mode (Docker - SQLite only)

```bash
# Start only web service with SQLite
docker-compose up web --build

# Or use make
make dev-up
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT tokens
- `POST /auth/logout` - Logout (invalidate refresh token)

### Paragraphs
- `POST /paragraphs` - Submit multiple paragraphs
- `GET /paragraphs` - List user paragraphs (paginated)
- `GET /paragraphs/search?word=<word>` - Search paragraphs by word frequency

### Documentation
- `GET /docs` - Swagger UI
- `GET /` - API info
- `GET /health` - Health check

## Step-by-Step API Testing Guide

### Method 1: Using Swagger UI (Recommended)

1. **Start the application:**
   ```bash
   # Using Python directly
   USE_SQLITE=true uvicorn app.main:app --reload --port 8000
   
   # Using Docker
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Open Swagger UI:** http://localhost:8000/docs

3. **Test User Registration:**
   - Find `POST /auth/register`
   - Click "Try it out"
   - Enter test data:
     ```json
     {
       "email": "test@example.com",
       "password": "password123"
     }
     ```
   - Click "Execute"
   - **Expected:** Status 200, user_id returned

4. **Test User Login:**
   - Find `POST /auth/login`
   - Use same credentials as registration
   - Click "Execute"
   - **Copy the `access_token` from response**

5. **Authorize for Protected Endpoints:**
   - Click **"Authorize"** button (top right)
   - Enter: `YOUR_ACCESS_TOKEN`
   - Click "Authorize"

6. **Test Paragraph Submission:**
   - Find `POST /paragraphs/`
   - Enter test paragraphs:
     ```json
     {
       "paragraphs": [
         "Python is a great programming language. Python is easy to learn.",
         "I love coding in Python. Python has many libraries.",
         "JavaScript is popular, but Python is my favorite programming language."
       ]
     }
     ```
   - Click "Execute"
   - **Expected:** Status 200, success message

7. **Test Word Search:**
   - Find `GET /paragraphs/search`
   - Enter search word: `python`
   - Click "Execute"
   - **Expected:** Paragraphs ranked by word frequency

8. **Test Paragraph Listing:**
   - Find `GET /paragraphs/`
   - Click "Execute"
   - **Expected:** Paginated list of your paragraphs

### Method 2: Using Postman

1. **Import Collection:** Create requests for each endpoint
2. **Set Environment Variable:** `{{token}}` for authorization
3. **Test Flow:** Register - Login - Save token - Test protected endpoints

### Method 3: Automated Testing

```bash
# Register user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Submit paragraphs (use token from login)
curl -X POST "http://localhost:8000/paragraphs/" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"paragraphs": ["I love apple pie. Apple is sweet.", "The apple tree grows apples."]}'

# Search for word
curl -X GET "http://localhost:8000/paragraphs/search?word=apple" \
  -H "Authorization: Bearer <your-token>"
```

## Configuration

Environment variables:

- `USE_SQLITE=true` - Use SQLite instead of PostgreSQL (dev mode)
- `POSTGRES_HOST` - PostgreSQL host (default: localhost)
- `POSTGRES_USER` - PostgreSQL user (default: backend_user)
- `POSTGRES_PASSWORD` - PostgreSQL password (default: password)
- `POSTGRES_DB` - PostgreSQL database (default: backend_db)
- `REDIS_URL` - Redis URL (default: redis://localhost:6379/0)
- `SECRET_KEY` - JWT secret key (change in production!)

## Testing

```bash
# Run tests (uses SQLite automatically)
make test

# Or directly with pytest
USE_SQLITE=true python -m pytest tests/ -v
```

## Make Commands

```bash
make build      # Build Docker images
make up         # Start production mode (all services)
make dev-up     # Start development mode (web only)
make test       # Run tests
make clean      # Clean Docker resources
make clean-all  # Clean everything including images
make dev-local  # Run locally without Docker
```

## Architecture

### Models
- `User` - User accounts with email/password
- `Paragraph` - User-submitted text content
- `WordCount` - Global word frequency per user
- `ParagraphWordCount` - Word frequency per paragraph
- `RefreshToken` - JWT refresh token storage

### Indexing Process
1. User submits paragraphs via `POST /paragraphs`
2. Paragraphs are stored immediately
3. Background task indexes words:
   - Tokenizes text (lowercase, remove punctuation)
   - Updates `ParagraphWordCount` (per paragraph)
   - Updates `WordCount` (global user totals)
   - Uses SQL upserts for concurrency safety

### Search Algorithm
1. Query `ParagraphWordCount` for user + word
2. Join with `Paragraph` for content
3. Order by word count descending
4. Return top 10 results

## Database Indexes

Optimized for fast search:
- `(user_id, word)` - Word lookup
- `(user_id, word, count)` - Frequency sorting
- `(paragraph_id)` - Paragraph joins

## Docker Optimization

- Uses `python:3.11-slim` base image
- Multi-stage builds avoided for simplicity
- `.dockerignore` excludes unnecessary files
- `pip install --no-cache-dir` reduces image size
- Alpine images for PostgreSQL and Redis

### Clean Docker Cache

```bash
# Remove unused containers, networks, images
docker system prune -a --volumes

# Remove build cache
docker builder prune

# Or use make
make clean-all
```

## Production Considerations

- Change `SECRET_KEY` environment variable
- Configure CORS origins appropriately
- Use Alembic migrations instead of `create_all()` (TODO)
- Set up proper logging and monitoring
- Configure PostgreSQL connection pooling
- Use Redis Sentinel for high availability

## Development vs Production

| Feature | Development (SQLite) | Production (Docker) |
|---------|---------------------|-------------------|
| Database | SQLite file | PostgreSQL container |
| Indexing | Synchronous/BackgroundTasks | Celery + Redis |
| Setup | Single command | Docker Compose |
| Dependencies | Python only | Full stack |

## File Structure

```
├── app/
│   ├── routers/
│   │   ├── auth.py          # Authentication endpoints
│   │   └── paragraphs.py    # Paragraph and search endpoints
│   ├── auth.py              # Authentication utilities
│   ├── celery_app.py        # Celery configuration
│   ├── config.py            # Settings and configuration
│   ├── database.py          # Database setup
│   ├── dependencies.py      # FastAPI dependencies
│   ├── indexing.py          # Word indexing logic
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   └── tasks.py             # Celery tasks
├── tests/
│   └── test_api.py          # API tests
├── docker-compose.yml       # Production Docker setup
├── docker-compose.override.yml  # Development overrides
├── Dockerfile               # Container definition
├── Makefile                 # Build and run commands
├── requirements.txt         # Python dependencies
└── README.md               # This file
```
