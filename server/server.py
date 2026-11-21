"""Expose the existing CGPA tools over the Model Context Protocol."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastmcp import FastMCP

# Also allow `python server.py` when the terminal is already in server/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools import ALL_TOOLS, SEMESTER_HOURS 


# tools.py uses LangChain's @tool decorator. FastMCP needs the original Python
mcp = FastMCP("Current CGPA Guider", tools=[tool.func for tool in ALL_TOOLS])


@mcp.tool
def get_credit_hours(semesters: list[int]) -> float:
    """Add the scheduled credit hours for selected semesters (1-8).

    Use this for a specific future planning window, such as semesters [5, 6].
    The returned total can be passed to required_gpa_for_target.
    """
    if not semesters:
        raise ValueError("Provide at least one semester number.")
    if len(set(semesters)) != len(semesters):
        raise ValueError("Do not repeat a semester number.")
    if any(semester < 1 or semester > 8 for semester in semesters):
        raise ValueError("Semester numbers must be between 1 and 8.")

    return sum(SEMESTER_HOURS[semester] for semester in semesters)


def main() -> None:
    """Run the server over HTTP for local or hosted MCP clients."""
    mcp.run(
        transport="http",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", os.getenv("MCP_PORT", "8000"))),
    )


if __name__ == "__main__":
    main()
