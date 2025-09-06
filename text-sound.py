from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI
import os

# Set your key in env first:
# export OPENAI_API_KEY=sk-...

client = OpenAI()

llm = ChatOllama(model="llama3", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise storyteller. Keep it under 120 words."),
    ("user", "Write a friendly bedtime story about {topic}.")
])

def openai_tts(text: str, outfile: str = "speech.mp3"):
    # Voice options vary; "alloy" is a safe default
    audio = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
        format="mp3",
    )
    with open(outfile, "wb") as f:
        f.write(audio.read())  # stream payload to file
    return {"audio_path": outfile}

chain = (
    prompt
    | llm
    | StrOutputParser()
    | RunnableLambda(lambda s: openai_tts(s, "story.mp3"))
)

result = chain.invoke({"topic": "a sleepy robot and a comet"})
print("Saved:", result["audio_path"])  # story.mp3
