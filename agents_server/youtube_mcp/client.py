import asyncio
import json
from typing import TypedDict

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from langchain_mcp_adapters.client import MultiServerMCPClient

from dotenv import load_dotenv
import os

load_dotenv()

# -------------------------
# Graph State
# -------------------------
class GraphState(TypedDict):
    question: str
    videos: str
    answer: str


# -------------------------
# MCP Client (YouTube MCP)
# -------------------------
client = MultiServerMCPClient(
    {
        "youtube": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp",
        }
    }
)

# -------------------------
# MCP Search Node
# -------------------------
async def youtube_search(state: GraphState) -> GraphState:
    tools = await client.get_tools()

    yt_tool = next(t for t in tools if t.name == "best_youtube_videos")

    result = await yt_tool.ainvoke(
        {
            "query": state["question"]
        }
    )

    # 🔍 DEBUG (optional)
    print("MCP Tool Raw Result:", result[0])

    # ✅ Correct extraction
    raw_text = result[0]["text"]        # TextContent -> text
    
    print("Raw Text:", raw_text)
    videos_json = json.loads(raw_text) # JSON string -> list
    print("Parsed JSON:", videos_json)

    return {
        **state,
        "videos": json.dumps(videos_json, indent=2)
    }



# -------------------------
# Groq LLM Node
# -------------------------
def groq_answer(state: GraphState) -> GraphState:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY")
    )

    response = llm.invoke(
        [
            HumanMessage(
                content=f"""
You are an expert learning advisor.

Based ONLY on the YouTube video data below:
- Explain which videos are best for the learner
- Give a short recommendation
- Present the result in a table
- Include video title, channel, views, likes, and link

If the data is empty, say:
"I could not find good YouTube videos for this query."

User Question:
{state["question"]}

YouTube Video Data:
{state["videos"]}
"""
            )
        ]
    )

    return {
        **state,
        "answer": response.content
    }


# -------------------------
# Build LangGraph
# -------------------------
def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("youtube_search", youtube_search)
    graph.add_node("answer", groq_answer)

    graph.set_entry_point("youtube_search")
    graph.add_edge("youtube_search", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


# -------------------------
# Run
# -------------------------
async def main():
    app = build_graph()

    result = await app.ainvoke(
        {
            "question": "best way to learn python for beginners",
        }
    )

    print("\nFinal Answer:\n")
    print(result["answer"])


if __name__ == "__main__":
    asyncio.run(main())
