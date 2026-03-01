"""
Setup and initialization for the Stage 3 Course Q&A Agent.

Initializes CourseManager, Redis, and other dependencies.
Uses the hierarchical_courses index (separate from stages 1 & 2).
"""

import json
import os
from pathlib import Path
from typing import Optional

from redis_context_course import CourseManager
from redis_context_course.redis_config import RedisConfig
from redis_context_course.scripts.generate_courses_from_hierarchical import hierarchical_to_course
from redis_context_course.scripts.ingest_courses import CourseIngestionPipeline

# Stage 3+ uses the hierarchical_courses index
# This keeps hierarchical data separate from the basic courses index used by Stages 1 & 2
HIERARCHICAL_INDEX = "hierarchical_courses"
HIERARCHICAL_DATA_PATH = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "redis_context_course"
    / "data"
    / "hierarchical"
    / "hierarchical_courses.json"
)


async def load_courses_if_needed(
    course_manager: CourseManager, force_reload: bool = False
) -> int:
    """
    Load hierarchical courses into Redis if they don't exist or if force_reload is True.

    Args:
        course_manager: CourseManager instance
        force_reload: If True, clear existing courses and reload

    Returns:
        Number of courses loaded
    """
    existing_courses = await course_manager.get_all_courses()

    if existing_courses and not force_reload:
        print(f"📚 Found {len(existing_courses)} existing courses in Redis")
        return len(existing_courses)

    if not existing_courses:
        print("📦 No courses found in Redis. Loading hierarchical courses...")
    else:
        print("🔄 Force reload requested. Reloading hierarchical courses...")

    try:
        # Clear existing data if needed
        if force_reload or not existing_courses:
            print("🧹 Clearing existing course data...")
            ingestion = CourseIngestionPipeline(config=course_manager._config)
            ingestion.clear_existing_data()

        # Load courses from hierarchical JSON file
        print(f"📖 Loading courses from {HIERARCHICAL_DATA_PATH}...")
        
        with open(HIERARCHICAL_DATA_PATH, 'r') as f:
            data = json.load(f)
        
        courses_data = data.get("courses", [])
        print(f"Found {len(courses_data)} courses in file")
        
        # Convert hierarchical courses to Course objects and store
        loaded = 0
        for h_course in courses_data:
            try:
                # Convert to Course format
                course_dict = hierarchical_to_course(h_course)
                
                # Create Course object
                from redis_context_course.models import Course
                course = Course(**course_dict)
                
                # Store using CourseManager (uses configured embeddings)
                await course_manager.store_course(course)
                loaded += 1
                
                if loaded % 10 == 0:
                    print(f"  Loaded {loaded}/{len(courses_data)} courses...")
            except Exception as e:
                print(f"⚠️ Failed to load course {h_course.get('id', 'unknown')}: {e}")
                continue

        print(f"✅ Loaded {loaded} hierarchical courses into Redis")
        return loaded

    except Exception as e:
        print(f"❌ Failed to load courses: {e}")
        raise


async def initialize_course_manager(
    redis_url: Optional[str] = None, auto_load: bool = True, force_reload: bool = False
) -> CourseManager:
    """
    Initialize the CourseManager for course search.

    Uses the hierarchical_courses index which contains courses
    with full syllabus data (separate from the basic courses index
    used by Stages 1 & 2).

    Args:
        redis_url: Redis connection URL (defaults to env var REDIS_URL)
        auto_load: If True, automatically load courses if they don't exist
        force_reload: If True, clear existing courses and reload from hierarchical data

    Returns:
        Initialized CourseManager instance
    """
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

    print(f"Initializing CourseManager with Redis")
    print(f"📇 Using index: {HIERARCHICAL_INDEX}")

    try:
        # Create config with hierarchical_courses index (separate from stages 1 & 2)
        config = RedisConfig(
            redis_url=redis_url,
            vector_index_name=HIERARCHICAL_INDEX
        )

        # Create CourseManager instance with custom config
        course_manager = CourseManager(config=config)

        # Load courses if needed
        if auto_load:
            course_count = await load_courses_if_needed(course_manager, force_reload=force_reload)
            print(f"✅ CourseManager initialized with {course_count} courses")
        else:
            # Just verify connection
            all_courses = await course_manager.get_all_courses()
            print(f"✅ CourseManager initialized with {len(all_courses)} courses")

        return course_manager

    except Exception as e:
        print(f"❌ Failed to initialize CourseManager: {e}")
        raise


async def cleanup_courses(course_manager: CourseManager):
    """
    Clean up courses from Redis.

    Args:
        course_manager: CourseManager instance
    """
    print("🧹 Cleaning up courses from Redis...")

    try:
        ingestion = CourseIngestionPipeline(config=course_manager._config)
        ingestion.clear_existing_data()
        print("✅ Courses cleaned up successfully")
    except Exception as e:
        print(f"❌ Failed to cleanup courses: {e}")


async def setup_agent(auto_load_courses: bool = True, force_reload: bool = False):
    """
    Complete setup for the Stage 3 Course Q&A Agent.

    Args:
        auto_load_courses: If True, automatically load courses if they don't exist
        force_reload: If True, clear existing courses and reload from hierarchical data

    Returns:
        CourseManager instance
    """
    print("=" * 80)
    print("Setting up Stage 3 Course Q&A Agent")
    print("=" * 80)

    # Initialize CourseManager (will auto-load courses if needed)
    course_manager = await initialize_course_manager(auto_load=auto_load_courses, force_reload=force_reload)

    print("=" * 80)
    print("✅ Stage 3 Course Q&A Agent setup complete")
    print("=" * 80)

    return course_manager
