"""
Course Q&A Agent - Stage 6 (Full Memory Agent)

A LangGraph-based agent for answering questions about courses with working memory and long-term memory for cross-session conversations. This is Stage 6 of the progressive learning path.
"""

from .nodes import get_memory_client
from .setup import cleanup_courses, initialize_course_manager, setup_agent
from .state import WorkflowMetrics, WorkflowState, initialize_metrics, initialize_state
from .tools import optimize_course_text, search_courses, transform_course_to_text, initialize_tools
from .workflow import create_workflow, run_agent, run_agent_async
from agent_memory_client.models import MemoryMessage, WorkingMemory

__all__ = [
    # State management
    "WorkflowState",
    "WorkflowMetrics",
    "initialize_metrics",
    "initialize_state",
    # Workflow
    "create_workflow",
    "run_agent",
    "run_agent_async",
    # Setup
    "setup_agent",
    "initialize_course_manager",
    "cleanup_courses",
    "initialize_tools",
    # Tools
    "search_courses",
    "transform_course_to_text",
    "optimize_course_text",
    # Memory
    "get_memory_client",
    "MemoryMessage",
    "WorkingMemory",
]

__version__ = "0.1.0"
