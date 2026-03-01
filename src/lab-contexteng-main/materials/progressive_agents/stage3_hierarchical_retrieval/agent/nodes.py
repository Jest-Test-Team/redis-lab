"""
Workflow nodes for the Course Q&A Agent.

Stage 3: Agentic workflow with LLM-controlled tool calling.
"""

import logging
import time

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

from .state import WorkflowState
from .tools import search_courses_sync, search_courses_tool

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Configure logger
logger = logging.getLogger("course-qa-workflow")

# Global cache variable - COMMENTED OUT FOR NOW
# Will be added in future stages
# semantic_cache = None

# Global LLMs
_analysis_llm = None
_research_llm = None
_agent_llm = None  # NEW: LLM for agent node

# Global function for intent classification (injectable from notebook)
_classify_intent_func = None

# Global tool for search (injectable from notebook)
_search_tool = search_courses_tool

# Global function for quality evaluation (injectable from notebook)
_evaluate_quality_func = None

# Verbose flag for controlling logging output
_verbose = True


def set_verbose(verbose: bool):
    """Set the verbose flag for controlling logging output."""
    global _verbose
    _verbose = verbose


def set_classify_intent_function(func):
    """Set a custom intent classification function (for educational use)."""
    global _classify_intent_func
    _classify_intent_func = func


def set_search_tool(tool):
    """Set a custom search tool (for educational use)."""
    global _search_tool, _agent_llm
    _search_tool = tool
    # Reset agent LLM so it gets rebuilt with the new tool
    _agent_llm = None


def set_evaluate_quality_function(func):
    """Set a custom quality evaluation function (for educational use)."""
    global _evaluate_quality_func
    _evaluate_quality_func = func


def initialize_nodes():
    """Initialize the nodes with required dependencies."""
    # NOTE: Semantic cache initialization commented out
    # global semantic_cache
    # semantic_cache = cache
    pass


def get_analysis_llm():
    """Get the configured analysis LLM instance."""
    global _analysis_llm
    if _analysis_llm is None:
        _analysis_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=800,
            timeout=30,
            max_retries=2
        )
    return _analysis_llm


def get_research_llm():
    """Get the configured research LLM instance."""
    global _research_llm
    if _research_llm is None:
        _research_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=3000,
            timeout=30,
            max_retries=2
        )
    return _research_llm


def get_agent_llm():
    """Get the configured agent LLM instance with tool binding."""
    global _agent_llm, _search_tool
    if _agent_llm is None:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000,
            timeout=30,
            max_retries=2
        )
        # Bind the search_courses tool
        # Use the injected tool if available, otherwise use default
        tool_to_use = _search_tool if _search_tool else search_courses_tool
        _agent_llm = llm.bind_tools([tool_to_use])
    return _agent_llm


