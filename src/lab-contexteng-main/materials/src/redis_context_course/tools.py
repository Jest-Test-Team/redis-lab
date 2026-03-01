"""
Tools for the Redis University Class Agent.

This module defines the tools that the agent can use to interact with
the course catalog and student data. These tools are used in the notebooks
throughout the course.
"""

from typing import Any, Dict, List, Optional

from agent_memory_client import MemoryAPIClient
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .course_manager import CourseManager
from .models import StudentProfile


# Tool Input Schemas
class SearchCoursesInput(BaseModel):
    """Input schema for searching courses."""

    query: str = Field(
        description="Natural language search query. Can be topics (e.g., 'machine learning'), "
        "characteristics (e.g., 'online courses'), or general questions "
        "(e.g., 'beginner programming courses')"
    )
    limit: int = Field(
        default=5,
        description="Maximum number of results to return. Default is 5. "
        "Use 3 for quick answers, 10 for comprehensive results.",
    )


class GetCourseDetailsInput(BaseModel):
    """Input schema for getting course details."""

    course_code: str = Field(
        description="Specific course code like 'CS101' or 'MATH201'"
    )


class CheckPrerequisitesInput(BaseModel):
    """Input schema for checking prerequisites."""

    course_code: str = Field(description="Course code to check prerequisites for")
    completed_courses: List[str] = Field(
        description="List of course codes the student has completed"
    )


# EXPERIMENTAL: Not currently used in notebooks or progressive_agents but available for external use
# Notebooks and agents create tools inline for educational clarity
# Course Tools
def create_course_tools(course_manager: CourseManager):
    """
    Create course-related tools.

    These tools are demonstrated in Section 2 notebooks.

    Note: This is experimental API surface. Notebooks and progressive_agents
    implement tools inline for educational purposes.
    """

    @tool(args_schema=SearchCoursesInput)
    async def search_courses(query: str, limit: int = 5) -> str:
        """
        Search for courses using semantic search based on topics, descriptions, or characteristics.

        Use this tool when students ask about:
        - Topics or subjects: "machine learning courses", "database courses"
        - Course characteristics: "online courses", "beginner courses", "3-credit courses"
        - General exploration: "what courses are available in AI?"

        Do NOT use this tool when:
        - Student asks about a specific course code (use get_course_details instead)
        - Student wants all courses in a department (use a filter instead)

        The search uses semantic matching, so natural language queries work well.

        Examples:
        - "machine learning courses" → finds CS401, CS402, etc.
        - "beginner programming" → finds CS101, CS102, etc.
        - "online data science courses" → finds online courses about data science
        """
        results = await course_manager.search_courses(query, limit=limit)

        if not results:
            return "No courses found matching your query."

        output = []
        for course in results:
            output.append(
                f"{course.course_code}: {course.title}\n"
                f"  Credits: {course.credits} | {course.format.value} | {course.difficulty_level.value}\n"
                f"  {course.description[:150]}..."
            )

        return "\n\n".join(output)

    @tool(args_schema=GetCourseDetailsInput)
    async def get_course_details(course_code: str) -> str:
        """
        Get detailed information about a specific course by its course code.

        Use this tool when:
        - Student asks about a specific course (e.g., "Tell me about CS101")
        - You need prerequisites for a course
        - You need full course details (schedule, instructor, etc.)

        Returns complete course information including description, prerequisites,
        schedule, credits, and learning objectives.
        """
        course = await course_manager.get_course(course_code)

        if not course:
            return f"Course {course_code} not found."

        prereqs = (
            "None"
            if not course.prerequisites
            else ", ".join(
                [
                    f"{p.course_code} (min grade: {p.min_grade})"
                    for p in course.prerequisites
                ]
            )
        )

        return f"""
{course.course_code}: {course.title}

Description: {course.description}

Details:
- Credits: {course.credits}
- Department: {course.department}
- Major: {course.major}
- Difficulty: {course.difficulty_level.value}
- Format: {course.format.value}
- Prerequisites: {prereqs}

Learning Objectives:
""" + "\n".join([f"- {obj}" for obj in course.learning_objectives])

    @tool(args_schema=CheckPrerequisitesInput)
    async def check_prerequisites(
        course_code: str, completed_courses: List[str]
    ) -> str:
        """
        Check if a student meets the prerequisites for a specific course.

        Use this tool when:
        - Student asks "Can I take [course]?"
        - Student asks about prerequisites
        - You need to verify eligibility before recommending a course

        Returns whether the student is eligible and which prerequisites are missing (if any).
        """
        course = await course_manager.get_course(course_code)

        if not course:
            return f"Course {course_code} not found."

        if not course.prerequisites:
            return f"✅ {course_code} has no prerequisites. You can take this course!"

        missing = []
        for prereq in course.prerequisites:
            if prereq.course_code not in completed_courses:
                missing.append(f"{prereq.course_code} (min grade: {prereq.min_grade})")

        if not missing:
            return f"✅ You meet all prerequisites for {course_code}!"

        return f"""❌ You're missing prerequisites for {course_code}:

Missing:
""" + "\n".join([f"- {p}" for p in missing])

    return [search_courses, get_course_details, check_prerequisites]


