"""Create the Groq chat model used by the CGPA advisor agent."""

from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Keep credentials beside the agent, as described in the setup instructions.
load_dotenv(Path(__file__).parent / "agent" / ".env")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("Set GROQ_API_KEY in agent/.env before starting the agent.")

# GPT-OSS 120B is Groq's recommended replacement for the retired Llama 3.3 model.
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    api_key=api_key,
    temperature=0,
)
