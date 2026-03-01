"""
Test utility for validating ContextAssembler implementations.

This module provides a simple test function that students can use to verify
their context assembly strategies work correctly with real course data.
"""

import json
from pathlib import Path
from IPython.display import HTML, display
from redis_context_course.hierarchical_models import HierarchicalCourse, CourseSummary, CourseDetails


def print_expandable(title, content, preview_lines=5):
    """Print content in an expandable HTML format for Jupyter notebooks."""
    lines = content.split('\n')
    
    # Show preview as regular text
    preview = '\n'.join(lines[:preview_lines])
    print(f"\n{title}")
    print("─" * 70)
    print(preview)
    
    if len(lines) > preview_lines:
        print(f"\n... ({len(lines) - preview_lines} more lines)")
        
        # Create collapsible HTML section
        full_content = '\n'.join(lines).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html = f"""
        <details style="margin-top: 10px; border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
            <summary style="cursor: pointer; font-weight: bold; color: #0066cc;">
                💡 Click to expand full output ({len(lines)} lines)
            </summary>
            <pre style="margin-top: 10px; background-color: #f5f5f5; padding: 10px; border-radius: 3px; max-height: 500px; overflow-y: auto;">{full_content}</pre>
        </details>
        """
        display(HTML(html))
    else:
        print("─" * 70)


def test_assembler(assembler):
    """
    Test a ContextAssembler implementation.
    
    Args:
        assembler: Instance of ContextAssembler (subclass of HierarchicalContextAssembler)
        
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("🧪 Testing your ContextAssembler implementation...\n")
    
    # Setup: Load hierarchical courses from JSON (same as stage3 agent does)
    print("📚 Loading hierarchical course data...")
    data_path = (
        Path(__file__).resolve().parents[3]
        / "materials"
        / "src"
        / "redis_context_course"
        / "data"
        / "hierarchical"
        / "hierarchical_courses.json"
    )
    
    if not data_path.exists():
        print(f"❌ ERROR: Hierarchical courses file not found at {data_path}")
        print("   Make sure you're running this from the correct directory.")
        return False
    
    with open(data_path) as f:
        data = json.load(f)
        hierarchical_courses = [
            HierarchicalCourse(**course_data) for course_data in data["courses"]
        ]
    
    print(f"✅ Loaded {len(hierarchical_courses)} courses\n")
    
    # Extract summaries and details for testing (first 3 courses)
    test_courses = hierarchical_courses[:3]
    summaries = [course.summary for course in test_courses]
    details = [course.details for course in test_courses[:2]]  # Only first 2 for details
    
    all_passed = True
    
    # Test 1: Summary-only assembly
    print("=" * 70)
    print("TEST 1: Summary-Only Context Assembly")
    print("=" * 70)
    try:
        result = assembler.assemble_summary_only_context(
            summaries=summaries,
            query="computer science courses"
        )
        
        # Basic validation
        if not result:
            print("❌ FAILED: Method returned empty result")
            all_passed = False
        elif "Course Search Results" not in result:
            print("❌ FAILED: Missing expected header")
            all_passed = False
        elif f"Found {len(summaries)}" not in result:
            print("❌ FAILED: Missing course count")
            all_passed = False
        elif "Overview of All Matches" in result:
            print("❌ FAILED: Should NOT have 'Overview' section (that's for hierarchical)")
            all_passed = False
        elif "Detailed Information" in result:
            print("❌ FAILED: Should NOT have 'Detailed Information' section")
            all_passed = False
        else:
            print("✅ PASSED: Summary-only assembly works!")
            print("   ✓ Contains only course summaries (no detailed syllabi)")
            print(f"   ✓ Shows all {len(summaries)} courses in summary form")
            
            # Show expandable output
            print_expandable("📄 Output Preview:", result, preview_lines=12)
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("   Make sure you implemented assemble_summary_only_context()\n")
        all_passed = False
    
    # Test 2: Hierarchical assembly
    print("=" * 70)
    print("TEST 2: Hierarchical Context Assembly (Progressive Disclosure)")
    print("=" * 70)
    try:
        result = assembler.assemble_hierarchical_context(
            summaries=summaries,
            details=details,
            query="computer science course details"
        )
        
        # Basic validation
        if not result:
            print("❌ FAILED: Method returned empty result")
            all_passed = False
        elif "Overview of All Matches" not in result:
            print("❌ FAILED: Missing 'Overview of All Matches' section")
            all_passed = False
        elif "Detailed Information" not in result:
            print("❌ FAILED: Missing 'Detailed Information' section")
            all_passed = False
        else:
            # Show structure by extracting key sections
            lines = result.split('\n')
            
            # Find where Overview starts
            overview_start = next(i for i, line in enumerate(lines) if 'Overview of All Matches' in line)
            # Find where Detailed section starts
            details_start = next(i for i, line in enumerate(lines) if 'Detailed Information' in line)
            
            print("✅ PASSED: Hierarchical assembly works!")
            
            print("\n📋 Structure Check:")
            print(f"   ✓ Header section: lines 1-{overview_start}")
            print(f"   ✓ Overview section (all {len(summaries)} summaries): lines {overview_start+1}-{details_start}")
            print(f"   ✓ Details section (top {len(details)} courses): lines {details_start+1}-end")
            
            print("\n🎯 Key observations:")
            print("   • Summaries appear FIRST (breadth-first navigation)")
            print(f"   • All {len(summaries)} courses shown in summary form for context")
            print(f"   • Full details appear LAST for top {len(details)} courses (recency bias)")
            print("   • Progressive disclosure pattern in action!")
            
            # Show expandable output
            print_expandable("\n📄 Output Preview:", result, preview_lines=20)
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("   Make sure you implemented assemble_hierarchical_context()\n")
        all_passed = False
    
    # Final summary
    print("=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("   Your ContextAssembler is ready to connect to the agent!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("   Review the errors above and check your implementation.")
    print("=" * 70)
    
    return all_passed
