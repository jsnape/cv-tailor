# CV Tailor Agent - Multi-User AI Resume Customization

A sophisticated AI agent that analyzes job specifications and creates tailored CVs and professional bios using your personal knowledge base.

## Features

- **Multi-User Support**: Secure user authentication and data isolation
- **Job Analysis**: Extract requirements from URLs or documents
- **AI-Powered Tailoring**: Generate customized CVs using Microsoft Agent Framework
- **Professional Bios**: Create one-page bios for presentations
- **Multiple Formats**: Export to PDF, DOCX, and Markdown
- **Knowledge Management**: Personal skill and experience database

## Quick Start

### Installation

```bash
# Install dependencies (--pre required for Agent Framework)
pip install agent-framework-azure-ai --pre
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database
alembic upgrade head

# Run the application
uvicorn src.api.main:app --reload
```

### Configuration

Create a `.env` file with:

```env
# API Keys
GITHUB_TOKEN=your_github_personal_access_token
OPENAI_API_KEY=your_openai_key  # Optional fallback

# Database
DATABASE_URL=sqlite+aiosqlite:///./cv_tailor.db
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cv_tailor

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Settings
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Profile Management
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `POST /api/profile/import` - Import profile data

### Job Analysis
- `POST /api/jobs/analyze` - Analyze job posting
- `GET /api/jobs/history` - Get analysis history
- `GET /api/jobs/{id}` - Get specific analysis

### Content Generation
- `POST /api/generate/cv` - Generate tailored CV
- `POST /api/generate/bio` - Generate professional bio
- `GET /api/generate/history` - View generation history

## Usage Example

### Web API
```python
import requests

# Login
auth = requests.post("http://localhost:8000/api/auth/login", 
    json={"email": "user@example.com", "password": "password"})
token = auth.json()["access_token"]

# Analyze job
job = requests.post("http://localhost:8000/api/jobs/analyze",
    headers={"Authorization": f"Bearer {token}"},
    json={"url": "https://company.com/job-posting"})

# Generate tailored CV
cv = requests.post("http://localhost:8000/api/generate/cv",
    headers={"Authorization": f"Bearer {token}"},
    json={"job_analysis_id": job.json()["id"], "format": "modern"})
```

### CLI Tool
```bash
# Quick end-to-end test with sample data
python cli.py quick-test

# Create a sample profile file
python cli.py create-sample my_profile.json

# Load your profile
python cli.py load-profile my_profile.json

# Analyze a job posting
python cli.py analyze-job --url "https://company.com/job"
python cli.py analyze-job --file sample_job_posting.txt

# Generate tailored CV
python cli.py generate-cv --style professional --output my_cv.md

# Generate professional bio
python cli.py generate-bio --context presentation --length medium --output bio.txt

# Check configuration status
python cli.py status
```

## Architecture

- **FastAPI**: Web framework and API endpoints
- **SQLAlchemy**: Database ORM with async support
- **Microsoft Agent Framework**: AI agent orchestration
- **GitHub Models**: Cost-effective AI model access
- **PostgreSQL/SQLite**: User data and knowledge storage

## Development

```bash
# Run tests
pytest

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Development server
uvicorn src.api.main:app --reload --port 8000
```

## License

MIT License - feel free to use for personal and commercial projects.