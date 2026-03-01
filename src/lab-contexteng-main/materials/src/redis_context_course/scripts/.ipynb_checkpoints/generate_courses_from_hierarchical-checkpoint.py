#!/usr/bin/env python3
"""
Generate courses.json from hierarchical_courses.json.

This ensures Redis only contains courses that have full hierarchical data
(syllabi, assignments, etc.), avoiding the "No hierarchical data" warnings.
"""

import json
from datetime import datetime, time
from pathlib import Path
from typing import Any, Dict, List

from ulid import ULID


def generate_schedule(format_type: str) -> Dict[str, Any] | None:
    """Generate a course schedule based on format."""
    if format_type == "online":
        return None  # Online courses typically don't have fixed schedules
    
    # In-person or hybrid courses have schedules
    return {
        "days": ["tuesday", "thursday"],
        "start_time": "10:00",
        "end_time": "11:30",
        "location": "Room 101"
    }


def hierarchical_to_course(h_course: Dict[str, Any]) -> Dict[str, Any]:
    """Convert hierarchical course data to Course model format."""
    summary = h_course["summary"]
    details = h_course["details"]
    
    # Convert prerequisites from hierarchical format
    prerequisites = []
    if details.get("prerequisites"):
        for prereq in details["prerequisites"]:
            if isinstance(prereq, dict):
                prerequisites.append(prereq)
            else:
                # It's just a course code string
                prerequisites.append({
                    "course_code": prereq,
                    "course_title": f"Prerequisite {prereq}",
                    "minimum_grade": "C",
                    "can_be_concurrent": False
                })
    
    # Determine major from department
    dept = summary.get("department", "Computer Science")
    major_map = {
        "Computer Science": "Computer Science",
        "Mathematics": "Mathematics",
        "Data Science": "Data Science",
        "Engineering": "Engineering",
    }
    major = major_map.get(dept, dept)
    
    return {
        "id": str(ULID()),
        "course_code": summary["course_code"],
        "title": summary["title"],
        "description": details.get("full_description", summary.get("short_description", "")),
        "credits": summary["credits"],
        "difficulty_level": summary["difficulty_level"],
        "format": summary["format"],
        "department": dept,
        "major": major,
        "prerequisites": prerequisites,
        "schedule": generate_schedule(summary["format"]),
        "semester": details.get("semester", "fall"),
        "year": details.get("year", 2024),
        "instructor": summary["instructor"],
        "max_enrollment": details.get("max_enrollment", 30),
        "current_enrollment": 0,
        "tags": summary.get("tags", []) + details.get("tags", []),
        "learning_objectives": details.get("learning_objectives", []),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


def main():
    """Generate courses.json from hierarchical_courses.json."""
    # Paths
    data_dir = Path(__file__).parent.parent / "data"
    hierarchical_path = data_dir / "hierarchical" / "hierarchical_courses.json"
    output_path = data_dir / "courses.json"
    
    # Load hierarchical courses
    print(f"Loading hierarchical courses from: {hierarchical_path}")
    with open(hierarchical_path) as f:
        hierarchical_data = json.load(f)
    
    # Convert to Course format
    courses = []
    seen_codes = set()  # Track unique course codes
    
    for h_course in hierarchical_data["courses"]:
        code = h_course["summary"]["course_code"]
        if code in seen_codes:
            print(f"  Skipping duplicate: {code}")
            continue
        seen_codes.add(code)
        
        course = hierarchical_to_course(h_course)
        courses.append(course)
        print(f"  Converted: {code} - {course['title']}")
    
    # Save courses.json
    print(f"\nSaving {len(courses)} courses to: {output_path}")
    with open(output_path, "w") as f:
        json.dump({"courses": courses}, f, indent=2, default=str)
    
    print(f"\n✅ Generated courses.json with {len(courses)} courses")
    print(f"   All courses have matching hierarchical data (syllabi, assignments)")


if __name__ == "__main__":
    main()
