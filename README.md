# PR Statement Generator - Backend Service

A FastAPI-based backend service for generating compelling PR statements using AI-powered workflows.

## Overview

This backend service provides RESTful API endpoints for automated PR statement generation using:
- **FastAPI** for the web framework and automatic API documentation
- **LangGraph** for AI workflow orchestration with iterative refinement
- **Groq** for LLM services (Meta Llama 4 Scout 17B model)
- **Pydantic** for data validation and serialization
- **python-dotenv** for environment variable management
- **Docker** support for containerized deployment

**Architecture:** The service uses a **functional programming approach** with standalone functions instead of class-based architecture, making the codebase simpler, more maintainable, and easier to test.

## Features

- **RESTful API** with automatic OpenAPI/Swagger documentation
- **AI-Powered Workflow** using LangGraph for iterative PR statement refinement
- **Quality Assurance** with built-in evaluation and feedback loops
- **Input Validation** and sanitization using Pydantic models
- **Comprehensive Error Handling** with appropriate HTTP status codes
- **CORS Support** configured for cross-origin requests
- **Health Monitoring** with dedicated health check endpoint
- **Structured Logging** for debugging and monitoring
- **Docker Support** for easy deployment and scaling
- **Fallback Mechanism** when external APIs are unavailable
- **Async Support** for high-performance concurrent request handling

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

### Generate PR Statement
```
POST /api/generate-pr-statement
Content-Type: application/json

{
  "topic": "Your topic here"
}
```

**Response:**
```json
{
  "pr_statement": "Generated PR statement content",
  "status": "success",
  "message": "PR statement generated successfully"
}
```

### API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- Git
- Groq API key (sign up at [Groq Console](https://console.groq.com/))

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/chaitanyacherukuri/PR-Statement-Generator-Backend-AWS.git
   cd PR-Statement-Generator-Backend-AWS
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Create .env file in the root directory
   echo "GROQ_API_KEY=your-groq-api-key-here" > .env
   ```

   Replace `your-groq-api-key-here` with your actual Groq API key.

   **Note:** The application automatically loads environment variables from the `.env` file using `python-dotenv`. No need to manually export variables!

## Running the Service

### Local Development
```bash
# Make sure virtual environment is activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using Docker
```bash
# Build the Docker image
docker build -t pr-statement-generator .

# Run the container
docker run -p 8000:8000 --env-file .env pr-statement-generator
```

The service will be available at:
- **API:** http://localhost:8000
- **Interactive Documentation:** http://localhost:8000/docs
- **Alternative Documentation:** http://localhost:8000/redoc

## Configuration

### Environment Variables
The application uses a `.env` file for configuration:
- `GROQ_API_KEY`: **Required.** Your Groq API key for LLM services.

### CORS Configuration
The service is configured to accept requests from:
- http://localhost:8501 (Streamlit default)
- http://127.0.0.1:8501

You can modify CORS settings in `main.py` if needed for your specific frontend application.

## Project Structure

```
PR-Statement-Generator-Backend-AWS/
├── main.py                 # FastAPI application entry point
├── models.py              # Pydantic models for request/response
├── services/
│   ├── __init__.py
│   └── pr_generator.py    # Core PR generation logic
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api_endpoints.py
│   ├── test_integration.py
│   └── test_models.py
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── pytest.ini           # Pytest configuration
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ API Routes  │  │ Middleware  │  │ Error Handling  │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                 PR Generator Service                    │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              LangGraph Workflow                     │ │
│  │  ┌─────────────┐    ┌─────────────────────────────┐ │ │
│  │  │  Generate   │───▶│      Evaluate & Route      │ │ │
│  │  │ PR Statement│    │                             │ │ │
│  │  └─────────────┘    └─────────────────────────────┘ │ │
│  │         │                        │                  │ │
│  │         └────────────────────────┘                  │ │
│  │              (Feedback Loop)                        │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    Groq LLM (Llama 4)                  │
└─────────────────────────────────────────────────────────┘
```

## Error Handling

The service implements comprehensive error handling:
- **400 Bad Request:** Invalid input data
- **500 Internal Server Error:** Service errors
- **503 Service Unavailable:** Service initialization failures

## Logging

The service uses Python's built-in logging module with INFO level by default. Logs include:
- Request processing information
- Error details and stack traces
- Service initialization status

## Testing

### Manual Testing
Test the API using curl:
```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Generate PR statement
curl -X POST "http://localhost:8000/api/generate-pr-statement" \
     -H "Content-Type: application/json" \
     -d '{"topic": "AI-powered chatbot launch"}'
```

### Running Unit Tests
```bash
# Make sure virtual environment is activated
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api_endpoints.py -v
```

## Dependencies

### Core Dependencies
- **FastAPI** (0.115.14): Modern web framework for building APIs
- **Uvicorn** (0.35.0): ASGI server for running FastAPI
- **Pydantic** (2.11.7): Data validation using Python type annotations
- **LangChain** (0.3.26): Framework for developing LLM applications
- **LangGraph** (0.5.1): Library for building stateful, multi-actor applications
- **Groq** (0.3.5): Client for Groq's LLM API
- **python-dotenv** (1.1.1): Load environment variables from .env file

### Development Dependencies
- **pytest** (8.4.1): Testing framework
- **pytest-asyncio** (1.0.0): Async support for pytest
- **httpx** (0.28.1): HTTP client for testing

See `requirements.txt` for the complete list with exact versions.

## Deployment

### AWS Deployment
This project is designed for AWS deployment. You can deploy using:

1. **AWS Lambda + API Gateway** (serverless)
2. **AWS ECS** (containerized)
3. **AWS EC2** (traditional server)

### Environment Variables for Production
```bash
GROQ_API_KEY=your-production-groq-api-key
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainer.

## Changelog

### v1.0.0
- Initial release
- FastAPI backend with LangGraph workflow
- Groq LLM integration
- Docker support
- Comprehensive test suite