async def classify_intent_node(state: WorkflowState) -> WorkflowState:
    """Classify query intent and determine appropriate detail level."""
    query = state["original_query"]
    
    # Reset state for new run (since this is the entry point)
    # This prevents state leakage from previous runs
    state["execution_path"] = []
    state["llm_calls"] = {}
    state["metrics"] = {
        "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        "total_latency": 0.0,
        "llm_calls": {},
        "execution_path": ""
    }

    logger.info(f"🎯 Classifying intent for: '{query[:50]}...'")

    try:
        # Use injected function if provided (for educational exercises)
        if _classify_intent_func is not None:
            intent = await _classify_intent_func(query)
            logger.info(f"🎯 Intent: {intent}")
            
            # Track LLM usage
            llm_calls = state.get("llm_calls", {}).copy()
            llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1
            
            return {
                **state,
                "query_intent": intent,
                "llm_calls": llm_calls,
            }
        
        # Default implementation
        intent_prompt = f"""You are a query intent classifier for a course information system.

TASK: Analyze the query and return ONLY the most appropriate intent category.

Query: {query}

INTENT CATEGORIES:

1. GREETING
   - Greetings, acknowledgments, pleasantries
   - Examples: "hello", "hi there", "thank you", "thanks"

2. GENERAL
   - Broad course information requests
   - Course descriptions and overviews
   - "What is [course]?" questions
   - Example: "What is CS002?"

3. SYLLABUS_OBJECTIVES
   - Syllabus requests
   - Course structure and topics covered
   - Learning objectives and outcomes
   - Examples: "Show me the syllabus for CS002", "What will I learn?", "What topics are covered?", "Give me details about this course"

4. ASSIGNMENTS
   - Homework, projects, exams
   - Assessment types and workload
   - Grading information
   - Examples: "What are the assignments?", "How many exams?", "What's the workload?"

5. PREREQUISITES
   - Course requirements
   - Prior knowledge needed
   - Examples: "What are the prerequisites?", "What do I need before taking this?"

CLASSIFICATION RULES:
- Choose the MOST SPECIFIC category that matches
- If multiple categories apply, prioritize based on the primary intent
- Default to GENERAL for ambiguous queries
- Ignore filler words and focus on core intent

OUTPUT FORMAT (respond with exactly this structure):
INTENT: <category_name>
"""

        response = await get_analysis_llm().ainvoke([HumanMessage(content=intent_prompt)])

        # Track LLM usage
        llm_calls = state.get("llm_calls", {}).copy()
        llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1
        
        # Track token usage
        metrics = state.get("metrics", {}).copy()
        token_usage = metrics.get("token_usage", {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}).copy()
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            token_usage["input_tokens"] += response.usage_metadata.get("input_tokens", 0)
            token_usage["output_tokens"] += response.usage_metadata.get("output_tokens", 0)
            token_usage["total_tokens"] += response.usage_metadata.get("total_tokens", 0)
        metrics["token_usage"] = token_usage

        # Parse response
        response_content = response.content.strip()
        intent = "GENERAL"

        for line in response_content.split("\n"):
            if line.startswith("INTENT:"):
                intent = line.split(":", 1)[1].strip()

        logger.info(f"🎯 Intent: {intent}")

        return {
            **state,
            "query_intent": intent,
            "llm_calls": llm_calls,
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"❌ Intent classification failed: {e}")
        # Default to safe values
        return {
            **state,
            "query_intent": "GENERAL_QUESTION",
            "detail_level": "summary",
        }


async def evaluate_quality_node(state: WorkflowState) -> WorkflowState:
    """Evaluate the quality of the agent's response."""
    start_time = time.perf_counter()
    query = state["original_query"]
    answer = state.get("final_response", "")

    logger.info("🎯 Quality Evaluation: Evaluating response quality")

    # Track LLM usage
    llm_calls = state.get("llm_calls", {}).copy()

    try:
        # Use custom evaluation function if provided (for educational use)
        if _evaluate_quality_func is not None:
            score, reasoning = await _evaluate_quality_func(query, answer)
            llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1
        else:
            # Default evaluation logic
            evaluation_prompt = f"""Evaluate the quality of this course search answer on a scale of 0.0 to 1.0.

Question: {query}
Answer: {answer}

Criteria:
- Completeness: Does it fully answer the question?
- Accuracy: Is the course information correct and relevant?
- Relevance: Does it directly address what was asked?
- Grounding: Does it provide specific course details and stick to facts?

Respond with ONLY a number between 0.0 and 1.0 (e.g., 0.85)
"""

            response = await get_analysis_llm().ainvoke(
                [HumanMessage(content=evaluation_prompt)]
            )
            llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1
            
            # Track token usage
            metrics = state.get("metrics", {}).copy()
            token_usage = metrics.get("token_usage", {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}).copy()
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                token_usage["input_tokens"] += response.usage_metadata.get("input_tokens", 0)
                token_usage["output_tokens"] += response.usage_metadata.get("output_tokens", 0)
                token_usage["total_tokens"] += response.usage_metadata.get("total_tokens", 0)
            metrics["token_usage"] = token_usage

            try:
                score = float(response.content.strip())
                score = max(0.0, min(1.0, score))
            except ValueError:
                score = 0.8

        if score < 0.7:
            logger.info(f"   📊 Score: {score:.2f} - Needs improvement")
        else:
            logger.info(f"   ✅ Score: {score:.2f} - Adequate")

        # Update state
        evaluation_time = (time.perf_counter() - start_time) * 1000
        iteration_count = state.get("iteration_count", 0) + 1

        logger.info(f"🎯 Quality evaluation complete in {evaluation_time:.2f}ms")

        return {
            **state,
            "quality_score": score,
            "iteration_count": iteration_count,
            "llm_calls": llm_calls,
            "metrics": metrics,
            "execution_path": state.get("execution_path", []) + ["quality_evaluated"],
        }

    except Exception as e:
        logger.error(f"Quality evaluation failed: {e}")
        return {
            **state,
            "quality_score": 0.8,
            "iteration_count": state.get("iteration_count", 0) + 1,
            "execution_path": state.get("execution_path", []) + ["quality_evaluation_failed"],
        }


