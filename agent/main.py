"""Terminal CGPA advisor with streaming and saved conversations."""

import asyncio
import sys
from pathlib import Path

# Also allow `python main.py` when the terminal is already in agent/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent

from agent.mcp_tools import load_mcp_tools
from llm import llm


SYSTEM_PROMPT = """You are an academic advisor for PUCIT BS(CS) students.

Rules:
- Use tools for every calculation. Never do arithmetic in your head.
- Do not guess marks, credits, CGPA, target, or semester. Ask for missing details.
- Ask for only one or two missing details at a time.
- MD-001 and MD-002 are non-credit. Quran Translation courses have 0.5 credits
  and count toward GPA.
- For an unreachable target, check one semester, then two, then three, and so
  on. Use get_credit_hours for each window and required_gpa_for_target to check
  it. Do not claim a plan is achievable if it needs a GPA above 4.0.
- Offer to save a report only after a useful result. Call save_report only if
  the student explicitly asks or agrees.
- If a tool fails, say so and do not claim it succeeded."""


def config_for(name: str) -> dict:
    """Use the student's name as the saved conversation ID."""
    return {"configurable": {"thread_id": name}}


async def list_threads(memory) -> list[str]:
    """Find names of conversations already saved in SQLite."""
    names = set()
    async for saved in memory.alist(None):
        name = saved.config.get("configurable", {}).get("thread_id")
        if name:
            names.add(name)
    return sorted(names, key=str.casefold)


async def repair_tool_replies(app, config: dict) -> int:
    """Close saved tool calls that were interrupted before returning a result.

    A model API expects one ToolMessage for every assistant tool call. If the
    MCP server stopped mid-call, this adds an error result so later turns work.
    """
    state = await app.aget_state(config)
    messages = state.values.get("messages", [])

    answered = {
        message.tool_call_id
        for message in messages
        if isinstance(message, ToolMessage)
    }
    missing = []

    for message in messages:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                call_id = call.get("id")
                if call_id and call_id not in answered:
                    missing.append(
                        ToolMessage(
                            tool_call_id=call_id,
                            name=call.get("name", "tool"),
                            content=(
                                "The MCP server stopped before this tool returned. "
                                "Explain that the result is unavailable."
                            ),
                        )
                    )
                    answered.add(call_id)

    if missing:
        await app.aupdate_state(config, {"messages": missing})
    return len(missing)


async def show_history(app, config: dict) -> None:
    """Print the messages saved for the selected student."""
    state = await app.aget_state(config)
    messages = state.values.get("messages", [])
    if not messages:
        print("No saved messages yet.")
        return

    for message in messages:
        text = message.content
        if isinstance(text, list):
            text = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in text
            )
        if text:
            label = {"human": "Student", "ai": "Advisor", "tool": "Tool"}.get(
                message.type, message.type.title()
            )
            print(f"{label}: {text}")


async def chat(app, config: dict, text: str) -> None:
    """Send one message and print model text and tool progress as it happens."""
    await repair_tool_replies(app, config)
    print("Advisor: ", end="", flush=True)

    try:
        async for event in app.astream(
            {"messages": [HumanMessage(content=text)]},
            config,
            stream_mode=["updates", "messages"],
            version="v2",
        ):
            if event["type"] == "messages":
                token, details = event["data"]
                if details.get("langgraph_node") == "agent":
                    content = token.content
                    if isinstance(content, str):
                        print(content, end="", flush=True)
                    elif isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                print(part.get("text", ""), end="", flush=True)
            else:
                for node, update in event["data"].items():
                    if node == "agent":
                        for message in update.get("messages", []):
                            for call in getattr(message, "tool_calls", []):
                                print(f"\n[Using {call['name']}…]", flush=True)
                    elif node == "tools":
                        for result in update.get("messages", []):
                            print(f"\n[{result.name} finished]", flush=True)
        print()
    except Exception as error:
        repaired = await repair_tool_replies(app, config)
        print(f"\nI couldn't finish that step: {error}")
        if repaired:
            print("I saved an error result, so you can continue chatting.")


async def main() -> None:
    """Start the MCP-backed advisor and its saved chat threads."""
    import os

    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
    url = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")
    try:
        tools = await load_mcp_tools(url, os.getenv("FASTMCP_KEY"))
    except Exception as error:
        raise RuntimeError(
            f"Can't connect to the MCP server at {url}. Start it and try again."
        ) from error

    async with AsyncSqliteSaver.from_conn_string("cgpa_memory.sqlite") as memory:
        app = create_react_agent(
            model=llm,
            tools=tools,
            prompt=SYSTEM_PROMPT,
            checkpointer=memory,
        )

        print("PUCIT GPA & CGPA Advisor (type /quit to stop)\n")
        names = await list_threads(memory)
        print("Saved chats: " + (", ".join(names) if names else "none"))

        name = input("Student name: ").strip()
        while not name:
            name = input("Please enter a name: ").strip()
        config = config_for(name)
        print("Commands: /switch, /history, /forget, /quit")

        while True:
            try:
                text = input(f"{name}> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not text:
                continue
            if text == "/quit":
                break
            if text == "/history":
                await show_history(app, config)
            elif text == "/forget":
                await memory.adelete_thread(name)
                print(f"Forgot {name}'s saved chat.")
            elif text == "/switch":
                new_name = input("Switch to whose chat? ").strip()
                if new_name:
                    name = new_name
                    config = config_for(name)
                    print(f"Switched to {name}'s chat.")
            else:
                await chat(app, config, text)


if __name__ == "__main__":
    asyncio.run(main())
