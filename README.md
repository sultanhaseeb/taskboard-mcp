# Taskboard MCP

A small [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for managing tasks. Tasks are stored in a SQLite database named `tasks.db` beside `server.py`. The database and `tasks` table are created when a task tool first needs them.

## Requirements

- Python 3.11 or newer
- Node.js and `npx` to use MCP Inspector
- ChatGPT Desktop for a local STDIO connection, or an HTTPS tunnel/deployed endpoint for ChatGPT on the web

## Set up

From this repository's directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

## MCP concepts in this server

MCP servers can expose tools, resources, and prompts. They have different roles:

| MCP feature | This server | Use it for |
| --- | --- | --- |
| Tool | `say_hello`, `add_task`, `list_tasks`, `complete_task` | An action the model can choose to call, such as listing or changing tasks. |
| Resource | `taskboard://tasks` | Task data a client reads and can provide as context. A resource is read by the client; it is not a tool call. |
| Prompt | `plan_open_tasks(goal)` | A reusable prompt template. The client supplies a goal and sends the resulting message to the model. The prompt itself does not call tools or change tasks. |

Completed tasks are stored with status `complete`. The `list_tasks` filter uses the value `completed` for those tasks.

## Run the server

For an MCP client that launches local processes, the server uses STDIO by default:

```bash
python server.py
```

The process waits for MCP messages on standard input; it does not display a taskboard page. An MCP client such as ChatGPT Desktop or MCP Inspector can launch this process for you. If configuring a client manually, use the absolute path to `.venv/bin/python` as the command and the absolute path to `server.py` as its argument. Use the virtual environment's Python so it can find the installed dependencies.

For Streamable HTTP, run:

```bash
python server.py --http
```

The MCP endpoint is `http://127.0.0.1:8000/mcp`. Keep this process running while a client uses it. Opening `/mcp` directly in a browser is not a taskboard page and may show a protocol error.

## Read the resource from the CLI

`client.py` launches `server.py` over STDIO, reads `taskboard://tasks`, and prints the resource contents. Run it from the repository directory:

```bash
.venv/bin/python client.py
```

You do not need to start the server separately for this command. On Windows, use `.venv\Scripts\python.exe client.py`.

## Try the server with MCP Inspector

Run this from the repository directory after installing the dependencies:

```bash
npx @modelcontextprotocol/inspector@latest .venv/bin/python server.py
```

Inspector launches the server over STDIO and opens its browser interface. Use the tabs to explore each MCP feature:

- **Tools:** call `list_tasks`, `add_task`, or another tool.
- **Resources:** select `taskboard://tasks` and read it.
- **Prompts:** select `plan_open_tasks` and enter a `goal`, such as `Prepare the demo by Friday`.

Alternatively, to inspect the HTTP transport, start `python server.py --http` in one terminal and launch Inspector with `npx @modelcontextprotocol/inspector@latest` in another. In Inspector, choose **Streamable HTTP** and connect to `http://127.0.0.1:8000/mcp`.

## Connect to ChatGPT

Choose the connection that matches where you use ChatGPT.

### ChatGPT Desktop: local STDIO

ChatGPT Desktop can run a local MCP server over STDIO. In the custom MCP connection form, use:

| Field | Value |
| --- | --- |
| Name | `taskboard-mcp` |
| Type | **STDIO** |
| Command to launch | Absolute path to `.venv/bin/python` |
| Argument | Absolute path to this repository's `server.py` |
| Environment variables | Leave blank |

For example, if the repository is at `/Users/your-name/taskboard-mcp`, set the command to `/Users/your-name/taskboard-mcp/.venv/bin/python` and the argument to `/Users/your-name/taskboard-mcp/server.py`. Use the actual absolute paths on your computer. ChatGPT Desktop launches the server, so you do not need to run `python server.py` separately. Local MCP apps are available in ChatGPT Desktop, not ChatGPT on the web or mobile.

Start a new chat, select or `@`-mention `taskboard-mcp`, and try:

> Use the taskboard-mcp `list_tasks` tool to show my open tasks.

Or add a task:

> Use taskboard-mcp to add a task called “Prepare demo slides”.

### ChatGPT on the web: Streamable HTTP

ChatGPT on the web needs a URL it can reach. A local `127.0.0.1` address is not reachable from ChatGPT, so for local development use an HTTPS tunnel or deploy the server.

1. Start the HTTP server in one terminal:

   ```bash
   source .venv/bin/activate
   python server.py --http
   ```

2. Install and configure [ngrok](https://ngrok.com/docs/getting-started/) if needed. ngrok requires an account and an authtoken. Add your token once with:

   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```

   Replace `YOUR_AUTHTOKEN` with the token from your ngrok dashboard. Keep it private.

3. In a second terminal, start the tunnel:

   ```bash
   ngrok http 8000
   ```

4. Copy the HTTPS forwarding address ngrok prints and append `/mcp`, for example `https://your-subdomain.ngrok-free.dev/mcp`.

5. In ChatGPT on the web, open **Plugins**, select **+ → Add custom MCP server**, enter a name and the HTTPS `/mcp` URL, choose **No authentication**, then create and install the connection. In some workspaces, the flow is under **Apps → Create**. Menu names and availability depend on your plan and workspace settings; see OpenAI's [custom MCP server guide](https://developers.openai.com/api/docs/guides/custom-mcp-server) and [availability details](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt). Full write support is currently available on Business, Enterprise, and Edu; Pro supports read/fetch actions.

6. In a new chat, type `@`, select `taskboard-mcp`, and ask it to use a tool. For example:

   > Use taskboard-mcp to list my open tasks and make a plan to prepare the demo by Friday. Do not change any task statuses.

ChatGPT uses the server's tools for these requests. Whether ChatGPT exposes MCP resource reading or prompt templates in its interface depends on the client; use MCP Inspector's **Resources** and **Prompts** tabs to try `taskboard://tasks` and `plan_open_tasks(goal)` directly.

The server has no authentication. A public tunnel lets anyone with its URL reach the task tools and data, including tools that add or complete tasks. Use the tunnel only for development, keep the URL private, and stop ngrok when finished. For a private connection, see [OpenAI Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

If you change tool names or descriptions, restart the server and refresh the connected app's tools in ChatGPT.
