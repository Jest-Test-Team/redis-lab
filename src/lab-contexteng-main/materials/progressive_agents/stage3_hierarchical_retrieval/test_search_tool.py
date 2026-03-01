"""
Test utility for the search_courses_tool implementation.

This module tests that the search tool was correctly implemented the tool with:
- Proper input schema (SearchCoursesInput)
- Correct tool decorator usage
- Intent-based logic that returns appropriate messages
"""


async def test_search_courses_tool(tool_func):
    """
    Test the search_courses_tool implementation.
    Returns markdown with collapsible sections for detailed output.
    
    Args:
        tool_func: The search_courses_tool function
    """
    import logging
    from IPython.display import Markdown, display
    
    # Temporarily suppress the course-qa-workflow logger for clean test output
    course_logger = logging.getLogger("course-qa-workflow")
    # Temporarily suppress all loggers for clean test output
    logging.disable(logging.CRITICAL)
    
    test_cases = [
        ("Test 1: GENERAL intent", "I'm interested in machine learning courses", "GENERAL"),
        ("Test 2: SYLLABUS_OBJECTIVES intent", "Can you show me the syllabus for CS101?", "SYLLABUS_OBJECTIVES"),
        ("Test 3: ASSIGNMENTS intent", "What homework assignments are in CS101?", "ASSIGNMENTS"),
        ("Test 4: PREREQUISITES intent", "What are the prerequisites for CS101?", "PREREQUISITES"),
        ("Test 5: Default intent", "I'd like to learn about data science courses", None),
    ]
    
    # Build markdown output
    markdown_parts = [
        "## 🧪 Testing search_courses_tool Implementation\n",
        "### 📊 Test Results Summary:\n"
    ]
    
    passed_count = 0
    
    for test_name, query, intent in test_cases:
        try:
            if intent:
                result = await tool_func.ainvoke({"query": query, "intent": intent})
            else:
                result = await tool_func.ainvoke({"query": query})
            
            passed = "Course Search Results" in result or "Found" in result
            if passed:
                passed_count += 1
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            intent_display = intent or "GENERAL (default)"
            
            # Add summary
            markdown_parts.append(f"**{status}** - {test_name}")
            markdown_parts.append(f"- Query: {query}")
            markdown_parts.append(f"- Intent: {intent_display}")
            markdown_parts.append(f"- Output: {len(result)} characters\n")
            
            # Add collapsible section
            markdown_parts.append(f"<details>")
            markdown_parts.append(f"<summary><strong>View Full Output</strong></summary>\n")
            markdown_parts.append(f"```")
            markdown_parts.append(result)
            markdown_parts.append(f"```")
            markdown_parts.append(f"</details>\n")
            
        except Exception as e:
            markdown_parts.append(f"**❌ FAILED** - {test_name}")
            error_msg = str(e)
            if "course_manager" in error_msg:
                error_msg += " - Make sure you ran the Setup cell at the beginning of the notebook"
            markdown_parts.append(f"- Error: `{error_msg}`\n")
    
    markdown_parts.append("\n---\n")
    markdown_parts.append(f"**Results: {passed_count}/{len(test_cases)} tests passed**\n")
    
    if passed_count == len(test_cases):
        markdown_parts.append("\n🎉 **All tests passed!**\n")
    else:
        markdown_parts.append("\n⚠️  **Some tests failed - check details above**\n")
    
    markdown_parts.append("\n### 💡 Key Observations:\n")
    markdown_parts.append("- **GENERAL intent** → Returns summaries only (low cost)\n")
    markdown_parts.append("- **SYLLABUS_OBJECTIVES/ASSIGNMENTS** → Returns full details (high cost)\n")
    markdown_parts.append("- **PREREQUISITES** → Returns summaries only (prereq codes included)\n")
    markdown_parts.append("- The tool adapts its behavior based on the intent parameter\n")
    
    # Display the markdown
    display(Markdown("\n".join(markdown_parts)))
