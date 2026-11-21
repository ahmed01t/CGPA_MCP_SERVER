"""Compatibility entry point; the implementation lives in server/server.py."""

import os

from server.server import main, mcp


if __name__ == "__main__":
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
    main()
