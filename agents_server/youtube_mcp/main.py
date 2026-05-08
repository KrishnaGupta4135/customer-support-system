from fastmcp import FastMCP
from youtube import search_youtube
from scoring import score_video

mcp = FastMCP("youtube-recommender")


@mcp.tool()
async def best_youtube_videos(query: str):
    """
    Search YouTube and return top 5 high-quality videos for learning.
    """
    videos = await search_youtube(query)

    scored = []
    for v in videos:
        score = score_video(v)
        scored.append({
            "title": v["snippet"]["title"],
            "channel": v["snippet"]["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={v['id']}",
            "views": v["statistics"].get("viewCount"),
            "likes": v["statistics"].get("likeCount"),
            "score": score,
        })

    top_5 = sorted(scored, key=lambda x: x["score"], reverse=True)[:5]
    return top_5


if __name__ == "__main__":
    mcp.run(transport="http")
