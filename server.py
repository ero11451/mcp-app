# server.py
from __future__ import annotations
from typing import Optional
from fastmcp import Client, FastMCP
from langchain.agents import AgentExecutor, create_tool_calling_agent
try:
    from langchain_ollama import ChatOllama
except Exception:
    from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from translation_tool import _translate_chain

mcp = FastMCP("langchain-agent-search")
llm = ChatOllama(model="llama3.1:8b", temperature=0) # swap model as you like
search_tool = DuckDuckGoSearchRun(name="searchWeb")

def build_agent() -> AgentExecutor:
    """Create a ReAct agent with a search tool."""
    tools = [search_tool]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a helpful research assistant. Use tools when useful. "
             "Cite sources in plain text if available."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Build once and reuse across tool calls
AGENT = build_agent()

@mcp.tool
def agent_search(query: str, max_steps: Optional[int] = 5) -> str:
    """Run a LangChain search agent to answer a query with web results.
    Args:
        query: The user question to research.
        max_steps: Safety cap on tool-use iterations (default 5).
    Returns:
        A final, concise answer from the agent.
    """
    result = AGENT.invoke( {"input": query}, config={ "configurable": { "thread_id": "mcp"  },  "recursion_limit": max_steps }, )
    # LangChain AgentExecutor returns a dict with "output"
    return result["output"]

@mcp.tool
def text_translation(text: str, target_language: str = "French", max_steps: Optional[int] = 5) -> str:
    """Translate `text` into `target_language`. Returns only the translation."""
    return _translate_chain.invoke({"text": text, "target_language": target_language})


@mcp.tool
async def research_then_translate(query: str, target_language: str = "French") -> str:
    """Run research, then translate the answer."""
    async with Client("./server.py") as c:
        await c.ping()
        res = await c.call_tool("agent_search", {"query": query, "max_steps": 5})
        ans = getattr(res, "data", res)
        tr  = await c.call_tool("text_translation", {"text": str(ans), "target_language": target_language})
        return getattr(tr, "data", tr)


if __name__ == "__main__":
    # Runs an MCP stdio server (compatible with Claude Desktop, Cursor, etc.)
   mcp.run(transport='stdio')
