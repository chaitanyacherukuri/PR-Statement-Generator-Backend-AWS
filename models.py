"""
Data models for the PR Statement Generator Backend Service.
"""

from typing import Literal, TypedDict
from pydantic import BaseModel, Field


class PRStatementRequest(BaseModel):
    """Request model for PR statement generation."""
    topic: str = Field(..., min_length=1, max_length=500, description="Topic for PR statement generation")


class PRStatementResponse(BaseModel):
    """Response model for PR statement generation."""
    pr_statement: str = Field(..., description="Generated PR statement")
    status: Literal["success", "error"] = Field(..., description="Status of the operation")
    message: str = Field(default="", description="Optional message or error details")


class State(TypedDict):
    """State dictionary that keeps track of information throughout the workflow."""
    pr_statement: str
    topic: str
    grade: str
    feedback: str


class Feedback(BaseModel):
    """Schema for structured output from the evaluator."""
    grade: Literal["good", "needs improvement"] = Field(
        description="Decide if the PR statement is well-formed or needs improvement."
    )
    feedback: str = Field(
        description="If the PR statement needs improvement, provide feedback on how to improve it."
    )


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service health status")
    message: str = Field(..., description="Health check message")
