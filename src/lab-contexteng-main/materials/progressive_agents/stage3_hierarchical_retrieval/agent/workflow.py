"""
Main workflow builder and runner for the Course Q&A Agent.

Adapted from caching-agent to use CourseManager for course search.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from .edges import (
    initialize_edges,
    route_after_quality_evaluation,
)
from .nodes import (
    agent_node,
    classify_intent_node,
    evaluate_quality_node,
    handle_greeting_node,
    initialize_nodes,
    set_verbose,
)
from .state import WorkflowState, initialize_metrics
from .tools import initialize_tools

# Configure logger
logger = logging.getLogger("course-qa-workflow")


def create_workflow(course_manager, verbose: bool = True):
    """
    Create and compile the complete Course Q&A agent workflow.

    Args:
        course_manager: CourseManager instance for course search
        verbose: If True, show detailed logging. If False, suppress intermediate logs.

    Returns:
        Compiled LangGraph workflow
    """
    # Set verbose mode for nodes
    set_verbose(verbose)

    # Control logger level based on verbose flag
    if not verbose:
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.INFO)

    # Initialize all components
    initialize_nodes()
    initialize_edges()
    initialize_tools(course_manager)

    # Create workflow graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("handle_greeting", handle_greeting_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("evaluate_quality", evaluate_quality_node)

    # Set entry point
    workflow.set_entry_point("classify_intent")

    # Add routing function for intent classification
    def route_after_intent(state: WorkflowState) -> str:
        """Route based on query intent."""
        intent = state.get("query_intent", "GENERAL")

        if intent == "GREETING":
            return "handle_greeting"
        else:
            return "agent"  # Route to agent for all non-greeting queries

    # Add edges
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "handle_greeting": "handle_greeting",
            "agent": "agent",
        },
    )
    workflow.add_edge("handle_greeting", END)
    
    # Add quality evaluation loop: agent → evaluate_quality → conditional routing
    workflow.add_edge("agent", "evaluate_quality")
    workflow.add_conditional_edges(
        "evaluate_quality",
        route_after_quality_evaluation,
        {
            "agent": "agent",  # Loop back if quality is low
            "end": END,
        },
    )

    # Compile and return
    return workflow.compile()


def run_agent(agent, query: str, enable_caching: bool = False) -> Dict[str, Any]:
    """
    Run the Course Q&A agent on a query (synchronous wrapper).

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
    Run the Course Q&A agent on a query (async).

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
        "query_intent": None,
        "final_response": None,
        "quality_score": 0.0,
        "iteration_count": 0,
        "max_iterations": 2,
        "execution_path": [],
        "metrics": initialize_metrics(),
        "timestamp": datetime.now().isoformat(),
        "llm_calls": {},
    }

    logger.info("=" * 80)
    logger.info(f"🚀 Starting Course Q&A workflow for query: '{query[:50]}...'")

    try:
        # Execute the workflow (async)
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

        return final_state

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return {
            "original_query": query,
            "final_response": f"Error: {e}",
            "execution_path": ["failed"],
            "metrics": {"total_latency": (time.perf_counter() - start_time) * 1000},
        }
