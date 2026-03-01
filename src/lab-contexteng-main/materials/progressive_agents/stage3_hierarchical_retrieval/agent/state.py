"""
Workflow state definitions for the Course Q&A Agent.

Adapted from the caching-agent for course-specific question answering.
"""

from typing import Dict, List, Optional, TypedDict


class WorkflowMetrics(TypedDict):
    """Metrics tracking for workflow performance analysis."""

    total_latency: float
    llm_calls: Dict[str, int]
    token_usage: Dict[str, int]  # Tracks input_tokens, output_tokens, total_tokens
    execution_path: str


class WorkflowState(TypedDict):
    """
    State for Course Q&A workflow with intent classification and quality evaluation.

    Tracks query processing, agent responses, and quality iteration.
    """

    # Core query management
    original_query: str
    final_response: Optional[str]

    # Query intent classification
    query_intent: Optional[
        str
    ]  # "GREETING", "GENERAL", "SYLLABUS_OBJECTIVES", "ASSIGNMENTS", "PREREQUISITES"

    # Quality evaluation and iteration control
    quality_score: float
    iteration_count: int
    max_iterations: int

    # Agent coordination
    execution_path: List[str]

    # Metrics and tracking
    metrics: WorkflowMetrics
    timestamp: str
    llm_calls: Dict[str, int]


def initialize_metrics() -> WorkflowMetrics:
    """Initialize a clean metrics structure with default values."""
    return {
        "total_latency": 0.0,
        "llm_calls": {},
        "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "execution_path": "",
    }
