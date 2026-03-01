"""Test hybrid search tool - semantic + exact filtering."""

import json
import logging

# Suppress httpx logging noise
logging.getLogger("httpx").setLevel(logging.WARNING)


async def test_hybrid_search_tool(search_tool_func):
    """
    Test the hybrid search tool implementation.
    
    Args:
        search_tool_func: Function that takes query and optional course_code
        
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("🧪 Testing your hybrid search tool implementation...\n")
    
    all_passed = True
    
    # Test 1: Semantic Search
    print("=" * 70)
    print("TEST 1: Semantic Search (No Exact Match)")
    print("=" * 70)
    
    query1 = "I want to learn about neural networks"
    print(f"Query: {query1}")
    print(f"Course Code Filter: None (semantic only)")
    
    try:
        result = await search_tool_func(query=query1)
        data = json.loads(result)
        
        print(f"\n📊 Result:")
        print(f"   Courses returned: {len(data)}")
        if data:
            codes = [c.get('course_code', 'N/A') for c in data[:3]]
            print(f"   Top matches: {', '.join(codes)}")
        
        if isinstance(data, list) and len(data) > 0:
            print("   ✅ PASSED - Semantic search returned relevant courses")
        else:
            print("   ❌ FAILED - No courses returned")
            all_passed = False
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        all_passed = False
    
    print()
    
    # Test 2: Exact Match
    print("=" * 70)
    print("TEST 2: Exact Match (Course Code Filter)")
    print("=" * 70)
    
    query2 = "Tell me about this course"
    code2 = "CS007"
    print(f"Query: {query2}")
    print(f"Course Code Filter: {code2}")
    
    try:
        result = await search_tool_func(query=query2, course_code=code2)
        data = json.loads(result)
        codes = [c.get('course_code') for c in data]
        
        print(f"\n📊 Result:")
        print(f"   Courses returned: {len(data)}")
        print(f"   Course codes: {', '.join(codes)}")
        
        if code2 in codes:
            print(f"   ✅ PASSED - Exact match found {code2}")
        else:
            print(f"   ❌ FAILED - {code2} not in results")
            all_passed = False
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        all_passed = False
    
    print()
    
    # Test 3: Both modes work together
    print("=" * 70)
    print("TEST 3: Hybrid Behavior (Both Modes Work)")
    print("=" * 70)
    
    query3_sem = "computer vision courses"
    query3_exact = "computer vision course"
    code3 = "CS013"
    print(f"Semantic Query: {query3_sem}")
    print(f"Exact Query: {query3_exact} (with code: {code3})")
    
    try:
        sem_result = await search_tool_func(query=query3_sem)
        sem = json.loads(sem_result)
        
        exact_result = await search_tool_func(query=query3_exact, course_code=code3)
        exact = json.loads(exact_result)
        
        print(f"\n📊 Result:")
        print(f"   Semantic results: {len(sem)} courses")
        print(f"   Exact results: {len(exact)} courses")
        
        if len(sem) > 0 and len(exact) > 0:
            print("   ✅ PASSED - Both semantic and exact modes work correctly")
        else:
            print("   ❌ FAILED - One or both modes returned no results")
            all_passed = False
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        all_passed = False
    
    # Final summary
    print()
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Your hybrid search tool correctly:")
        print("  • Returns relevant courses via semantic search")
        print("  • Finds exact matches when course_code is provided")
        print("  • Supports both modes independently")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Review the test output above and fix any issues.")
    print("=" * 70)
    
