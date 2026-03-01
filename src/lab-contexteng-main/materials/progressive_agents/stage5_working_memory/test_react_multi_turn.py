"""
Multi-turn conversation tests for Stage 5 ReAct agent.

Tests the ReAct pattern with conversation history and context.
Uses the full workflow with memory nodes.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import List, Dict

from tqdm.auto import tqdm

from agent import create_workflow, run_agent_async
from agent.setup import initialize_course_manager

# Configure logging - suppress by default for cleaner output
logging.basicConfig(
    level=logging.ERROR,  # Only show errors
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress all the chatty loggers
logging.getLogger("course-qa-workflow").setLevel(logging.ERROR)
logging.getLogger("course-qa-setup").setLevel(logging.ERROR)
logging.getLogger("redisvl.index.index").setLevel(logging.ERROR)
logging.getLogger("redis_context_course").setLevel(logging.ERROR)

logger = logging.getLogger("course-qa-workflow")


async def run_conversation(
    workflow,
    queries: List[str],
    conversation_name: str,
    session_id: str,
    student_id: str,
    verbose: bool = False
):
    """Run a multi-turn conversation using the full workflow with memory nodes."""
    # Capture all output for this conversation
    import sys
    from io import StringIO
    
    output_buffer = StringIO()
    
    output_buffer.write("\n" + "=" * 80 + "\n")
    output_buffer.write(f"CONVERSATION: {conversation_name}\n")
    output_buffer.write(f"Session: {session_id} | Student: {student_id}\n")
    output_buffer.write("=" * 80 + "\n")
    
    # Progress bar for turns
    progress_bar = tqdm(total=len(queries), desc=f"{conversation_name}", leave=False, 
                       bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} turns')
    
    for i, query in enumerate(queries, 1):
        output_buffer.write(f"\n{'─' * 80}\n")
        output_buffer.write(f"Turn {i}: {query}\n")
        output_buffer.write(f"{'─' * 80}\n")
        
        # Run the full workflow (includes load_memory → classify → react → save_memory)
        result = await run_agent_async(
            agent=workflow,
            query=query,
            session_id=session_id,
            student_id=student_id,
            enable_caching=False
        )
        
        # # Show execution path (which nodes ran)
        # execution_path = result.get("execution_path", [])
        # output_buffer.write(f"\n🔄 Workflow nodes executed: {' → '.join(execution_path)}\n")
        
        # Show loaded conversation history
        conversation_history = result.get("conversation_history", [])
        if i == 1:
            output_buffer.write(f"\n💭 WORKING MEMORY: [Empty - First turn]\n")
        else:
            output_buffer.write(f"\n💭 WORKING MEMORY: Loaded {len(conversation_history)} messages from RAMS\n")
            for msg in conversation_history[-4:]:  # Show last 2 exchanges
                role = "👤 User" if msg["role"] == "user" else "🤖 Agent"
                content = msg["content"][:80] + "..." if len(msg["content"]) > 80 else msg["content"]
                output_buffer.write(f"   {role}: {content}\n")
            if len(conversation_history) > 4:
                output_buffer.write(f"   ... (and {len(conversation_history) - 4} earlier messages)\n")
        
        # Show reasoning if available (from react_agent_node)
        if "reasoning_trace" in result:
            reasoning_trace = result["reasoning_trace"]
            output_buffer.write(f"\n🧠 REASONING: {len(reasoning_trace)} steps\n")
            
            if verbose:
                for j, step in enumerate(reasoning_trace, 1):
                    output_buffer.write(f"\n  Step {j}:\n")
                    output_buffer.write(f"    💭 Thought: {step.thought}\n")
                    output_buffer.write(f"    🔧 Action: {step.action}\n")
                    if step.action != "FINISH":
                        observation = step.observation[:200] + "..." if len(step.observation) > 200 else step.observation
                        output_buffer.write(f"    👁️  Observation: {observation}\n")
        
        # Print answer
        answer = result.get("final_response", "No response")
        output_buffer.write(f"\n✅ ANSWER:\n")
        output_buffer.write(f"   {answer}\n")
        
        # Calculate new message count
        new_message_count = (len(conversation_history) + 2) // 2
        output_buffer.write(f"\n📝 Memory saved to RAMS: Now contains {new_message_count} turn(s)\n")
        
        # Show full memory contents if verbose
        if verbose:
            # Reconstruct full conversation including current turn
            full_history = conversation_history.copy()
            full_history.append({"role": "user", "content": query})
            full_history.append({"role": "assistant", "content": answer})
            
            output_buffer.write(f"\n💾 FULL CONVERSATION HISTORY ({len(full_history)} messages):\n")
            for msg in full_history:
                role = "👤 User" if msg["role"] == "user" else "🤖 Agent"
                output_buffer.write(f"   {role}: {msg['content']}\n\n")
        
        # Update progress bar
        progress_bar.update(1)
    
    # Close progress bar
    progress_bar.close()
    
    # Display entire conversation in a collapsible dropdown
    from IPython.display import HTML, display
    
    conversation_output = output_buffer.getvalue()
    escaped = conversation_output.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    html = f"""
    <details style="margin: 15px 0; border: 2px solid #0066cc; padding: 15px; border-radius: 8px; background-color: #f8f9fa;">
        <summary style="cursor: pointer; font-weight: bold; font-size: 16px; color: #0066cc; padding: 5px;">
            📋 {conversation_name} - Click to expand ({len(queries)} turns)
        </summary>
        <pre style="margin-top: 15px; background-color: #ffffff; padding: 15px; border-radius: 5px; max-height: 600px; overflow-y: auto; border: 1px solid #dee2e6; font-size: 13px; line-height: 1.5;">{escaped}</pre>
    </details>
    """
    display(HTML(html))


async def test_pronoun_resolution(workflow, session_id: str, student_id: str, verbose: bool = False):
    """Test pronoun resolution across turns."""
    queries = [
        "What is CS002?",
        "What are the prerequisites for it?",
        "Tell me more about the syllabus",
    ]
    await run_conversation(workflow, queries, "Pronoun Resolution Test", session_id, student_id, verbose)


async def test_follow_up_questions(workflow, session_id: str, student_id: str, verbose: bool = False):
    """Test follow-up questions building on previous context."""
    queries = [
        "Tell me about machine learning courses",
        "Which one is best for beginners?",
        "What are the prerequisites for that course?",
    ]
    await run_conversation(workflow, queries, "Follow-up Questions Test", session_id, student_id, verbose)


async def test_comparison_across_turns(workflow, session_id: str, student_id: str, verbose: bool = False):
    """Test comparing courses mentioned in different turns."""
    queries = [
        "What is CS001?",
        "What is CS002?",
        "Which one should I take first?",
    ]
    await run_conversation(workflow, queries, "Comparison Across Turns Test", session_id, student_id, verbose)


async def test_context_accumulation(workflow, session_id: str, student_id: str, verbose: bool = False):
    """Test accumulating context across multiple turns."""
    queries = [
        "I'm interested in computer vision",
        "What courses cover that topic?",
        "What are the prerequisites for the advanced one?",
        "Are there any beginner courses I should take first?",
    ]
    await run_conversation(workflow, queries, "Context Accumulation Test", session_id, student_id, verbose)


async def run_tests(verbose: bool = False, student_id: str = "test_user"):
    """
    Run all multi-turn tests using the full workflow with memory nodes.
    
    Args:
        verbose: If True, show detailed reasoning traces and full memory contents.
                If False (default), show only execution path and answers.
        student_id: User identifier for RAMS (default: "test_user")
    """
    print("\n" + "=" * 80)
    print("STAGE 5: WORKING MEMORY DEMONSTRATIONS (Using Workflow)")
    print("Focus: Load Memory → Classify → ReAct → Save Memory")
    print(f"Student ID: {student_id}")
    print("=" * 80)
    
    # Initialize workflow (suppress output)
    import sys
    from io import StringIO
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        course_manager = await initialize_course_manager(auto_load=True)
        workflow = create_workflow(course_manager, verbose=False)
    finally:
        sys.stdout = old_stdout
    
    print("✅ Workflow initialized with memory nodes")
    
    # Create list of tests
    tests = [
        ("Pronoun Resolution Test", f"pronoun_resolution_{uuid.uuid4().hex[:8]}", test_pronoun_resolution),
        ("Follow-up Questions Test", f"follow_up_{uuid.uuid4().hex[:8]}", test_follow_up_questions),
        ("Comparison Across Turns Test", f"comparison_{uuid.uuid4().hex[:8]}", test_comparison_across_turns),
        ("Context Accumulation Test", f"context_accumulation_{uuid.uuid4().hex[:8]}", test_context_accumulation),
    ]
    
    # Overall progress bar
    overall_progress = tqdm(total=len(tests), desc="Running Tests", 
                           bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} tests')
    
    for test_name, session_id, test_func in tests:
        await test_func(workflow, session_id, student_id, verbose)
        overall_progress.update(1)
    
    overall_progress.close()
    
    print("\n" + "=" * 80)
    print("✅ ALL MULTI-TURN TESTS COMPLETE")
    print("=" * 80)
    print("\nKey Takeaway: Working memory (via RAMS) allows the agent to:")
    print("  • Resolve pronouns ('it', 'that course') using conversation history")
    print("  • Answer follow-up questions without re-stating context")
    print("  • Compare items mentioned in separate turns")
    print("  • Accumulate understanding across a multi-turn conversation")
    print(f"\n💡 All conversations saved to RAMS for student: {student_id}")

    # Return session IDs for compression analysis in notebook
    session_ids = [session_id for _, session_id, _ in tests]
    return session_ids

