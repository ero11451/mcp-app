# server.py (snippet)
from fastmcp import FastMCP
from typing import Optional
from translation_tool import _translate_chain  # reuse the chain

mcp = FastMCP("translator")

@mcp.tool
def text_translation(text: str, target_language: str = "French",
                     max_steps: Optional[int] = 5) -> str:
    """Translate `text` into `target_language`. Returns only the translation."""
    # `max_steps` is accepted for a consistent signature; not used by this chain.
    return _translate_chain.invoke({"text": text, "target_language": target_language})

if __name__ == "__main__":
   mcp.run(transport='stdio')