async def handle_greeting_node(state: WorkflowState) -> WorkflowState:
    """Handle greetings and non-course queries without course search."""
    start_time = time.perf_counter()
    query = state["original_query"]

    logger.info(f"👋 Handling greeting/non-course query: '{query[:50]}...'")

    try:
        greeting_prompt = f"""
        The user sent this message: {query}

        Respond naturally and helpfully. If it's a greeting, greet them back and let them know you're a course advisor agent that can help them find courses, view syllabi, check prerequisites, etc.

        Keep it brief and friendly (2-3 sentences max).
        """

        response = await get_analysis_llm().ainvoke([HumanMessage(content=greeting_prompt)])

        # Track LLM usage
        llm_calls = state.get("llm_calls", {}).copy()
        llm_calls["analysis_llm"] = llm_calls.get("analysis_llm", 0) + 1
        
        # Track token usage
        metrics = state.get("metrics", {}).copy()
        token_usage = metrics.get("token_usage", {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}).copy()
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            token_usage["input_tokens"] += response.usage_metadata.get("input_tokens", 0)
            token_usage["output_tokens"] += response.usage_metadata.get("output_tokens", 0)
            token_usage["total_tokens"] += response.usage_metadata.get("total_tokens", 0)
        metrics["token_usage"] = token_usage

        final_response = response.content.strip()

        logger.info(f"👋 Greeting response: {final_response[:100]}...")

        latency = (time.perf_counter() - start_time) * 1000
        metrics["total_latency"] = latency

        return {
            **state,
            "final_response": final_response,
            "llm_calls": llm_calls,
            "execution_path": state.get("execution_path", []) + ["greeting_handled"],
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"❌ Greeting handling failed: {e}")
        return {
            **state,
            "final_response": "Hello! I'm a course advisor agent. I can help you find courses, view syllabi, check prerequisites, and more. What would you like to know?",
            "execution_path": state.get("execution_path", []) + ["greeting_failed"],
        }


# ============================================================================
# NEW: Agent Node with Tool Calling
# ============================================================================


