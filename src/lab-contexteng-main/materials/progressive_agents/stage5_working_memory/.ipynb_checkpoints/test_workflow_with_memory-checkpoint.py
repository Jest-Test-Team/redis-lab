"""
Test the full Stage 5 workflow with memory AND detailed reasoning traces.

This test demonstrates:
1. Load working memory from RAMS (session-scoped conversation history)
2. Classify intent
3. ReAct agent reasoning (Thought → Action → Observation cycles)
4. Save working memory back to RAMS

Shows both the memory lifecycle AND the detailed reasoning process.
"""

import logging
from pathlib import Path

from redis_context_course import CourseManager

from agent.workflow import (
    create_workflow,
    run_agent_async,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def test_single_turn_queries():
    """Test single-turn queries showing full workflow + reasoning."""
    print("\n" + "=" * 80)
    print("STAGE 5: Full Workflow with Working Memory")
    print("=" * 80)
    print("\nThis test demonstrates the complete memory lifecycle:")
    print("  1. Load Working Memory (from RAMS)")
    print("  2. Classify Intent")
    print("  3. ReAct Agent (with reasoning traces)")
    print("  4. Save Working Memory (to RAMS)")
    print("=" * 80)
    
    # Initialize using setup_agent to ensure courses are loaded
    print("\nInitializing Agent (with course data)...")
    from agent.setup import setup_agent
    course_manager, _ = await setup_agent(auto_load_courses=True)

    print("Creating agent workflow...")
    agent = create_workflow(course_manager, verbose=False)

    # Test questions
    test_cases = [
        {
            "name": "Simple Course Lookup",
            "query": "What is CS004?",
            "session_id": "test_simple",
        },
        {
            "name": "Semantic Search",
            "query": "I want to learn about machine learning",
            "session_id": "test_semantic",
        },
        {
            "name": "Prerequisites Query",
            "query": "What are the prerequisites for CS004?",
            "session_id": "test_prereqs",
        },
    ]

    for test in test_cases:
        print("\n" + "=" * 80)
        print(f"TEST: {test['name']}")
        print("=" * 80)
        print(f"Query: {test['query']}")
        
        try:
            # Run the full workflow
            result = await run_agent_async(
                agent=agent,
                query=test['query'],
                session_id=test['session_id'],
                student_id="test_user",
                enable_caching=False,
            )

            # Show execution path (memory lifecycle)
            execution_path = " → ".join(result.get("execution_path", []))
            print(f"\n{'─' * 80}")
            print("EXECUTION PATH (Memory Lifecycle):")
            print(f"{'─' * 80}")
            print(f"  {execution_path}")
            
            # Show reasoning trace (ReAct steps)
            reasoning_trace = result.get("reasoning_trace", [])
            if reasoning_trace:
                print(f"\n{'─' * 80}")
                print("REASONING TRACE (ReAct Agent):")
                print(f"{'─' * 80}")
                for i, step in enumerate(reasoning_trace, 1):
                    print(f"\nStep {i}:")
                    print(f"  💭 Thought: {step.get('thought', 'N/A')}")
                    print(f"  🔧 Action: {step.get('action', 'N/A')}")
                    if step.get('action') != 'FINISH':
                        action_input = step.get('action_input', 'N/A')
                        print(f"     Input: {action_input}")
                        observation = step.get('observation', 'N/A')
                        if len(observation) > 200:
                            observation = observation[:200] + "..."
                        print(f"  👁️  Observation: {observation}")
                    else:
                        print(f"     ✅ FINISH - Answer Ready")
            
            # Show final response
            response = result.get("final_response", "No response")
            print(f"\n{'─' * 80}")
            print("FINAL ANSWER:")
            print(f"{'─' * 80}")
            print(response)
            
            # Show metrics
            metrics = result.get("metrics", {})
            print(f"\n📊 Metrics:")
            print(f"   Total latency: {metrics.get('total_latency', 0):.2f}ms")
            print(f"   Reasoning steps: {len(reasoning_trace)}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


async def run_tests():
    """Run all tests."""
    await test_single_turn_queries()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests())
