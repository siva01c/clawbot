"""
MCP HTTP server for OSINTbot.
Exposes JSON-RPC 2.0 tools: query_intel, list_posts, get_status.
Runs on port 7861 alongside the Gradio chat on 7860.
Auth: Authorization: Basic <base64(OSINT_MCP_TOKEN)>
"""
import os
import json
import base64
import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

OSINT_MCP_TOKEN = os.getenv("OSINT_MCP_TOKEN", "")
POSTS_PATH = Path(os.getenv("POSTS_PATH", "/app/posts.json"))
MCP_PORT = int(os.getenv("OSINT_MCP_PORT", "7861"))

# Lazy-loaded RAG instance
_rag = None

def _get_rag():
    global _rag
    if _rag is None:
        if not POSTS_PATH.exists():
            raise FileNotFoundError(f"posts.json not found at {POSTS_PATH}. Run scrape mode first.")
        from linkedin_tool import RagChat
        target_name = os.getenv("LINKEDIN_TARGET_NAME", "LinkedIn User")
        _rag = RagChat(POSTS_PATH, target_name=target_name)
    return _rag


# ── Auth ──────────────────────────────────────────────────────────────────────

def check_auth(request: Request) -> bool:
    if not OSINT_MCP_TOKEN:
        return True  # dev mode — no token set
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("basic "):
        return False
    try:
        decoded = base64.b64decode(header[6:]).decode("utf-8")
    except Exception:
        return False
    return decoded == OSINT_MCP_TOKEN


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "query_intel",
        "description": (
            "Query the OSINT knowledge base (LinkedIn posts, competitor data) "
            "using natural language. Returns relevant excerpts and a generated answer."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language question to answer from the OSINT data",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_posts",
        "description": "List scraped posts/entries in the OSINT knowledge base with basic metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of posts to return (default 20)",
                    "default": 20,
                }
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "get_status",
        "description": "Check OSINT service status: whether posts.json exists and how many entries it has.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]


# ── Tool handlers ─────────────────────────────────────────────────────────────

def handle_query_intel(args: dict[str, Any]) -> str:
    query = str(args.get("query", "")).strip()
    if not query:
        return json.dumps({"error": "query is required"})
    try:
        rag = _get_rag()
        answer = rag.generate_response(query)
        context = rag.retrieve_context(query, top_k=3)
        return json.dumps({"answer": answer, "sources": context[:3]})
    except FileNotFoundError as e:
        return json.dumps({"error": str(e), "hint": "Run the scrape tool first to collect data"})
    except Exception as e:
        return json.dumps({"error": f"RAG query failed: {e}"})


def handle_list_posts(args: dict[str, Any]) -> str:
    limit = int(args.get("limit", 20))
    if not POSTS_PATH.exists():
        return json.dumps({"error": "posts.json not found. Run scrape mode first."})
    try:
        with open(POSTS_PATH) as f:
            data = json.load(f)
        # posts.json is a dict {name: {posts: {id: {text, date, ...}}}}
        entries = []
        for author, info in data.items():
            posts = info.get("posts", {}) if isinstance(info, dict) else {}
            for pid, post in posts.items():
                entries.append({
                    "author": author,
                    "id": pid,
                    "text_preview": str(post.get("text", ""))[:120],
                    "date": post.get("date", ""),
                })
                if len(entries) >= limit:
                    break
            if len(entries) >= limit:
                break
        return json.dumps({"total_authors": len(data), "posts_returned": len(entries), "posts": entries})
    except Exception as e:
        return json.dumps({"error": f"Failed to read posts: {e}"})


def handle_get_status() -> str:
    exists = POSTS_PATH.exists()
    count = 0
    if exists:
        try:
            with open(POSTS_PATH) as f:
                data = json.load(f)
            for info in data.values():
                if isinstance(info, dict):
                    count += len(info.get("posts", {}))
        except Exception:
            pass
    return json.dumps({
        "posts_json_exists": exists,
        "posts_path": str(POSTS_PATH),
        "total_posts": count,
        "rag_loaded": _rag is not None,
    })


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(title="OSINT MCP Server", docs_url=None, redoc_url=None)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/mcp/post")
async def mcp_endpoint(request: Request):
    if not check_auth(request):
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
        )

    rpc_id = body.get("id")
    method = body.get("method", "")
    params = body.get("params", {})

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0", "id": rpc_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "osint-mcp", "version": "1.0.0"},
            },
        })

    # notifications/initialized is a JSON-RPC notification (no id) — ack with 204
    if method == "notifications/initialized":
        return Response(status_code=204)

    if method == "tools/list":
        return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": TOOLS}})

    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})

        if name == "query_intel":
            text = handle_query_intel(args)
        elif name == "list_posts":
            text = handle_list_posts(args)
        elif name == "get_status":
            text = handle_get_status()
        else:
            return JSONResponse({
                "jsonrpc": "2.0", "id": rpc_id,
                "error": {"code": -32601, "message": f"Unknown tool: {name}"},
            })

        return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "result": {"content": [{"type": "text", "text": text}]}})

    return JSONResponse({
        "jsonrpc": "2.0", "id": rpc_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    })


if __name__ == "__main__":
    print(f"[osint-mcp] Starting on port {MCP_PORT}")
    print(f"[osint-mcp] Auth: {'enabled' if OSINT_MCP_TOKEN else 'DISABLED (set OSINT_MCP_TOKEN)'}")
    uvicorn.run(app, host="0.0.0.0", port=MCP_PORT)