async def agent_node(state: WorkflowState) -> WorkflowState:
    """
    Agent node that uses LLM with tool calling to answer questions.

    This replaces the scripted research → evaluate → synthesize pipeline
    with an agentic approach where the LLM decides:
    - When to search for courses
    - What parameters to use (intent, strategy, entities)
    - How to formulate the final answer
    """
    start_time = time.perf_counter()

    query = state["original_query"]

    logger.info(f"🤖 Agent: Processing query with tool calling")

    try:
        # Build messages
        messages = []

        # Add system message with instructions
        system_prompt = """You are a helpful course advisor assistant. Your job is to help students find and learn about courses.

You have access to a search_courses tool that can search the course catalog. Use this tool to find relevant courses to answer the user's question.

When using the search_courses tool, you need to determine the **intent** - what type of information does the user want?

**Intent Categories:**
- "GENERAL": Just course summaries/overviews (lightweight, ~300 tokens)
- "PREREQUISITES": Prerequisite information (summaries only - prereq codes are included)
- "SYLLABUS_OBJECTIVES": Syllabus and learning objectives (includes full course details)
- "ASSIGNMENTS": Assignment details (includes full course details)

**Examples:**
- "What computer science courses exist?" → intent="GENERAL"
- "What is CS004?" → intent="GENERAL"
- "What are the prerequisites for CS004?" → intent="PREREQUISITES"
- "What will I learn in CS004?" → intent="SYLLABUS_OBJECTIVES"
- "What's the syllabus for CS004?" → intent="SYLLABUS_OBJECTIVES"
- "What assignments are in CS004?" → intent="ASSIGNMENTS"

After calling the tool and getting results, provide a clear, helpful answer to the user."""

        messages.append(HumanMessage(content=system_prompt))

        # Add current query
        messages.append(HumanMessage(content=query))

        # Get LLM with tool binding
        llm = get_agent_llm()

        # Track LLM calls and tokens
        llm_calls = state.get("llm_calls", {}).copy()
        llm_calls["agent_llm"] = llm_calls.get("agent_llm", 0) + 1
        
        metrics = state.get("metrics", {}).copy()
        token_usage = metrics.get("token_usage", {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}).copy()

        # First LLM call - may include tool calls
        logger.info(f"   🧠 Calling LLM with tool binding...")
        response = await llm.ainvoke(messages)
        
        # Track tokens from first call
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            token_usage["input_tokens"] += response.usage_metadata.get("input_tokens", 0)
            token_usage["output_tokens"] += response.usage_metadata.get("output_tokens", 0)
            token_usage["total_tokens"] += response.usage_metadata.get("total_tokens", 0)

        # Check if LLM wants to use tools
        if response.tool_calls:
            logger.info(f"   🔧 LLM requested {len(response.tool_calls)} tool call(s)")

            # Add AI response to messages
            messages.append(response)

            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                logger.info(f"   📞 Executing tool: {tool_name}")
                logger.info(f"      Args: {tool_args}")

                # Execute the tool
                # Use the injected tool if available
                tool_to_use = _search_tool if _search_tool else search_courses_tool
                tool_result = await tool_to_use.ainvoke(tool_args)

                # Add tool result to messages
                messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    )
                )

            # Second LLM call - synthesize final answer
            llm_calls["agent_llm"] = llm_calls.get("agent_llm", 0) + 1
            logger.info(f"   🧠 Calling LLM to synthesize final answer...")
            final_response = await llm.ainvoke(messages)
            
            # Track tokens from second call
            if hasattr(final_response, 'usage_metadata') and final_response.usage_metadata:
                token_usage["input_tokens"] += final_response.usage_metadata.get("input_tokens", 0)
                token_usage["output_tokens"] += final_response.usage_metadata.get("output_tokens", 0)
                token_usage["total_tokens"] += final_response.usage_metadata.get("total_tokens", 0)
            
            final_answer = final_response.content.strip()
        else:
            # No tool calls, use direct response
            logger.info(f"   💬 LLM provided direct answer (no tools)")
            final_answer = response.content.strip()

        # Update state
        latency = (time.perf_counter() - start_time) * 1000

        state["final_response"] = final_answer
        state["llm_calls"] = llm_calls
        
        # Safely update execution path
        current_path = state.get("execution_path", [])
        if current_path is None:
            current_path = []
        # Create a new list to ensure we don't mutate shared state
        new_path = list(current_path)
        new_path.append("agent_completed")
        state["execution_path"] = new_path

        # Update metrics
        metrics["total_latency"] = latency
        metrics["token_usage"] = token_usage
        state["metrics"] = metrics

        logger.info(f"🤖 Agent complete in {latency:.2f}ms")
        logger.info(f"   Response: {final_answer[:100]}...")

        return state

    except Exception as e:
        logger.error(f"Agent node failed: {e}")
        import traceback
        traceback.print_exc()

        # Safely update state even on failure
        if "execution_path" not in state:
            state["execution_path"] = []
        state["execution_path"].append("agent_failed")
        state["final_response"] = f"I encountered an error: {str(e)}"
        return state
