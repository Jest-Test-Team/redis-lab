"""
Simple test for search_memories tool.
"""
from agent import get_memory_client
from agent_memory_client.models import ClientMemoryRecord

async def seed_test_memories(student_id: str = "test_user"):
    """
    Seed long-term memory with test data for the given student.
    Call this before running tests if Redis was cleared.
    """

    memory_client = get_memory_client()

    test_memories = [
        ClientMemoryRecord(
            text="Student prefers online courses",
            user_id=student_id,
            memory_type="semantic",
            topics=["preferences", "learning_style"],
        ),
        ClientMemoryRecord(
            text="Student is interested in machine learning and AI",
            user_id=student_id,
            memory_type="semantic",
            topics=["interests", "goals"],
        ),
        ClientMemoryRecord(
            text="Student works full-time and prefers evening classes",
            user_id=student_id,
            memory_type="semantic",
            topics=["preferences", "schedule"],
        ),
        ClientMemoryRecord(
            text="Student has completed CS101 Introduction to Programming",
            user_id=student_id,
            memory_type="episodic",
            topics=["completed_courses", "progress"],
        ),
    ]
    
    await memory_client.create_long_term_memory(test_memories)
    print(f"✅ Seeded {len(test_memories)} test memories for '{student_id}'")
    return len(test_memories)


async def test_search_memories_tool(search_func, student_id: str = "test_user"):
    """
    Test the search_memories tool implementation.
    """
    print("🧪 Testing search_memories tool...")
    print("=" * 60)
    
    # Test 1: Basic search with results
    print("\n📋 TEST 1: Search for preferences")
    print("-" * 60)
    print(f"Student ID: {student_id}")
    
    try:
        results = await search_func.coroutine(
            query="preferences interests",
            limit=3,
            student_id=student_id
        )
        
        if not isinstance(results, list):
            print(f"❌ FAILED: Expected list, got {type(results)}")
            return False
        
        print(f"✅ Returned list with {len(results)} results")
        
        if results:
            result = results[0]
            required_fields = ["text", "memory_type"]
            for field in required_fields:
                if field not in result:
                    print(f"❌ FAILED: Missing '{field}' in result")
                    return False
            
            print("✅ Results have correct structure")
            for i, mem in enumerate(results[:3]):
                text = mem.get('text', 'N/A')[:50]
                print(f"   {i+1}. {text}...")
        else:
            print("ℹ️  No results found (OK if no memories exist)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Search without student_id (should return empty)
    print("\n📋 TEST 2: Search without student_id")
    print("-" * 60)
    
    try:
        results2 = await search_func.coroutine(
            query="test query",
            limit=3,
            student_id=None
        )
        
        if not isinstance(results2, list):
            print(f"❌ FAILED: Expected list, got {type(results2)}")
            return False
        
        if len(results2) == 0:
            print("✅ Correctly returned empty list for missing student_id")
        else:
            print("⚠️  Warning: Got results without student_id (check validation)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    
    return True


# Convenience function for running in notebooks
def run_test(search_func, student_id: str = "test_student"):
    """Synchronous wrapper for test_search_memories_tool."""
    return asyncio.run(test_search_memories_tool(search_func, student_id))


if __name__ == "__main__":
    print("This test utility should be imported and used with your search_memories implementation")
    print("\nExample usage:")
    print("  from test_search_memories_tool import test_search_memories_tool")
    print("  await test_search_memories_tool(search_memories, student_id='test_user')")
