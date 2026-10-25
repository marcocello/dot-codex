#!/usr/bin/env python3
"""Verify one declared MCP transport without calling application tools."""
import asyncio
import json
import os
from pathlib import Path
import re
import sys


def interpolate(value):
    if not isinstance(value, str):
        return value
    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", lambda match: os.environ[match[1]], value)


async def probe(server):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamable_http_client
    from contextlib import AsyncExitStack
    async with AsyncExitStack() as stack:
        if "command" in server:
            env = {**os.environ, **{key:interpolate(value) for key,value in server.get("env", {}).items()}}
            errors = stack.enter_context(open(os.devnull, "w"))
            streams = await stack.enter_async_context(stdio_client(StdioServerParameters(
                command=interpolate(server["command"]), args=[interpolate(value) for value in server.get("args", [])], env=env), errlog=errors))
        else:
            import httpx
            headers = {key:interpolate(value) for key,value in server.get("http_headers", server.get("headers", {})).items()}
            if name := server.get("bearer_token_env_var"):
                headers["Authorization"] = "Bearer " + os.environ[name]
            client = await stack.enter_async_context(httpx.AsyncClient(headers=headers, timeout=30, follow_redirects=False))
            streams = await stack.enter_async_context(streamable_http_client(interpolate(server["url"]), http_client=client))
        session = await stack.enter_async_context(ClientSession(streams[0], streams[1]))
        await session.initialize()
        result = await session.list_tools()
        return {"ok": True, "tools": len(result.tools), "boundary": "MCP initialized and tools listed; application actions were not invoked"}


if __name__ == "__main__":
    try:
        server = json.loads(Path(sys.argv[1]).read_text())
        print(json.dumps(asyncio.run(asyncio.wait_for(probe(server), timeout=90))))
    except Exception:
        print(json.dumps({"ok": False, "error": "MCP transport unavailable; verify required application, network and provider authentication"}))
        raise SystemExit(2)
