"""
Workflow builder for Stage 1 Baseline RAG Agent.

This is a 2-node workflow:
1. Research (semantic search with raw context)
2. Synthesize (LLM answer generation)

"""

import logging

from langgraph.graph import END, START, StateGraph

from .nodes import research_node, synthesize_node, set_verbose
from .state import AgentState

logger = logging.getLogger("stage1-baseline")


def create_workflow(verbose: bool = True) -> StateGraph:
    """
    Create a simple 2-node RAG workflow.

    Args:
        verbose: If True, show detailed logging. If False, suppress intermediate logs.

    Workflow:
    START → research → synthesize → END

    Returns:
        Compiled LangGraph workflow
    """
    # Set verbose mode for nodes
    set_verbose(verbose)

    # Control logger level based on verbose flag
    if not verbose:
        logging.getLogger("stage1-baseline").setLevel(logging.CRITICAL)
    else:
        logging.getLogger("stage1-baseline").setLevel(logging.INFO)

    logger.info("🏗️  Building Stage 1 Baseline RAG workflow...")

    # Create state graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("synthesize", synthesize_node)

    # Define edges (linear flow)
    workflow.add_edge(START, "research")
    workflow.add_edge("research", "synthesize")
    workflow.add_edge("synthesize", END)

    # Compile
    app = workflow.compile()

    logger.info("✅ Workflow created successfully")
    logger.info("📊 Workflow: START → research → synthesize → END")

    return app