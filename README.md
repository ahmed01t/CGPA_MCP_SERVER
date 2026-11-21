# Current CGPA Guider with MCP

The existing calculations remain in `tools.py`. `server/server.py` publishes
those same functions plus a small `get_credit_hours` helper for planning a
selected semester window. `agent/main.py` connects to any MCP URL.

## 1. Install dependencies

From the project root:

```powershell
python -m pip install -r requirements.txt
Copy-Item agent/.env.example agent/.env
```

Add your Groq key to `agent/.env`. For local use, keep
`MCP_URL=http://127.0.0.1:8000/mcp`.

## 2. Check the MCP server without an agent

Start the server in its own terminal first (`cd server; python server.py`),
then use the FastMCP CLI from the project root:

```powershell
fastmcp list http://127.0.0.1:8000/mcp
fastmcp call http://127.0.0.1:8000/mcp get_credit_hours semesters='[5,6]'
```

To run the server over HTTP, open a terminal:

```powershell
cd server
python server.py
```

The endpoint is `http://127.0.0.1:8000/mcp`.

## 3. Start the agent

From the project root, in another terminal:

```powershell
python -m agent.main
```

The agent uses async MCP calls and an async SQLite checkpointer. The database
`cgpa_memory.sqlite` stores chat threads after the program closes. Enter the
student's name to resume that thread. Commands are `/switch`, `/history`,
`/forget`, and `/quit`.

The agent streams model text as it arrives and prints progress when a tool
starts and finishes. If a network failure leaves a tool call without a result,
the agent adds a clear error result to the saved thread before the next turn.

## 4. Deploy on Prefect Horizon

Horizon deploys FastMCP servers from GitHub. Push this project to a GitHub
repository, connect the repository in Horizon, and set the server entry point
to `server/server.py:mcp`. Horizon reads `requirements.txt` to install the
Python packages. Its deployment guide has the current setup steps:
[Prefect Horizon deployment](https://gofastmcp.com/deployment/prefect-horizon).

After deployment, Horizon gives the server a URL. Set `MCP_URL` in
`agent/.env` to that URL with `/mcp` at the end. Horizon OAuth opens a browser
for sign-in the first time the agent connects. If you create a bearer/API key
instead, put it in `FASTMCP_KEY`; the agent will send it when it lists and
calls tools.

For example, a Horizon URL looks like
`https://your-server-name.fastmcp.app/mcp`. You can check it with:

```powershell
fastmcp list $env:MCP_URL --auth $env:FASTMCP_KEY
fastmcp call $env:MCP_URL get_credit_hours semesters='[5,6]' --auth $env:FASTMCP_KEY
```

The SQLite chat history stays on the computer running the agent; it is not
stored by the MCP server.
