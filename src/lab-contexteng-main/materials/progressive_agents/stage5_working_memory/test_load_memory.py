"""
Test suite for load_working_memory_node implementation.

Tests both empty session (no history) and session with existing conversation history.
Uses production save implementation internally for test data setup.
"""

import asyncio
from typing import Dict, Any


async def test_empty_session(load_fn) -> bool:
    """Test loading from a session with no previous history."""
    print("=" * 60)
    print("TEST 1: Loading from empty session (no previous history)")
    print("=" * 60)

    # Test with a fresh session that has no history
    empty_state = {
        "session_id": "test-session-empty-123",
        "student_id": "student-456",
        "conversation_history": []
    }

    print(f"📋 Memory Context:")
    print(f"   Session ID: {empty_state['session_id']}")
    print(f"   Student ID: {empty_state['student_id']}")
    print(f"   Loading working memory...\n")

    result_empty = await load_fn(empty_state)
    
    print(f"📦 Loaded Memory Structure:")
    print(f"   Conversation history: {len(result_empty['conversation_history'])} messages")
    print(f"   Session ID: {result_empty['session_id']}")
    print(f"   Student ID: {result_empty['student_id']}")
    
    assert len(result_empty['conversation_history']) == 0, "Expected empty history for new session"
    print("\n✓ Test passed: Empty session returns no messages\n")
    
    return True


async def test_session_with_history(load_fn) -> bool:
    """Test loading from a session with existing conversation history."""
    # Import production save for test setup
    from agent.nodes import save_working_memory_node as production_save
    
    print("=" * 60)
    print("TEST 2: Loading from session with existing history")
    print("=" * 60)

    # First, save some conversation history to create a session with messages
    # Use complete state structure expected by production save
    save_state = {
        "session_id": "test-session-with-history-456",
        "student_id": "student-789",
        "conversation_history": [],
        "original_query": "What is CS001?",
        "final_response": "CS001 is Introduction to Programming, covering fundamental programming concepts.",
        "metrics": {}
    }

    # Save first turn
    await production_save(save_state)

    # Build on the first turn for the second save
    save_state["conversation_history"] = [
        {"role": "user", "content": "What is CS001?"},
        {"role": "assistant", "content": "CS001 is Introduction to Programming, covering fundamental programming concepts."}
    ]
    save_state["original_query"] = "What are the prerequisites?"
    save_state["final_response"] = "CS001 has no prerequisites - it's an introductory course."
    
    # Save second turn
    await production_save(save_state)

    # Now test loading from this session with history
    load_state = {
        "session_id": "test-session-with-history-456",
        "student_id": "student-789",
        "conversation_history": []
    }

    print(f"\n📋 Memory Context:")
    print(f"   Session ID: {load_state['session_id']}")
    print(f"   Student ID: {load_state['student_id']}")
    print(f"   Loading working memory...\n")

    result_with_history = await load_fn(load_state)
    
    print(f"📦 Loaded Memory Structure:")
    print(f"   Session ID: {result_with_history['session_id']}")
    print(f"   Student ID: {result_with_history['student_id']}")
    print(f"   Conversation history: {len(result_with_history['conversation_history'])} messages")
    
    assert len(result_with_history['conversation_history']) == 4, "Expected 4 messages (2 turns)"
    
    print(f"\n💬 Complete Conversation History (2 turns, 4 messages):")
    for i, msg in enumerate(result_with_history['conversation_history'], 1):
        print(f"\n   Message {i}:")
        print(f"   Role: {msg['role']}")
        print(f"   Content: {msg['content']}")

    print("\n✓ Test passed: Session with history returns all messages\n")

    return True


async def run_tests(load_fn):
    """
    Run all load memory node tests.
    
    Args:
        load_fn: The load_working_memory_node function to test
    """
    try:
        # Run Test 1: Empty session
        await test_empty_session(load_fn)
        
        # Run Test 2: Session with history (uses production save internally for setup)
        await test_session_with_history(load_fn)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ All tests passed! Load node handles both scenarios correctly")
        print("=" * 60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
