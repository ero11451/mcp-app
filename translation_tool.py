from __future__ import annotations
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
try:
    from langchain_ollama import ChatOllama
except Exception:
    from langchain_community.chat_models import ChatOllama

LLM = ChatOllama(model="llama3.1:8b", temperature=0)

_translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "Translate the user's input into the target language. "
               "Return only the translation, no explanations."),
    ("human", "Target language: {target_language}\n\nText:\n{text}")
])

_translate_chain = _translate_prompt | LLM | StrOutputParser()

class TranslateArgs(BaseModel):
    text: str = Field(..., description="The text to translate")
    target_language: str = Field("French", description="Target language name, e.g. 'French', 'Spanish'")

@tool("translate_text", args_schema=TranslateArgs)
def translate_text(text: str, target_language: str = "French") -> str:
    """Translate text into the specified target language and return only the translation."""
    return _translate_chain.invoke({"text": text, "target_language": target_language})


