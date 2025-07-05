"""
FastAPI Backend Service for PR Statement Generator.

This service provides RESTful API endpoints for generating PR statements
using LangGraph workflow and Groq LLM.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import PRStatementRequest, PRStatementResponse, HealthResponse
from services.pr_generator import initialize_pr_generator, generate_pr_statement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global initialization flag
_pr_generator_initialized = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _pr_generator_initialized

    # Startup
    try:
        # Initialize the PR generator (loads .env automatically)
        initialize_pr_generator()
        _pr_generator_initialized = True
        logger.info("PR Generator Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down PR Generator Service")


# Create FastAPI application
app = FastAPI(
    title="PR Statement Generator API",
    description="RESTful API for generating compelling PR statements using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "pr_statement": "",
            "status": "error",
            "message": "Internal server error occurred"
        }
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="PR Statement Generator API is running"
    )


@app.post("/api/generate-pr-statement", response_model=PRStatementResponse)
async def generate_pr_statement_endpoint(request: PRStatementRequest):
    """
    Generate a PR statement for the given topic.
    
    Args:
        request: PR statement generation request containing the topic
        
    Returns:
        Generated PR statement with status information
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        logger.info(f"Received PR statement generation request for topic: {request.topic}")

        # Validate service is available
        if not _pr_generator_initialized:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PR Generator Service is not available"
            )

        # Generate PR statement using functional approach
        pr_statement = await generate_pr_statement(request.topic)
        
        logger.info("PR statement generated successfully")
        
        return PRStatementResponse(
            pr_statement=pr_statement,
            status="success",
            message="PR statement generated successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PR statement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PR statement: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PR Statement Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