# EXPERIMENTAL: Not currently used in notebooks or progressive_agents but available for external use
# Memory Tools
def create_memory_tools(memory_client: MemoryAPIClient, session_id: str, user_id: str):
    """
    Create memory-related tools using the memory client's built-in LangChain integration.

    These tools are demonstrated in Section 3, notebook 04_memory_tools.ipynb.
    They give the LLM explicit control over memory operations.

    Note: This is experimental API surface. Progressive_agents implement memory
    tools inline for educational purposes.

    Args:
        memory_client: The memory client instance
        session_id: Session ID for the conversation
        user_id: User ID for the student

    Returns:
        List of LangChain StructuredTool objects for memory operations
    """
    from agent_memory_client.integrations.langchain import get_memory_tools

    return get_memory_tools(
        memory_client=memory_client, session_id=session_id, user_id=user_id
    )


# EXPERIMENTAL: Not currently used in notebooks or progressive_agents but available for external use
# Tool Selection Helpers (from Section 4, notebook 04_tool_optimization.ipynb)
def select_tools_by_keywords(query: str, all_tools: dict) -> List:
    """
    Select relevant tools based on query keywords.

    This is a simple tool filtering strategy demonstrated in Section 4.
    For production, consider using intent classification or hierarchical tools.

    Note: This is experimental API surface. Notebooks implement inline versions
    for educational purposes.

    Args:
        query: User's query
        all_tools: Dictionary mapping categories to tool lists

    Returns:
        List of relevant tools
    """
    query_lower = query.lower()

    # Search-related keywords
    if any(
        word in query_lower
        for word in ["search", "find", "show", "what", "which", "tell me about"]
    ):
        return all_tools.get("search", [])

    # Memory-related keywords
    elif any(
        word in query_lower
        for word in ["remember", "recall", "know about me", "preferences"]
    ):
        return all_tools.get("memory", [])

    # Default: return search tools
    else:
        return all_tools.get("search", [])


