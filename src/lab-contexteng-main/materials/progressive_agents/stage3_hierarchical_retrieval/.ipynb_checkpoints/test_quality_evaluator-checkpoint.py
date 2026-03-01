"""
Test utility for validating quality evaluator implementations.

This module provides a test function that can be used to verify
the quality evaluation logic works correctly with different context quality levels.
"""


async def test_quality_evaluator(evaluate_func):
    """
    Test a quality evaluator implementation.
    
    Args:
        evaluate_func: Function that takes (question, context) and returns (score, reasoning)
        
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("🧪 Testing your quality evaluator implementation...\n")
    
    all_passed = True
    
    # Test 1: GOOD context (should score high)
    print("=" * 70)
    print("TEST 1: High Quality Context (Complete & Relevant)")
    print("=" * 70)
    
    question1 = "What are the learning objectives for CS101?"
    good_context = """
CS101: Intro to Computer Science
Learning Objectives:
- Understand fundamental programming concepts
- Master Python syntax and control flow
- Implement algorithms and data structures
- Apply computational thinking to problem-solving
"""
    
    print(f"Question: {question1}")
    print(f"Context Preview: {good_context[:100]}...")
    
    try:
        score1, reasoning1 = await evaluate_func(question1, good_context)
        print(f"\n📊 Result:")
        print(f"   Score: {score1:.2f}")
        print(f"   Reasoning: {reasoning1}")
        
        if score1 >= 0.7:
            print("   ✅ PASSED - High quality context correctly scored ≥ 0.7")
        else:
            print(f"   ⚠️  WARNING - High quality context scored {score1:.2f} (expected ≥ 0.7)")
            all_passed = False
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        all_passed = False
    
    print()
    
    # Test 2: BAD context (should score low)
    print("=" * 70)
    print("TEST 2: Low Quality Context (Vague & Generic)")
    print("=" * 70)
    
    question2 = "What are the learning objectives for CS101?"
    bad_context = """
CS101 is a course offered by the Computer Science department.
Programming is important. Python is a popular language.
Many students enjoy computer science.
"""
    
    print(f"Question: {question2}")
    print(f"Context Preview: {bad_context[:100]}...")
    
    try:
        score2, reasoning2 = await evaluate_func(question2, bad_context)
        print(f"\n📊 Result:")
        print(f"   Score: {score2:.2f}")
        print(f"   Reasoning: {reasoning2}")
        
        if score2 < 0.7:
            print("   ✅ PASSED - Low quality context correctly scored < 0.7")
        else:
            print(f"   ⚠️  WARNING - Low quality context scored {score2:.2f} (expected < 0.7)")
            all_passed = False
    except Exception as e:
        print(f"   ❌ FAILED - Error: {e}")
        all_passed = False
    
    print()
    
    # Test 3: Partial context (borderline)
    print("=" * 70)
    print("TEST 3: Partial Quality Context (Incomplete)")
    print("=" * 70)
    
    question3 = "What are the learning objectives for CS101?"
    partial_context = """
CS101: Intro to Computer Science
- Learn programming
- Understand data structures
(Syllabus details not included)
"""
    
    print(f"Question: {question3}")
    print(f"Context Preview: {partial_context[:100]}...")
    
    try:
        score3, reasoning3 = await evaluate_func(question3, partial_context)
        print(f"\n📊 Result:")
        print(f"   Score: {score3:.2f}")
        print(f"   Reasoning: {reasoning3}")
        
        # Partial context is borderline - we just check it returns a valid score
        if 0.0 <= score3 <= 1.0:
            print("   ✅ PASSED - Valid score returned for partial context")
        else:
            print(f"   ❌ FAILED - Score {score3:.2f} is outside valid range [0.0, 1.0]")
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
        print("Your quality evaluator correctly:")
        print("  • Scores high-quality context ≥ 0.7")
        print("  • Scores low-quality context < 0.7")
        print("  • Returns valid scores in [0.0, 1.0] range")

    else:
        print("⚠️  SOME TESTS FAILED")
        print("Review the test output above and fix any issues.")
    print("=" * 70)
    
    return all_passed
