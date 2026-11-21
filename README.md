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

## 4. Use a hosted server

`render.yaml` prepares a free Render web service. Push this project to a Git
provider, connect the repository in Render, and create the service from the
blueprint. Render supplies the public service URL; FastMCP's HTTP endpoint is
that URL plus `/mcp`. Set `MCP_URL` in `agent/.env` to that full endpoint.

Render's free web services can be used at no charge, but they spin down after
15 minutes without traffic and use an ephemeral filesystem. This MCP server
does not store conversation memory; the agent's SQLite file remains local to
the agent. See [Render's free service limits](https://render.com/docs/free).

The included Render service is unauthenticated to keep the assignment setup
simple. Anyone with its public URL can call the exposed tools, including the
report-saving tool. For private use, configure authentication at the hosting
gateway and set `FASTMCP_KEY` in `agent/.env` to the matching bearer token.
