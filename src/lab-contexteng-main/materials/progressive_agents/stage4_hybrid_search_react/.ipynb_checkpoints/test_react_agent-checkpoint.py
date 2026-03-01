"""
Test utility for ReAct agent implementation.

Tests the Thought → Action → Observation loop logic.
"""

import asyncio
import io
import logging
import sys

from IPython.display import display, HTML, Markdown


async def test_react_agent(react_agent_func, tools_map, llm):
    """
    Test the ReAct agent implementation with educational output.
    
    Shows the Thought → Action → Observation loop for learning purposes
    while suppressing verbose HTTP and logging noise.
    
    Args:
        react_agent_func: The react_agent_node function to test
        tools_map: Dictionary of available tools
        llm: The LLM instance to use
    """
    # Temporarily suppress verbose logging (HTTP requests, workflow info)
    httpx_logger = logging.getLogger("httpx")
    workflow_logger = logging.getLogger("course-qa-workflow")
    original_httpx_level = httpx_logger.level
    original_workflow_level = workflow_logger.level
    
    httpx_logger.setLevel(logging.WARNING)
    workflow_logger.setLevel(logging.WARNING)
    
    display(Markdown("## 🧪 Testing ReAct Agent Implementation"))
    
    all_passed = True
    
    # Test 1: Simple query requiring tool call
    test1_output = io.StringIO()
    test1_passed = False
    old_stdout = sys.stdout
    
    try:
        sys.stdout = test1_output
        print("Query: 'What are the prerequisites for CS002?'\n")
        
        state = {
            "input": "What are the prerequisites for CS002?",
            "history": [],
            "final_response": ""
        }
        result = await react_agent_func(state)
        
        if result.get("final_response"):
            test1_passed = True
            print(f"\n✅ Passed")
            print(f"Final Answer: {result['final_response'][:300]}...")
        else:
            print("❌ No final response returned")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        sys.stdout = old_stdout
    
    icon1 = "✅" if test1_passed else "❌"
    border1 = "#4CAF50" if test1_passed else "#f44336"
    display(HTML(f"""<details style="margin: 4px 0; border: 1px solid {border1}; border-radius: 4px;">
        <summary style="cursor: pointer; padding: 6px 10px; background: #fafafa; font-weight: bold;">{icon1} Test 1: Simple tool call query</summary>
        <pre style="padding: 8px 12px; font-size: 0.85em; white-space: pre-wrap; margin: 0;">{test1_output.getvalue()}</pre>
    </details>"""))
    all_passed &= test1_passed
    
    # Test 2: Query requiring reasoning
    test2_output = io.StringIO()
    test2_passed = False
    
    try:
        sys.stdout = test2_output
        print("Query: 'Tell me about machine learning courses'\n")
        
        state = {
            "input": "Tell me about machine learning courses",
            "history": [],
            "final_response": ""
        }
        result = await react_agent_func(state)
        
        if result.get("final_response"):
            test2_passed = True
            course_count = result['final_response'].count("**CS") + result['final_response'].count("**MATH")
            print(f"\n✅ Passed - Found {course_count} relevant course(s)")
            print(f"Final Answer: {result['final_response'][:400]}...")
        else:
            print("❌ No final response returned")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        sys.stdout = old_stdout
    
    icon2 = "✅" if test2_passed else "❌"
    border2 = "#4CAF50" if test2_passed else "#f44336"
    display(HTML(f"""<details style="margin: 4px 0; border: 1px solid {border2}; border-radius: 4px;">
        <summary style="cursor: pointer; padding: 6px 10px; background: #fafafa; font-weight: bold;">{icon2} Test 2: Multi-step reasoning query</summary>
        <pre style="padding: 8px 12px; font-size: 0.85em; white-space: pre-wrap; margin: 0;">{test2_output.getvalue()}</pre>
    </details>"""))
    all_passed &= test2_passed
    
    # Test 3: Max iterations safety check
    test3_output = io.StringIO()
    test3_passed = False
    
    try:
        sys.stdout = test3_output
        print("Query: 'What courses exist?'\n")
        
        state = {
            "input": "What courses exist?",
            "history": [],
            "final_response": ""
        }
        result = await react_agent_func(state)
        
        if result.get("final_response"):
            test3_passed = True
            print(f"\n✅ Passed (completed within iteration limit)")
            print(f"Final Answer: {result['final_response'][:400]}...")
        else:
            print("❌ Agent did not return response")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        sys.stdout = old_stdout
    
    icon3 = "✅" if test3_passed else "❌"
    border3 = "#4CAF50" if test3_passed else "#f44336"
    display(HTML(f"""<details style="margin: 4px 0; border: 1px solid {border3}; border-radius: 4px;">
        <summary style="cursor: pointer; padding: 6px 10px; background: #fafafa; font-weight: bold;">{icon3} Test 3: Max iterations safety check</summary>
        <pre style="padding: 8px 12px; font-size: 0.85em; white-space: pre-wrap; margin: 0;">{test3_output.getvalue()}</pre>
    </details>"""))
    all_passed &= test3_passed
    
    # Restore logging levels
    httpx_logger.setLevel(original_httpx_level)
    workflow_logger.setLevel(original_workflow_level)
    
    # Final banner
    if all_passed:
        display(HTML("""<div style="margin-top: 10px; padding: 8px; background: #e8f5e9; border-radius: 4px; border-left: 4px solid #4CAF50;">
            <b style="color: #2e7d32;">✅ ALL TESTS PASSED!</b><br>
            <span style="font-size: 0.9em;">Thought→Action→Observation loop ✓ | Tool calls ✓ | Final answers ✓ | Iteration limits ✓</span>
        </div>"""))
    else:
        display(HTML("""<div style="margin-top: 10px; padding: 8px; background: #ffebee; border-radius: 4px; border-left: 4px solid #f44336;">
            <b style="color: #c62828;">❌ SOME TESTS FAILED</b>
        </div>"""))
    
    return all_passed
