import httpx
import os

YOUTUBE_API_KEY = "AIzaSyDBxeWsg0PNU6oshQegElRrRjcT06L_9_w"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"


async def search_youtube(query: str, max_results=10):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            YOUTUBE_SEARCH_URL,
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": max_results,
                "key": YOUTUBE_API_KEY,
            },
        )
        res.raise_for_status()
        items = res.json()["items"]

        video_ids = [item["id"]["videoId"] for item in items]
        return await fetch_video_stats(video_ids)


async def fetch_video_stats(video_ids):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            YOUTUBE_VIDEO_URL,
            params={
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(video_ids),
                "key": YOUTUBE_API_KEY,
            },
        )
        res.raise_for_status()
        return res.json()["items"]
