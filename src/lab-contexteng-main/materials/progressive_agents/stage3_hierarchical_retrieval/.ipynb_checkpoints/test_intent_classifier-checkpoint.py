"""
Test utility for validating intent classification function.

Tests the student's implementation against all 5 intent categories.
"""

import asyncio


async def test_intent_classifier(classify_func):
    """
    Test the intent classification function with various queries.
    
    Args:
        classify_func: Async function that takes a query string and returns intent category
        
    Returns:
        None (prints results)
    """
    # Test cases covering all 5 categories
    test_cases = [
        # GREETING
        {
            "query": "Hello!",
            "expected": "GREETING",
            "description": "Simple greeting"
        },
        {
            "query": "Hi there, how are you?",
            "expected": "GREETING",
            "description": "Greeting with pleasantry"
        },
        {
            "query": "Thanks for your help!",
            "expected": "GREETING",
            "description": "Thank you message"
        },
        
        # GENERAL
        {
            "query": "What is CS002?",
            "expected": "GENERAL",
            "description": "General course question"
        },
        {
            "query": "Tell me about Introduction to Machine Learning",
            "expected": "GENERAL",
            "description": "Course overview request"
        },
        {
            "query": "Can you describe DATA101?",
            "expected": "GENERAL",
            "description": "Course description request"
        },
        
        # SYLLABUS_OBJECTIVES
        {
            "query": "Show me the syllabus for CS002",
            "expected": "SYLLABUS_OBJECTIVES",
            "description": "Explicit syllabus request"
        },
        {
            "query": "What topics are covered in Machine Learning?",
            "expected": "SYLLABUS_OBJECTIVES",
            "description": "Topics covered question"
        },
        {
            "query": "What will I learn in this course?",
            "expected": "SYLLABUS_OBJECTIVES",
            "description": "Learning outcomes question"
        },
        {
            "query": "Give me details about DATA101",
            "expected": "SYLLABUS_OBJECTIVES",
            "description": "Detailed course structure request"
        },
        
        # ASSIGNMENTS
        {
            "query": "What are the assignments for CS002?",
            "expected": "ASSIGNMENTS",
            "description": "Assignment list request"
        },
        {
            "query": "How many exams are there?",
            "expected": "ASSIGNMENTS",
            "description": "Exam count question"
        },
        {
            "query": "What's the workload like?",
            "expected": "ASSIGNMENTS",
            "description": "Workload question"
        },
        {
            "query": "Tell me about the projects in this course",
            "expected": "ASSIGNMENTS",
            "description": "Project information request"
        },
        
        # PREREQUISITES
        {
            "query": "What are the prerequisites for Advanced Algorithms?",
            "expected": "PREREQUISITES",
            "description": "Explicit prerequisites question"
        },
        {
            "query": "What do I need to know before taking this course?",
            "expected": "PREREQUISITES",
            "description": "Prior knowledge question"
        },
        {
            "query": "Do I need any background for CS300?",
            "expected": "PREREQUISITES",
            "description": "Background requirements question"
        }
    ]
    
    print("🧪 Testing Intent Classification Function")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        query = test["query"]
        expected = test["expected"]
        description = test["description"]
        
        try:
            # Call the student's function
            result = await classify_func(query)
            
            # Check if result matches expected
            if result == expected:
                print(f"✅ Test {i} PASSED: {description}")
                print(f"   Query: \"{query}\"")
                print(f"   Expected: {expected}, Got: {result}")
                passed += 1
            else:
                print(f"❌ Test {i} FAILED: {description}")
                print(f"   Query: \"{query}\"")
                print(f"   Expected: {expected}, Got: {result}")
                failed += 1
                
        except Exception as e:
            print(f"💥 Test {i} ERROR: {description}")
            print(f"   Query: \"{query}\"")
            print(f"   Error: {e}")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 80)
    print(f"📊 Test Results: {passed} passed, {failed} failed out of {len(test_cases)} total")
    
    if failed == 0:
        print("🎉 All tests passed! Your intent classifier is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Review the output above to debug.")
    
    return passed, failed


# Convenience function for running tests
def run_tests(classify_func):
    """Synchronous wrapper for test_intent_classifier."""
    return asyncio.run(test_intent_classifier(classify_func))