# EXPERIMENTAL: Tools from the original ClassAgent - available for building custom agents
def create_agent_tools(
    course_manager: CourseManager,
    memory_client: MemoryAPIClient,
    student_id: str,
    llm: Optional[ChatOpenAI] = None,
):
    """
    Create the full set of agent tools for a course advisor agent.

    This includes course tools, memory tools, and utility tools that were
    originally part of the ClassAgent implementation.

    Note: This is experimental API surface for building custom agents.

    Args:
        course_manager: CourseManager instance for course operations
        memory_client: MemoryAPIClient for memory operations
        student_id: Student ID for memory scoping
        llm: Optional ChatOpenAI instance for LLM-based operations

    Returns:
        List of LangChain tools
    """

    @tool
    async def search_courses_tool(
        query: str, filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Search course catalog by topic, department, or difficulty.

        Use this tool when users ask for specific courses or subjects, or when
        filtering by department, difficulty, or topic. Returns matching courses
        with detailed information.

        Args:
            query (str): Search terms like "programming", "CS", "beginner math".
            filters (Dict[str, Any], optional): Additional filters for department,
                difficulty, or other course attributes. Defaults to None.

        Returns:
            str: Formatted list of courses with codes, titles, descriptions,
                credits, and difficulty levels. Returns "No courses found" if
                no matches.
        """
        if not filters:
            filters = {}

        # Handle problematic abbreviations
        problematic_mappings = {
            " ds ": "Data Science",
            "ds classes": "Data Science",
            "ds courses": "Data Science",
        }

        query_lower = query.lower()
        for pattern, dept in problematic_mappings.items():
            if pattern in query_lower:
                filters["department"] = dept
                break

        courses = await course_manager.search_courses(query, filters=filters)

        if not courses:
            return "No courses found matching your criteria."

        result = f"Found {len(courses)} courses:\n\n"
        for course in courses[:10]:
            result += f"**{course.course_code}: {course.title}**\n"
            result += f"Department: {course.department} | Credits: {course.credits} | Difficulty: {course.difficulty_level.value}\n"
            result += f"Description: {course.description[:150]}...\n\n"

        return result

    @tool
    async def list_majors_tool() -> str:
        """List all university majors and degree programs.

        Use this tool when users ask about available majors, programs, or degrees.
        Returns a comprehensive list of all academic programs offered.

        Returns:
            str: Formatted list of majors with codes, departments, descriptions,
                and required credits.
        """
        try:
            major_keys = course_manager.redis_client.keys("major:*")

            if not major_keys:
                return "No majors found in the system."

            majors = []
            for key in major_keys:
                major_data = course_manager.redis_client.hgetall(key)
                if major_data:
                    major_info = {
                        "name": major_data.get("name", "Unknown"),
                        "code": major_data.get("code", "N/A"),
                        "department": major_data.get("department", "N/A"),
                        "description": major_data.get(
                            "description", "No description available"
                        ),
                        "required_credits": major_data.get("required_credits", "N/A"),
                    }
                    majors.append(major_info)

            if not majors:
                return "No major information could be retrieved."

            result = f"Available majors at Redis University ({len(majors)} total):\n\n"
            for major in majors:
                result += f"**{major['name']} ({major['code']})**\n"
                result += f"Department: {major['department']}\n"
                result += f"Required Credits: {major['required_credits']}\n"
                result += f"Description: {major['description']}\n\n"

            return result

        except Exception as e:
            return f"Error retrieving majors: {str(e)}"

    @tool
    async def get_recommendations_tool(query: str = "", limit: int = 3) -> str:
        """Generate personalized course recommendations based on user interests.

        Use this tool when users express interests or ask for course suggestions.
        Creates personalized recommendations and stores user interests in memory.

        Args:
            query (str, optional): User interests like "math and engineering".
            limit (int, optional): Maximum recommendations to return. Defaults to 3.

        Returns:
            str: Personalized course recommendations with details and reasoning.
        """
        interests = []
        if query:
            from agent_memory_client.models import ClientMemoryRecord

            memory = ClientMemoryRecord(
                text=f"Student expressed interest in: {query}",
                user_id=student_id,
                memory_type="semantic",
                topics=["interests", "preferences"],
            )
            await memory_client.create_long_term_memory([memory])
            interests = [interest.strip() for interest in query.split(" and ")]

        student_profile = StudentProfile(
            name=student_id,
            email=f"{student_id}@university.edu",
            interests=interests if interests else ["general"],
        )

        recommendations = await course_manager.recommend_courses(
            student_profile, query, limit
        )

        if not recommendations:
            return "No recommendations available at this time."

        result = f"Here are {len(recommendations)} personalized course recommendations:\n\n"
        for i, rec in enumerate(recommendations, 1):
            result += f"{i}. **{rec.course.course_code}: {rec.course.title}**\n"
            result += f"   Relevance: {rec.relevance_score:.2f} | Credits: {rec.course.credits}\n"
            result += f"   Reasoning: {rec.reasoning}\n"
            result += f"   Prerequisites met: {'Yes' if rec.prerequisites_met else 'No'}\n\n"

        return result

    @tool
    async def store_memory_tool(
        text: str,
        memory_type: str = "semantic",
        topics: Optional[List[str]] = None,
    ) -> str:
        """Store important student information in persistent long-term memory.

        Use this tool when the user shares preferences, goals, or important facts
        that should be remembered for future sessions.

        Args:
            text (str): Information to store in memory.
            memory_type (str, optional): Type of memory. Defaults to "semantic".
            topics (List[str], optional): Tags to categorize the memory.

        Returns:
            str: Confirmation message.
        """
        from agent_memory_client.models import ClientMemoryRecord

        memory = ClientMemoryRecord(
            text=text,
            user_id=student_id,
            memory_type=memory_type,
            topics=topics or [],
        )

        await memory_client.create_long_term_memory([memory])
        return f"Stored in long-term memory: {text}"

    @tool
    async def search_memories_tool(query: str, limit: int = 5) -> str:
        """Search stored memories using semantic search.

        Use this tool to recall previous preferences or information about the user.

        Args:
            query (str): Search terms for finding relevant memories.
            limit (int, optional): Maximum results to return. Defaults to 5.

        Returns:
            str: Formatted list of relevant memories.
        """
        from agent_memory_client.models import UserId

        results = await memory_client.search_long_term_memory(
            text=query, user_id=UserId(eq=student_id), limit=limit
        )

        if not results.memories:
            return "No relevant memories found."

        result = f"Found {len(results.memories)} relevant memories:\n\n"
        for i, memory in enumerate(results.memories, 1):
            result += f"{i}. {memory.text}\n"
            if memory.topics:
                result += f"   Topics: {', '.join(memory.topics)}\n"
            result += "\n"

        return result

    @tool
    async def summarize_user_knowledge_tool() -> str:
        """Summarize what the agent knows about the user.

        Searches through long-term memory to gather all stored information
        and organizes it into categories.

        Returns:
            str: Comprehensive summary of user information.
        """
        try:
            from agent_memory_client.filters import UserId

            results = await memory_client.search_long_term_memory(
                text="",
                user_id=UserId(eq=student_id),
                limit=50,
            )
        except Exception as e:
            return f"Error accessing stored information: {str(e)}"

        if not results.memories:
            return "I don't have any stored information about you yet."

        # Check for reset flag
        reset_memories = [
            m
            for m in results.memories
            if m.topics and "reset" in [t.lower() for t in m.topics]
        ]
        if reset_memories:
            return "You previously requested to start fresh. Please share your interests!"

        # Format memories
        if llm:
            return await _create_llm_summary(llm, results.memories)
        else:
            result = "Here's what I know about you:\n\n"
            result += "\n".join([f"• {memory.text}" for memory in results.memories])
            return result

    @tool
    async def clear_user_memories_tool(confirmation: str = "yes") -> str:
        """Clear or reset stored user information.

        Use this tool when users explicitly request to clear their information.

        Args:
            confirmation (str, optional): Must be "yes" to proceed.

        Returns:
            str: Confirmation message about the memory clearing operation.
        """
        if confirmation.lower() != "yes":
            return "Memory clearing cancelled."

        try:
            from agent_memory_client.filters import UserId

            memory_ids = []
            async for mem in memory_client.search_all_long_term_memories(
                text="",
                user_id=UserId(eq=student_id),
                batch_size=100,
            ):
                if getattr(mem, "memory_id", None):
                    memory_ids.append(mem.memory_id)

            deleted = 0
            if memory_ids:
                BATCH = 100
                for i in range(0, len(memory_ids), BATCH):
                    batch = memory_ids[i : i + BATCH]
                    try:
                        await memory_client.delete_long_term_memories(batch)
                        deleted += len(batch)
                    except Exception:
                        pass

            if deleted == 0:
                from agent_memory_client.models import ClientMemoryRecord

                reset_memory = ClientMemoryRecord(
                    text="User requested to clear/reset all previous information",
                    user_id=student_id,
                    memory_type="semantic",
                    topics=["reset", "clear", "fresh_start"],
                )
                await memory_client.create_long_term_memory([reset_memory])
                return "Marked profile as reset. Starting fresh."

            return f"Deleted {deleted} memories. Starting fresh."

        except Exception as e:
            return f"Error clearing information: {str(e)}"

    return [
        search_courses_tool,
        list_majors_tool,
        get_recommendations_tool,
        store_memory_tool,
        search_memories_tool,
        summarize_user_knowledge_tool,
        clear_user_memories_tool,
    ]


async def _create_llm_summary(llm: ChatOpenAI, memories) -> str:
    """Create an LLM-based summary of user information."""
    if not memories:
        return "I don't have any stored information about you yet."

    memory_info = []
    for memory in memories:
        topics_str = f" (Topics: {', '.join(memory.topics)})" if memory.topics else ""
        memory_info.append(f"- {memory.text}{topics_str}")

    memories_str = "\n".join(memory_info)

    prompt = f"""Based on the following stored information about a student, create a well-organized summary:

{memories_str}

Create a summary that:
1. Groups related information logically
2. Uses clear headings
3. Is conversational and helpful
4. Uses bullet points for easy reading

Start with "Here's what I know about you:" """

    try:
        from langchain_core.messages import HumanMessage

        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content
    except Exception:
        result = "Here's what I know about you:\n\n"
        result += "\n".join([f"• {memory.text}" for memory in memories])
        return result
