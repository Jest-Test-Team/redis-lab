"""
Workflow state definitions for the Stage 4 ReAct Course Q&A Agent.

Extends Stage 4 state with ReAct-specific fields.
"""

from typing import Any, Dict, List, Optional, TypedDict


class WorkflowMetrics(TypedDict):
    """Metrics tracking for workflow performance analysis."""

    total_latency: float
    decomposition_latency: float
    cache_latency: float
    research_latency: float
    synthesis_latency: float
    cache_hit_rate: float
    cache_hits_count: int
    questions_researched: int
    total_research_iterations: int
    llm_calls: Dict[str, int]
    sub_question_count: int
    execution_path: str


class WorkflowState(TypedDict):
    """
    State for Stage 4 ReAct Course Q&A workflow.

    Combines hybrid search with NER and ReAct reasoning loop.
    """

    # Core query management
    original_query: str
    sub_questions: List[str]
    sub_answers: Dict[str, str]
    final_response: Optional[str]

    # Query intent classification
    query_intent: Optional[str]  # "GREETING", "GENERAL", "SYLLABUS_OBJECTIVES", etc.

    # Named Entity Recognition (NER) - from Stage 4
    extracted_entities: Optional[Dict[str, Any]]
    search_strategy: Optional[str]  # "exact_match", "hybrid", "semantic_only"

    # Hybrid search results - from Stage 4
    exact_matches: Optional[List[str]]
    metadata_filters: Optional[Dict[str, Any]]

    # ReAct-specific fields
    reasoning_trace: List[Dict[str, Any]]  # Thought/Action/Observation history
    react_iterations: int  # Number of ReAct loop iterations

    # Cache management (disabled for now)
    cache_hits: Dict[str, bool]
    cache_confidences: Dict[str, float]
    cache_enabled: bool

    # Research iteration and quality control
    research_iterations: Dict[str, int]
    max_research_iterations: int
    research_quality_scores: Dict[str, float]
    research_feedback: Dict[str, str]
    current_research_strategy: Dict[str, str]

    # Agent coordination
    execution_path: List[str]
    active_sub_question: Optional[str]

    # Metrics and tracking
    metrics: WorkflowMetrics
    timestamp: str
    comparison_mode: bool
    llm_calls: Dict[str, int]


def initialize_metrics() -> WorkflowMetrics:
    """Initialize a clean metrics structure with default values."""
    return {
        "total_latency": 0.0,
        "decomposition_latency": 0.0,
        "cache_latency": 0.0,
        "research_latency": 0.0,
        "synthesis_latency": 0.0,
        "cache_hit_rate": 0.0,
        "cache_hits_count": 0,
        "questions_researched": 0,
        "total_research_iterations": 0,
        "llm_calls": {},
        "sub_question_count": 0,
        "execution_path": "",
    }

