"""
ReAct output parser for Stage 4 ReAct.

Parses LLM output in the Thought → Action → Observation format.
"""

import json
import re
from typing import Any, Dict, Optional


def parse_react_output(text: str) -> Dict[str, Optional[str]]:
    """
    Parse ReAct format output from LLM.

    Expected format:
        Thought: [reasoning]
        Action: [action_name]
        Action Input: [JSON input]

    Args:
        text: Raw LLM output text

    Returns:
        Dictionary with 'thought', 'action', and 'action_input' keys
    """
    # Extract Thought (everything between "Thought:" and "Action:")
    thought_match = re.search(
        r"Thought:\s*(.+?)(?=\nAction:|\Z)", text, re.DOTALL | re.IGNORECASE
    )

    # Extract Action (word after "Action:")
    action_match = re.search(r"Action:\s*(\w+)", text, re.IGNORECASE)

    # Extract Action Input - everything after "Action Input:" until end or next section
    # For FINISH actions, this can be multi-line plain text
    action_input_match = re.search(
        r"Action Input:\s*(.+?)(?=\nThought:|\nObservation:|\nAction:|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    return {
        "thought": thought_match.group(1).strip() if thought_match else None,
        "action": action_match.group(1).strip() if action_match else None,
        "action_input": (
            action_input_match.group(1).strip() if action_input_match else None
        ),
    }


def validate_action_input(action_input: str) -> Optional[Dict[str, Any]]:
    """
    Validate and parse action input as JSON.

    Args:
        action_input: Raw action input string

    Returns:
        Parsed JSON dict, or None if invalid
    """
    if not action_input:
        return None

    try:
        # Try to parse as JSON
        parsed = json.loads(action_input)
        return parsed
    except json.JSONDecodeError:
        # If not valid JSON, try to extract JSON-like content
        json_match = re.search(r"({.+}|\[.+\])", action_input, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        return None


def format_observation(result: str, max_length: int = 8000) -> str:
    """
    Format tool result as observation for ReAct loop.

    Args:
        result: Raw tool result
        max_length: Maximum length of observation (default 8000 chars ≈ 2000 tokens)
                   This should be large enough to include full syllabus data.

    Returns:
        Formatted observation string
    """
    if len(result) > max_length:
        result = result[:max_length] + "... [truncated]"
    return f"Observation: {result}"


def extract_final_answer(action_input: str) -> str:
    """
    Extract final answer from FINISH action input.

    Args:
        action_input: Action input for FINISH action

    Returns:
        Final answer text
    """
    parsed = validate_action_input(action_input)
    if parsed:
        if isinstance(parsed, dict):
            return parsed.get("answer", parsed.get("response", str(parsed)))
        return str(parsed)
    return action_input.strip()


def is_valid_react_output(text: str) -> bool:
    """
    Check if LLM output is valid ReAct format.

    Args:
        text: Raw LLM output

    Returns:
        True if valid ReAct format, False otherwise
    """
    parsed = parse_react_output(text)
    if not parsed["action"]:
        return False
    if parsed["action"].upper() != "FINISH" and not parsed["action_input"]:
        return False
    return True


def format_react_error(error: str) -> str:
    """
    Format error message for ReAct loop.

    Args:
        error: Error message

    Returns:
        Formatted error observation
    """
    return f"Observation: Error - {error}"

