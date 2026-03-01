"""
Simple test for store_memory tool.
"""
from agent import get_memory_client
from agent_memory_client.models import ClientMemoryRecord


async def test_store_memory_tool(store_func, student_id: str = "test_student"):
    """
    Test the store_memory tool implementation by storing memories directly via memory_client.
    """
    print("🧪 Testing store_memory tool...")
    print("=" * 60)
    
    memory_client = get_memory_client()
    all_passed = True
    
    # Test 1: Store semantic memory
    print("\n📋 TEST 1: Store semantic memory")
    print("-" * 60)
    
    try:
        memory1 = ClientMemoryRecord(
            text="Student prefers online courses",
            user_id=student_id,
            memory_type="semantic",
            topics=["preferences"],
        )
        await memory_client.create_long_term_memory([memory1])
        print(f"✅ Success: Stored semantic memory")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # Test 2: Store episodic memory
    print("\n📋 TEST 2: Store episodic memory")
    print("-" * 60)
    
    try:
        memory2 = ClientMemoryRecord(
            text="Student completed CS101 on 2024-10-15",
            user_id=student_id,
            memory_type="episodic",
            topics=["completion"],
        )
        await memory_client.create_long_term_memory([memory2])
        print(f"✅ Success: Stored episodic memory")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        all_passed = False
    
    # Test 3: Store memory with multiple topics
    print("\n📋 TEST 3: Store memory with multiple topics")
    print("-" * 60)
    
    try:
        memory3 = ClientMemoryRecord(
            text="Student is interested in machine learning and AI",
            user_id=student_id,
            memory_type="semantic",
            topics=["interests", "goals", "ML"],
        )
        await memory_client.create_long_term_memory([memory3])
        print(f"✅ Success: Stored memory with multiple topics")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print(f"✅ Stored 3 test memories for '{student_id}'")
    else:
        print("❌ SOME TESTS FAILED - check errors above")
    print("=" * 60)
    
    return all_passed


# Convenience function for running in notebooks
def run_test(store_func, student_id: str = "test_student"):
    """Synchronous wrapper for test_store_memory_tool."""
    return asyncio.run(test_store_memory_tool(store_func, student_id))


if __name__ == "__main__":
    print("This test utility should be imported and used with your store_memory implementation")
    print("\nExample usage:")
    print("  from test_store_memory_tool import test_store_memory_tool")
    print("  await test_store_memory_tool(store_memory, student_id='test_user')")
