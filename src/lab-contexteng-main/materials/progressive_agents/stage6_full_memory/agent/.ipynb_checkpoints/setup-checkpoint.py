"""
Setup and initialization for the Memory-Augmented Course Q&A Agent.

Initializes CourseManager, Redis, Agent Memory Server client, and other dependencies.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

from agent_memory_client import MemoryAPIClient, MemoryClientConfig

from redis_context_course import CourseManager
from redis_context_course.redis_config import RedisConfig
from redis_context_course.scripts.generate_courses import CourseGenerator
from redis_context_course.scripts.ingest_courses import CourseIngestionPipeline
from redis_context_course.scripts.generate_courses_from_hierarchical import hierarchical_to_course

# Progressive agents use the hierarchical_courses index
# This index contains only courses with full syllabus data
PROGRESSIVE_AGENTS_INDEX = "hierarchical_courses"
HIERARCHICAL_DATA_PATH = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "redis_context_course"
            / "data"
            / "hierarchical"
            / "hierarchical_courses.json"
        )

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("course-qa-setup")


def initialize_memory_client(
    base_url: Optional[str] = None, namespace: str = "course_qa_agent"
) -> MemoryAPIClient:
    """
    Initialize Agent Memory Server client.

    Args:
        base_url: Agent Memory Server URL (defaults to env var AGENT_MEMORY_URL)
        namespace: Namespace for memory storage

    Returns:
        Initialized MemoryAPIClient instance
    """
    if base_url is None:
        base_url = os.getenv("AGENT_MEMORY_URL", "http://agent-memory-server:8000")

    logger.info(f"Initializing Agent Memory Server client: {base_url}")

    try:
        config = MemoryClientConfig(
            base_url=base_url,
            default_namespace=namespace,
        )
        memory_client = MemoryAPIClient(config=config)

        logger.info(f"✅ Agent Memory Server client initialized")
        return memory_client

    except Exception as e:
        logger.error(f"Failed to initialize memory client: {e}")
        raise


async def load_courses_if_needed(
    course_manager: CourseManager, force_reload: bool = False
) -> int:
    """
    Load courses into Redis if they don't exist or if force_reload is True.

    Args:
        course_manager: CourseManager instance
        force_reload: If True, clear existing courses and reload

    Returns:
        Number of courses loaded
    """
    # Check if courses already exist
    existing_courses = await course_manager.get_all_courses()

    # If courses exist and we're not forcing reload, just return the count
    if existing_courses and not force_reload:
        logger.info(f"📚 Found {len(existing_courses)} existing courses in Redis")
        return len(existing_courses)

    # If we get here, either no courses exist OR force_reload is True
    if not existing_courses:
        logger.info(
            "📦 No courses found in Redis. Loading courses from hierarchical data..."
        )
    else:
        logger.info("🔄 Force reload requested. Reloading courses...")

    try:
        # Clear existing data if force_reload (or if empty, to be safe)
        ingestion = CourseIngestionPipeline(config=course_manager._config)
        if force_reload or not existing_courses:
            logger.info("🧹 Clearing existing course data...")
            ingestion.clear_existing_data()
        
        # Load courses from hierarchical JSON file
        logger.info(f"📖 Loading courses from {HIERARCHICAL_DATA_PATH}...")
        
        with open(HIERARCHICAL_DATA_PATH, 'r') as f:
            data = json.load(f)
        
        courses_data = data.get("courses", [])
        logger.info(f"Found {len(courses_data)} courses in file")
        
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
                    logger.info(f"  Loaded {loaded}/{len(courses_data)} courses...")
                    
            except Exception as e:
                logger.warning(f"  Failed to load course {h_course.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"✅ Successfully loaded {loaded}/{len(courses_data)} courses into Redis")
        return loaded

    except Exception as e:
        logger.error(f"Failed to load courses: {e}")
        raise


async def initialize_course_manager(
    redis_url: Optional[str] = None, auto_load: bool = True
) -> CourseManager:
    """
    Initialize the CourseManager for course search.

    Uses the hierarchical_courses index which contains only courses
    with full syllabus data (matching hierarchical_courses.json).

    Args:
        redis_url: Redis connection URL (defaults to env var REDIS_URL)
        auto_load: If True, automatically load courses if they don't exist

    Returns:
        Initialized CourseManager instance
    """
    if redis_url is None:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

    logger.info(f"Initializing CourseManager with Redis URL: {redis_url}")
    logger.info(f"📇 Using index: {PROGRESSIVE_AGENTS_INDEX}")

    try:
        # Create config with hierarchical_courses index
        config = RedisConfig(
            redis_url=redis_url,
            vector_index_name=PROGRESSIVE_AGENTS_INDEX
        )

        # Create CourseManager instance with custom config
        course_manager = CourseManager(config=config)

        # Load courses if needed
        if auto_load:
            course_count = await load_courses_if_needed(course_manager)
            logger.info(f"✅ CourseManager initialized with {course_count} courses")
        else:
            # Just verify connection
            all_courses = await course_manager.get_all_courses()
            logger.info(f"✅ CourseManager initialized with {len(all_courses)} courses")

        return course_manager

    except Exception as e:
        logger.error(f"Failed to initialize CourseManager: {e}")
        raise


async def cleanup_courses(course_manager: CourseManager):
    """
    Clean up courses from Redis.

    Args:
        course_manager: CourseManager instance
    """
    logger.info("🧹 Cleaning up courses from Redis...")

    try:
        ingestion = CourseIngestionPipeline(config=course_manager._config)
        ingestion.clear_existing_data()
        logger.info("✅ Courses cleaned up successfully")
    except Exception as e:
        logger.error(f"Failed to cleanup courses: {e}")


async def setup_agent(
    auto_load_courses: bool = True,
) -> Tuple[CourseManager, MemoryAPIClient]:
    """
    Complete setup for the Memory-Augmented Course Q&A Agent.

    Args:
        auto_load_courses: If True, automatically load courses if they don't exist

    Returns:
        Tuple of (course_manager, memory_client)
    """
    logger.info("=" * 80)
    logger.info("Setting up Memory-Augmented Course Q&A Agent")
    logger.info("=" * 80)

    # Initialize CourseManager (will auto-load courses if needed)
    course_manager = await initialize_course_manager(auto_load=auto_load_courses)

    # Initialize Agent Memory Server client
    memory_client = initialize_memory_client()

    logger.info("=" * 80)
    logger.info("✅ Memory-Augmented Course Q&A Agent setup complete")
    logger.info("=" * 80)

    return course_manager, memory_client
