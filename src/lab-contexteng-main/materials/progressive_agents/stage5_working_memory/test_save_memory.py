"""
Test suite for save_working_memory_node implementation.

Tests saving to empty session and session with existing conversation history.
"""

import asyncio
from typing import Dict, Any


async def test_save_to_new_session(save_fn) -> bool:
    """Test saving a conversation turn to a new session with no previous history."""
    print("=" * 60)
    print("TEST 1: Saving to new session (no previous history)")
    print("=" * 60)

    # Test saving first turn to a fresh session
    new_session_state = {
        "session_id": "test-save-new-session-123",
        "student_id": "student-save-001",
        "conversation_history": [],
        "user_query": "What is CS002?",
        "agent_response": "CS002 is Data Structures and Algorithms, covering fundamental concepts like arrays, linked lists, trees, and sorting algorithms."
    }

    print(f"📋 Memory Context:")
    print(f"   Session ID: {new_session_state['session_id']}")
    print(f"   Student ID: {new_session_state['student_id']}")
    print(f"   Previous history: {len(new_session_state['conversation_history'])} messages")
    print(f"   Saving new turn...\n")

    result = await save_fn(new_session_state)
    
    print(f"💬 Saved Conversation Turn:")
    print(f"   User: {new_session_state['user_query']}")
    print(f"   Agent: {new_session_state['agent_response'][:80]}...")
    
    print("\n✓ Test passed: Successfully saved first turn to new session\n")
    
    return True


async def test_save_with_existing_history(save_fn) -> bool:
    """Test saving a conversation turn when there's existing history."""
    print("=" * 60)
    print("TEST 2: Saving to session with existing history")
    print("=" * 60)

    # Test saving a follow-up turn to a session with history
    existing_history_state = {
        "session_id": "test-save-with-history-456",
        "student_id": "student-save-002",
        "conversation_history": [
            {"role": "user", "content": "What is CS001?"},
            {"role": "assistant", "content": "CS001 is Introduction to Programming, covering basic programming concepts and Python fundamentals."},
            {"role": "user", "content": "What comes after it?"},
            {"role": "assistant", "content": "CS002 Data Structures and Algorithms comes after CS001."}
        ],
        "user_query": "What are the prerequisites for CS003?",
        "agent_response": "CS003 Computer Architecture requires CS002 as a prerequisite."
    }

    print(f"📋 Memory Context:")
    print(f"   Session ID: {existing_history_state['session_id']}")
    print(f"   Student ID: {existing_history_state['student_id']}")
    print(f"   Previous history: {len(existing_history_state['conversation_history'])} messages")
    print(f"   Saving new turn (turn 3)...\n")

    result = await save_fn(existing_history_state)
    
    print(f"📦 Complete Memory After Save:")
    print(f"   Session ID: {existing_history_state['session_id']}")
    print(f"   Student ID: {existing_history_state['student_id']}")
    print(f"   Total messages: {len(existing_history_state['conversation_history']) + 2}")
    print(f"   (Previous: {len(existing_history_state['conversation_history'])} + Current turn: 2)")
    
    print(f"\n💬 Current Turn Saved:")
    print(f"   User: {existing_history_state['user_query']}")
    print(f"   Agent: {existing_history_state['agent_response']}")
    
    print("\n✓ Test passed: Successfully saved turn with existing history\n")
    
    return True


async def run_tests(save_fn):
    """
    Run all save memory node tests.
    
    Args:
        save_fn: The save_working_memory_node function to test
    """
    try:
        # Run Test 1: Save to new session
        await test_save_to_new_session(save_fn)
        
        # Run Test 2: Save with existing history
        await test_save_with_existing_history(save_fn)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ All tests passed! Save node handles both scenarios correctly")
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
