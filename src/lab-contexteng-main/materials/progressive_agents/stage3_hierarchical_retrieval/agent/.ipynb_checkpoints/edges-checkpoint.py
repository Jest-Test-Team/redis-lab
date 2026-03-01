"""
Workflow edges and routing logic for the Course Q&A Agent.

Adapted from caching-agent with minimal changes for course Q&A routing.
"""

import logging
from typing import Any, Dict, Literal

# Configure logger
logger = logging.getLogger("course-qa-workflow")

# NOTE: Semantic cache initialization commented out for now
# Global cache variable
# cache = None


def initialize_edges():
    """Initialize edges with required dependencies."""
    # NOTE: Semantic cache initialization commented out
    # global cache
    # cache = semantic_cache
    pass


def route_after_quality_evaluation(
    state: Dict[str, Any],
) -> Literal["agent", "end"]:
    """
    Route after quality evaluation based on response quality score.

    Returns:
        "agent" if answer needs improvement and hasn't exceeded max iterations
        "end" if answer is adequate or max iterations reached
    """
    quality_score = state.get("quality_score", 0.0)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 2)

    if quality_score < 0.7 and iteration_count < max_iterations:
        logger.info(
            f"🔄 Quality score {quality_score:.2f} below threshold. Iteration {iteration_count + 1}/{max_iterations}. Routing back to agent."
        )
        return "agent"
    else:
        if quality_score >= 0.7:
            logger.info(f"✅ Quality score {quality_score:.2f} adequate. Routing to end.")
        else:
            logger.info(f"⚠️ Max iterations ({max_iterations}) reached. Routing to end.")
        return "end"
