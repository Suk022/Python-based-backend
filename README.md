# Text Processing API

A production-ready backend API for text processing with user authentication, designed to handle paragraph submissions, word indexing, and efficient text search. This project demonstrates modern Python backend development using FastAPI, SQLAlchemy, and asynchronous task processing.

## Key Features

- **User Authentication**: Secure JWT-based authentication with refresh tokens
- **Text Processing**: Efficient word indexing and frequency analysis
- **Search Capabilities**: Fast search with relevance ranking by word frequency
- **Asynchronous Processing**: Background tasks for non-blocking operations
- **Scalable Architecture**: Designed for horizontal scaling
- **Containerized**: Ready for Docker and cloud deployment


## System Architecture

### Tech Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: JWT with bcrypt password hashing
- **Background Processing**: FastAPI BackgroundTasks
- **API Documentation**: Auto-generated OpenAPI/Swagger UI
- **Containerization**: Docker with multi-stage builds
- **Testing**: pytest test coverage
- **CI/CD**: GitHub Actions ready

### Database Schema

```mermaid
erDiagram
    users ||--o{ paragraphs : "1-to-many"
    users ||--o{ word_counts : "1-to-many"
    users ||--o{ refresh_tokens : "1-to-many"
    paragraphs ||--o{ paragraph_word_counts : "1-to-many"
    
    users {
        UUID id PK
        string email "UQ, indexed"
        string hashed_password
        datetime created_at
    }
    
    paragraphs {
        UUID id PK
        UUID user_id FK
        text content
        datetime created_at
    }
    
    word_counts {
        UUID id PK
        UUID user_id FK
        string word "indexed"
        integer count "indexed"
    }
    
    paragraph_word_counts {
        UUID id PK
        UUID user_id FK
        UUID paragraph_id FK
        string word "indexed"
        integer count "indexed"
    }
    
    refresh_tokens {
        UUID id PK
        UUID user_id FK
        string token "UQ, indexed"
        datetime expires_at
    }
```

### Data Flow

1. **User Authentication**
   - User registers with email/password
   - Password is hashed using bcrypt
   - JWT tokens are issued for authenticated sessions

2. **Paragraph Submission**
   - User submits one or more paragraphs
   - Paragraphs are stored in the database
   - Background task is triggered for word indexing

3. **Word Indexing Process**
   - Text is tokenized into words (case-insensitive)
   - Word frequencies are calculated per paragraph
   - Global word counts are updated
   - All counts are stored in optimized database tables

4. **Search Operation**
   - User searches for a word
   - System queries pre-computed word frequencies
   - Results are ranked by word count
   - Paginated results are returned

##  Quick Start

### Prerequisites
- Python 3.11+
- pip (or Docker for containerized setup)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Suk022/Python-based-backend.git
   cd backend-assignment
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Access the API:**
   - **API Documentation**: `http://localhost:8000/docs`
   - **Health Check**: `http://localhost:8000/health`
   - **Root Endpoint**: `http://localhost:8000/`

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# App Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=sqlite:///./database.db
# For PostgreSQL: postgresql://user:password@localhost:5432/dbname

# CORS (comma-separated origins, or * for all)
CORS_ORIGINS=*
```

## API Documentation

### Authentication

#### `POST /auth/register`
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### `POST /auth/login`
Authenticate user and get access token.

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "refresh_token": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Paragraphs

#### `POST /paragraphs`
Submit one or more paragraphs for processing.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "paragraphs": [
    "This is the first paragraph.",
    "This is another paragraph with more text."
  ]
}
```

**Response:**
```json
{
  "message": "Created 2 paragraphs",
  "paragraph_ids": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"],
  "indexing_status": "queued"
}
```

#### `GET /paragraphs`
List user's paragraphs with pagination.

**Query Parameters:**
- `page` (int, default: 1)
- `per_page` (int, default: 20, max: 100)

#### `GET /paragraphs/search`
Search paragraphs containing a specific word, ranked by frequency.

**Query Parameters:**
- `word` (string, required): Word to search for

**Response:**
```json
{
  "word": "example",
  "total_found": 5,
  "results": [
    {
      "paragraph_id": "550e8400-e29b-41d4-a716-446655440000",
      "content": "This is an example paragraph with the word example.",
      "word_count": 2,
      "created_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

## Development

### Project Structure

```
backend-assignment/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application setup
│   ├── config.py             # Configuration settings
│   ├── database.py           # Database connection and models
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic models for request/response
│   ├── auth.py               # Authentication utilities
│   ├── indexing.py           # Text processing and word counting
│   └── routers/
│       ├── __init__.py
│       ├── auth.py           # Authentication routes
│       └── paragraphs.py     # Paragraph management routes
├── tests/                    # Test files
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
├── Dockerfile                # Production Dockerfile
└── docker-compose.yml        # Docker Compose for development
```

## Testing Guide

### Below are the instructions for testing APIs using different methods:
1. **Start the application:**
   ```bash
   # Using Python directly
   uvicorn app.main:app --reload --port 8000
   
   # Using Docker
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Open Swagger UI:** `http://localhost:8000/docs`

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
