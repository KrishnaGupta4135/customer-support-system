from datetime import datetime

def score_video(video):
    stats = video.get("statistics", {})
    snippet = video.get("snippet", {})

    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))

    published_at = snippet.get("publishedAt")
    year_bonus = 1 if published_at and "2023" in published_at else 0

    score = (
        views * 0.4 +
        likes * 0.3 +
        comments * 0.2 +
        year_bonus * 10000
    )
    return score
