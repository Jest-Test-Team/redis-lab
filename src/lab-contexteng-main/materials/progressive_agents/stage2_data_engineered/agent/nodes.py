"""
Workflow nodes for Stage 2 Data Engineered Agent.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional

import nest_asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)

from redis_context_course import CourseManager
from redis_context_course.hierarchical_models import HierarchicalCourse

from .data_engineering import format_courses_for_llm
from .state import AgentState

# Configure logger
logger = logging.getLogger("stage2-engineered")

course_manager: Optional[CourseManager] = None
hierarchical_courses = []

# Verbose mode flag
_verbose = True

SYSTEM_INSTRUCTIONS = (
    "You are a helpful course advisor assistant. "
    "Answer questions using only the course information provided."
)

def set_verbose(verbose: bool):
    """Set the verbose mode for logging."""
    global _verbose
    _verbose = verbose

def initialize_nodes(manager: CourseManager):
    """
    Initialize nodes with required dependencies.

    Args:
        manager: CourseManager instance for course search
    """
    global course_manager, hierarchical_courses
    course_manager = manager

    # Load hierarchical courses
    try:
        data_path = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "redis_context_course"
            / "data"
            / "hierarchical"
            / "hierarchical_courses.json"
        )
        if data_path.exists():
            with open(data_path) as f:
                data = json.load(f)
                hierarchical_courses = [
                    HierarchicalCourse(**course_data) for course_data in data["courses"]
                ]
            logger.info(f"Loaded {len(hierarchical_courses)} hierarchical courses")
        else:
            logger.warning(f"Hierarchical courses not found at {data_path}")
    except Exception as e:
        logger.error(f"Failed to load hierarchical courses: {e}")


def research_node(state: AgentState) -> AgentState:
    """
    Research node - performs a semantic search and returns data engineered context.
    """
    start_time = time.perf_counter()
    query = state["query"]

    logger.info(f"🔍 Searching for courses: '{query[:50]}...'")

    try:
        # Allow nested event loops
        nest_asyncio.apply()

        # Get event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Semantic search (same as Stage 1)
        basic_courses = loop.run_until_complete(
            course_manager.search_courses(
                query=query, limit=5, similarity_threshold=0.5
            )
        )

        logger.info(f"✅ Found {len(basic_courses)} courses")

        if not basic_courses:
            state["engineered_context"] = "No courses found."
            state["courses_found"] = 0
            return state

        # Use the existing format_courses_for_llm function
        engineered_context = format_courses_for_llm(
            basic_courses,
            use_compact=False,  # Use full format for better quality
        )

        # Calculate approximate token count (rough estimate: 1 token ≈ 4 chars)
        token_estimate = len(engineered_context) // 4

        logger.info(
            f"📊 Engineered context: {len(engineered_context)} chars (~{token_estimate} tokens)"
        )
        logger.info("✅ data engineering applied:")
        logger.info("   - Cleaned: Removed noise fields (id, timestamps, enrollment)")
        logger.info("   - Transformed: JSON → natural text format")
        state["engineered_context"] = engineered_context
        state["courses_found"] = len(basic_courses)
        state["total_tokens"] = token_estimate

        research_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"🔬 Research complete in {research_time:.2f}ms")

        return state

    except Exception as e:
        logger.error(f"Research failed: {e}")
        import traceback

        traceback.print_exc()
        state["engineered_context"] = f"Search failed: {str(e)}"
        state["courses_found"] = 0
        return state



def synthesize_node(state: AgentState) -> AgentState:
    """
    Synthesis node - uses LLM to answer the question based on engineered context.

    The LLM receives clean, well-formatted context that's easy to parse.
    Students will see better answers with fewer tokens compared to Stage 1.
    """
    
    start_time = time.perf_counter()
    query = state["query"]
    context = state["engineered_context"]

    logger.info("🔗 Synthesizing answer from engineered context...")

    try:
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # We follow the same structure as the "Crafting effective
        # system prompts" notebook: a SystemMessage for the
        # persistent instructions plus a HumanMessage for the
        # concrete user request and retrieved context.
        messages = [
            SystemMessage(content=SYSTEM_INSTRUCTIONS),
            HumanMessage(
                content=(
                    "Course Information (context engineered data):\n"
                    f"{context}\n\n"
                    f"Student Question: {query}\n\n"
                    "Please provide a clear, helpful answer based on the course information above."
                )
            ),
        ]

        # Get LLM response
        response = llm.invoke(messages)
        answer = response.content

        synthesis_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"🔗 Synthesis complete in {synthesis_time:.2f}ms")
        # logger.info(f"📝 Answer: {answer[:3000]}...")

        state["final_answer"] = answer

        return state

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        import traceback

        traceback.print_exc()
        state["final_answer"] = f"Failed to generate answer: {str(e)}"
        return state