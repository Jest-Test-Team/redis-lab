"""Test hybrid search tool - semantic + exact filtering."""

import json
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)


async def test_hybrid_search_tool(search_tool_func):
    """Test the hybrid search tool implementation."""
    print("🧪 Testing Hybrid Search Tool\n")
    all_passed = True
    
    # Test 1: Semantic Search
    try:
        result = await search_tool_func(query="I want to learn about neural networks")
        data = json.loads(result)
        assert isinstance(data, list) and len(data) > 0
        print(f"✅ Test 1: Semantic search returned {len(data)} courses")
    except Exception as e:
        print(f"❌ Test 1: Semantic search failed - {e}")
        all_passed = False
    
    # Test 2: Exact Match
    try:
        result = await search_tool_func(query="Tell me about this course", course_code="CS007")
        data = json.loads(result)
        codes = [c.get('course_code') for c in data]
        assert "CS007" in codes
        print(f"✅ Test 2: Exact match found CS007")
    except Exception as e:
        print(f"❌ Test 2: Exact match failed - {e}")
        all_passed = False
    
    # Test 3: Both modes work
    try:
        sem = json.loads(await search_tool_func(query="computer vision courses"))
        exact_result = await search_tool_func(query="computer vision course", course_code="CS013")
        exact = json.loads(exact_result)
        assert len(sem) > 0 and len(exact) > 0
        print(f"✅ Test 3: Semantic ({len(sem)}) and exact ({len(exact)}) both work")
    except Exception as e:
        print(f"❌ Test 3: Filtering behavior failed - {e}")
        all_passed = False
    
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed
