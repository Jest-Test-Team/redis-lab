"""
Tools for the Stage 4 ReAct Course Q&A Agent workflow.

This version includes:
- Hybrid search with NER
- Correct hierarchical data path
- FilterQuery for exact course code matching
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from redis_context_course import CourseManager
from redis_context_course.hierarchical_context import HierarchicalContextAssembler
from redis_context_course.hierarchical_models import (
    CourseDetails,
    CourseSummary,
    HierarchicalCourse,
)
from redis_context_course.models import Course
from redisvl.query import FilterQuery
from redisvl.query.filter import Tag

# Configure logger
logger = logging.getLogger("course-qa-workflow")

# Global variables that will be set during initialization
course_manager: Optional[CourseManager] = None
hierarchical_courses: List[HierarchicalCourse] = []
context_assembler = HierarchicalContextAssembler()


def initialize_tools(manager: CourseManager):
    """
    Initialize tools with required dependencies.

    Args:
        manager: CourseManager instance for course search
    """
    global course_manager, hierarchical_courses
    course_manager = manager

    # Load hierarchical courses with full syllabi
    # FIX: Correct path - go up 4 levels from tools.py to reach project root
    try:
        data_path = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "redis_context_course"
            / "data"
            / "hierarchical"
            / "hierarchical_courses.json"
        )
        if data_path.exists():
            with open(data_path) as f:
                data = json.load(f)
                hierarchical_courses = [
                    HierarchicalCourse(**course_data) for course_data in data["courses"]
                ]
            logger.info(
                f"Loaded {len(hierarchical_courses)} hierarchical courses for progressive disclosure"
            )
        else:
            logger.warning(f"Hierarchical courses not found at {data_path}")
    except Exception as e:
        logger.error(f"Failed to load hierarchical courses: {e}")


def transform_course_to_text(course: Course) -> str:
    """
    Transform course object to LLM-optimized text format.

    Args:
        course: Course object to transform

    Returns:
        LLM-friendly text representation
    """
    prereq_text = ""
    if course.prerequisites:
        prereq_codes = [p.course_code for p in course.prerequisites]
        prereq_text = f"\nPrerequisites: {', '.join(prereq_codes)}"

    objectives_text = ""
    if course.learning_objectives:
        objectives_text = f"\nLearning Objectives:\n" + "\n".join(
            f"  - {obj}" for obj in course.learning_objectives
        )

    course_text = f"""{course.course_code}: {course.title}
Department: {course.department}
Credits: {course.credits}
Level: {course.difficulty_level.value}
Format: {course.format.value}
Instructor: {course.instructor}{prereq_text}
Description: {course.description}{objectives_text}"""

    return course_text


def optimize_course_text(course: Course) -> str:
    """
    Create ultra-compact course description.

    Args:
        course: Course object to optimize

    Returns:
        Compact text representation
    """
    prereqs = (
        f" (Prereq: {', '.join([p.course_code for p in course.prerequisites])})"
        if course.prerequisites
        else ""
    )
    return (
        f"{course.course_code}: {course.title} - {course.description[:100]}...{prereqs}"
    )


def _filter_course_details(
    details: List[CourseDetails], info_types: List[str]
) -> List[CourseDetails]:
    """
    Filter course details to include only requested information.

    Args:
        details: List of CourseDetails objects
        info_types: Types of information requested

    Returns:
        Filtered CourseDetails with only requested information
    """
    if not info_types:
        return details

    filtered = []
    for detail in details:
        filtered_detail = CourseDetails(
            course_code=detail.course_code,
            title=detail.title,
            department=detail.department,
            credits=detail.credits,
            difficulty_level=detail.difficulty_level,
            format=detail.format,
            instructor=detail.instructor,
            semester=detail.semester,
            year=detail.year,
            max_enrollment=detail.max_enrollment,
            full_description=detail.full_description
            if "overview" in info_types or "description" in info_types
            else "",
            prerequisites=detail.prerequisites
            if "prerequisites" in info_types or "prerequisite" in info_types
            else [],
            learning_objectives=detail.learning_objectives
            if "syllabus" in info_types
            or "learning_objectives" in info_types
            or "objectives" in info_types
            else [],
            syllabus=detail.syllabus if "syllabus" in info_types else detail.syllabus,
            assignments=detail.assignments
            if "assignments" in info_types or "assignment" in info_types
            else [],
            tags=detail.tags,
        )
        filtered.append(filtered_detail)

    return filtered


class SearchCoursesInput(BaseModel):
    """Input schema for search_courses tool."""
    query: str = Field(description="Search query")
    intent: str = Field(default="GENERAL", description="Query intent")
    search_strategy: str = Field(default="hybrid", description="Search strategy")
    course_codes: Optional[List[str]] = Field(default=None, description="Specific course codes")
    information_type: Optional[List[str]] = Field(default=None, description="Info types to retrieve")
    departments: Optional[List[str]] = Field(default=None, description="Filter by department")


async def search_courses_async(
    query: str,
    top_k: int = 5,
    intent: str = "GENERAL",
    search_strategy: str = "semantic_only",
    extracted_entities: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Async search for courses using hybrid search with NER.

    Uses FilterQuery for exact course code matching.
    """
    global course_manager, hierarchical_courses

    if course_manager is None:
        return "Error: Course search not initialized."

    logger.info(f"🔍 Searching courses: query='{query}', intent={intent}, strategy={search_strategy}")

    basic_results = []
    extracted_entities = extracted_entities or {}

    # Handle exact match strategy with FilterQuery
    if search_strategy == "exact_match" and extracted_entities.get("course_codes"):
        logger.info(f"   Using exact match for course codes: {extracted_entities['course_codes']}")
        for course_code in extracted_entities["course_codes"]:
            # Use FilterQuery for exact course code matching
            filter_query = FilterQuery(
                filter_expression=Tag("course_code") == course_code,
                return_fields=[
                    "id", "course_code", "title", "description", "department",
                    "major", "difficulty_level", "format", "semester", "year",
                    "credits", "tags", "instructor", "max_enrollment",
                    "current_enrollment", "learning_objectives", "prerequisites",
                    "schedule", "created_at", "updated_at",
                ],
            )
            results = course_manager.vector_index.query(filter_query)
            result_list = results if isinstance(results, list) else results.docs

            if result_list:
                first_result = result_list[0]
                course_dict = first_result if isinstance(first_result, dict) else first_result.__dict__
                course = course_manager._dict_to_course(course_dict)
                if course:
                    basic_results.append(course)
                    logger.info(f"   Found exact match: {course_code}")
    else:
        # Fall back to semantic search
        logger.info(f"   Using semantic search")
        results = await course_manager.search_courses(query=query, limit=top_k)
        basic_results = results

    if not basic_results:
        return f"No courses found matching '{query}'."

    logger.info(f"   Found {len(basic_results)} courses")

    # Get hierarchical details
    course_codes_list = [c.course_code for c in basic_results]
    hierarchical_map = {hc.summary.course_code: hc for hc in hierarchical_courses}

    matched_courses = [hierarchical_map[code] for code in course_codes_list if code in hierarchical_map]
    logger.info(f"   Hierarchical data for {len(matched_courses)} courses")

    # Build context with progressive disclosure
    info_types = extracted_entities.get("information_type", [])

    if matched_courses:
        summaries = [c.summary for c in matched_courses]
        details = [c.details for c in matched_courses]

        if info_types:
            details = _filter_course_details(details, info_types)

        # Limit details to top 3 courses
        top_details = details[:min(3, len(details))]

        context = context_assembler.assemble_hierarchical_context(
            summaries=summaries,
            details=top_details,
            query=query,
        )
    else:
        # Fallback to basic format
        context = f"# Course Search Results for: {query}\n\n"
        for course in basic_results[:top_k]:
            context += transform_course_to_text(course) + "\n\n"

    logger.info(f"   Context: {len(context)} chars")
    return context


@tool(args_schema=SearchCoursesInput)
async def search_courses_hybrid(
    query: str,
    intent: str = "GENERAL",
    search_strategy: str = "hybrid",
    course_codes: Optional[List[str]] = None,
    information_type: Optional[List[str]] = None,
    departments: Optional[List[str]] = None,
) -> str:
    """
    Search the Redis University course catalog.

    Use exact_match strategy for specific course codes.
    Use hybrid strategy for topic-based searches.
    """
    extracted_entities = {
        "course_codes": course_codes or [],
        "departments": departments or [],
        "information_type": information_type or [],
    }

    # Determine strategy
    if course_codes and search_strategy != "semantic_only":
        search_strategy = "exact_match"

    return await search_courses_async(
        query=query,
        intent=intent,
        search_strategy=search_strategy,
        extracted_entities=extracted_entities,
    )

