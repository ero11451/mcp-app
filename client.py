import asyncio
import os
from fastmcp import Client
from flask import Flask, render_template,jsonify, request
import sys

# Path to your MCP server; override with MCP_SERVER env if needed
SERVER_PATH = os.environ.get("MCP_SERVER", "./server.py")

async def research_then_translate(query: str, target_language: str = "French") -> str:
    """Run research, then translate the answer."""
    async with Client("./server.py") as c:
        await c.ping()
        res = await c.call_tool("agent_search", {"query": query, "max_steps": 5})
        ans = getattr(res, "data", res)
        tr  = await c.call_tool("text_translation", {"text": str(ans), "target_language": target_language})
        return getattr(tr, "data", tr)


async def main(query:str):
    client = Client(SERVER_PATH)
    async with client:
        await client.ping()
        tools = await client.list_tools()
        print("Connected. Tools:", [t.name for t in tools])
        result = await client.call_tool("research_then_translate", {"query": query, "max_steps": 5})
        try:
           return result.data
        except AttributeError:
            return  result
