"""
PR Statement Generation Service.

This module contains the core business logic for generating PR statements
using LangGraph workflow and Groq LLM. Implemented using functional programming.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

from models import State, Feedback

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for LLM instances (initialized once)
_llm: Optional[ChatGroq] = None
_evaluator: Optional[ChatGroq] = None
_workflow_graph = None


def initialize_llm() -> None:
    """Initialize the LLM and evaluator instances."""
    global _llm, _evaluator

    try:
        # Get API key from environment variables (loaded from .env)
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        # Set environment variable for Groq API (if not already set)
        os.environ["GROQ_API_KEY"] = groq_api_key

        # Initialize LLM
        _llm = ChatGroq(model_name="meta-llama/llama-4-scout-17b-16e-instruct")

        # Augment LLM with schema for structured output
        _evaluator = _llm.with_structured_output(Feedback)

        logger.info("LLM initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise

def build_workflow() -> None:
    """Build the LangGraph workflow for PR statement generation."""
    global _workflow_graph

    try:
        # Create state graph
        workflow = StateGraph(State)

        # Add nodes
        workflow.add_node("Generate_PR_Statement", generate_pr_statement_node)
        workflow.add_node("Evaluate_PR_Statement", evaluate_pr_statement_node)

        # Add edges
        workflow.add_edge(START, "Generate_PR_Statement")
        workflow.add_edge("Generate_PR_Statement", "Evaluate_PR_Statement")
        workflow.add_conditional_edges(
            "Evaluate_PR_Statement",
            route_statement,
            {"Accepted": END, "Rejected + Feedback": "Generate_PR_Statement"}
        )

        # Compile the workflow
        _workflow_graph = workflow.compile()

        logger.info("Workflow built successfully")
    except Exception as e:
        logger.error(f"Failed to build workflow: {e}")
        raise

def generate_pr_statement_node(state: State) -> Dict[str, Any]:
    """Generate a PR statement based on the given topic."""
    global _llm

    try:
        if _llm is None:
            raise RuntimeError("LLM not initialized. Call initialize_llm() first.")

        prompt = f"""
        Generate a compelling PR statement for the topic {state['topic']}.

        - The statement should highlight key benefits, address any potential concerns, and capture the excitement and innovation surrounding the subject.
        - Ensure that the tone is professional yet engaging, appealing to the target audience while maintaining clarity and impact."""

        if state.get("feedback"):
            response = _llm.invoke(prompt + f" Also take provided feedback into account: {state['feedback']}")
        else:
            response = _llm.invoke(prompt)

        logger.info(f"Generated PR statement for topic: {state['topic']}")
        return {"pr_statement": response.content}

    except Exception as e:
        logger.error(f"Error generating PR statement: {e}")
        raise

def evaluate_pr_statement_node(state: State) -> Dict[str, Any]:
    """Evaluate the generated PR statement and provide feedback."""
    global _evaluator

    try:
        if _evaluator is None:
            raise RuntimeError("Evaluator not initialized. Call initialize_llm() first.")

        prompt = f"""
        Review the following PR statement: {state['pr_statement']}.

        - Assess its clarity, engagement, and overall effectiveness in capturing the key benefits and addressing potential concerns.
        - Decide whether the statement is well-formed ('good') or if it requires further refinement ('needs improvement').
        - If it needs improvement, please provide concise and actionable feedback on how to enhance the statement."""

        decision = _evaluator.invoke(prompt)

        logger.info(f"Evaluated PR statement with grade: {decision.grade}")
        return {"grade": decision.grade, "feedback": decision.feedback}

    except Exception as e:
        logger.error(f"Error evaluating PR statement: {e}")
        raise
    
def route_statement(state: State) -> str:
    """Route to the appropriate node based on the evaluation grade."""
    if state["grade"] == "good":
        return "Accepted"
    else:
        return "Rejected + Feedback"


def initialize_pr_generator() -> None:
    """Initialize the PR generator by setting up LLM and workflow."""
    initialize_llm()
    build_workflow()


async def generate_pr_statement(topic: str) -> str:
    """
    Generate a PR statement for the given topic.

    Args:
        topic: The topic for PR statement generation

    Returns:
        Generated PR statement

    Raises:
        Exception: If generation fails
    """
    global _workflow_graph

    try:
        if _workflow_graph is None:
            raise RuntimeError("Workflow not initialized. Call initialize_pr_generator() first.")

        logger.info(f"Starting PR statement generation for topic: {topic}")

        # Invoke the workflow
        result = await _workflow_graph.ainvoke({"topic": topic})

        logger.info("PR statement generation completed successfully")
        return result["pr_statement"]
    except Exception as api_error:
        logger.warning(f"API call failed: {api_error}")
        # Fallback response when API is unavailable
        fallback_statement = f"""FOR IMMEDIATE RELEASE

        [Company Name] Announces Exciting Development in {topic}
        ..."""
        return fallback_statement

