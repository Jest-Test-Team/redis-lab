"""
Main workflow builder and runner for the Stage 4 ReAct Course Q&A Agent.

Implements ReAct (Reasoning + Acting) loop with hybrid search.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from .react_agent import react_agent_node, set_verbose
from .state import WorkflowState, initialize_metrics
from .tools import initialize_tools

# Configure logger
logger = logging.getLogger("course-qa-workflow")


def create_workflow(course_manager, verbose: bool = True):
    """
    Create and compile the Stage 4 ReAct Course Q&A agent workflow.

    Args:
        course_manager: CourseManager instance for course search
        verbose: If True, show detailed logging. If False, suppress intermediate logs.

    Returns:
        Compiled LangGraph workflow
    """
    # Set verbose mode for react agent
    set_verbose(verbose)

    # Control logger level based on verbose flag
    if not verbose:
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.INFO)

    # Initialize tools
    initialize_tools(course_manager)

    # Create workflow graph
    workflow = StateGraph(WorkflowState)

    # Add ReAct agent node
    workflow.add_node("react_agent", react_agent_node)

    # Set entry point
    workflow.set_entry_point("react_agent")

    # Add edge to end
    workflow.add_edge("react_agent", END)

    # Compile and return
    return workflow.compile()


def run_agent(agent, query: str, enable_caching: bool = False) -> Dict[str, Any]:
    """
    Run the Stage 4 ReAct Course Q&A agent on a query (synchronous).

    Args:
        agent: Compiled LangGraph workflow
        query: User query about courses
        enable_caching: Whether to use semantic caching (currently disabled)

    Returns:
        Dictionary with results and metrics
    """
    import asyncio
    return asyncio.run(run_agent_async(agent, query, enable_caching))


async def run_agent_async(
    agent, query: str, enable_caching: bool = False
) -> Dict[str, Any]:
    """
    Run the Stage 4 ReAct Course Q&A agent on a query (async).

    Args:
        agent: Compiled LangGraph workflow
        query: User query about courses
        enable_caching: Whether to use semantic caching (currently disabled)

    Returns:
        Dictionary with results and metrics
    """
    start_time = time.perf_counter()

    # Initialize state for the workflow
    initial_state: WorkflowState = {
        "original_query": query,
        "sub_questions": [],
        "sub_answers": {},
        "query_intent": None,
        "extracted_entities": None,
        "search_strategy": None,
        "exact_matches": None,
        "metadata_filters": None,
        # ReAct-specific fields
        "reasoning_trace": [],
        "react_iterations": 0,
        # Cache (disabled)
        "cache_hits": {},
        "cache_confidences": {},
        "cache_enabled": enable_caching,
        # Research
        "research_iterations": {},
        "max_research_iterations": 2,
        "research_quality_scores": {},
        "research_feedback": {},
        "current_research_strategy": {},
        # Output
        "final_response": None,
        "execution_path": [],
        "active_sub_question": None,
        "metrics": initialize_metrics(),
        "timestamp": datetime.now().isoformat(),
        "comparison_mode": False,
        "llm_calls": {},
    }

    logger.info("=" * 80)
    logger.info(f"🚀 Starting Stage 4 ReAct workflow for query: '{query[:50]}...'")

    try:
        # Execute the workflow
        final_state = await agent.ainvoke(initial_state)

        # Calculate final metrics
        total_time = (time.perf_counter() - start_time) * 1000
        final_state["metrics"]["total_latency"] = total_time

        # Create execution path string
        execution_path = " → ".join(final_state["execution_path"])
        final_state["metrics"]["execution_path"] = execution_path

        logger.info("=" * 80)
        logger.info(f"✅ Workflow completed in {total_time:.2f}ms")
        logger.info(f"📊 Execution path: {execution_path}")
        logger.info(f"🔄 ReAct iterations: {final_state.get('react_iterations', 0)}")

        return final_state

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return {
            "original_query": query,
            "final_response": f"Error: {e}",
            "execution_path": ["failed"],
            "metrics": {"total_latency": (time.perf_counter() - start_time) * 1000},
            "reasoning_trace": [],
            "react_iterations": 0,
        }

