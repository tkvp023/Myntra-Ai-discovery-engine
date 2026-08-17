"""
YouTube scraper using YouTube Data API v3.
Searches for Myntra-related videos, then extracts comment threads.
Requires YOUTUBE_API_KEY in .env.
"""

import os
from typing import List, Optional
from datetime import datetime, timezone

from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username, with_retry
from pipeline.scrapers.config import YOUTUBE_CONFIG


class YouTubeScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "youtube"

    def _get_youtube_client(self):
        """Initialize YouTube Data API client."""
        from googleapiclient.discovery import build

        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not set in .env")

        return build("youtube", "v3", developerKey=api_key)

    @with_retry
    def _search_videos(self, youtube, query: str, max_results: int = 30) -> List[dict]:
        """Search for YouTube videos matching the query."""
        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=min(50, max_results - len(videos)),
                order=self.config.get("order", "relevance"),
                publishedAfter=self.config.get("published_after"),
                regionCode=self.config.get("region_code", "IN"),
                relevanceLanguage=self.config.get("relevance_language", "en"),
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response.get("items", []):
                videos.append({
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "channel_title": item["snippet"]["channelTitle"],
                    "published_at": item["snippet"]["publishedAt"],
                    "description": item["snippet"].get("description", ""),
                })

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return videos

    @with_retry
    def _get_comments(self, youtube, video_id: str, max_comments: int = 200) -> List[dict]:
        """Fetch comment threads for a video."""
        comments = []
        next_page_token = None

        while len(comments) < max_comments:
            try:
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=min(100, max_comments - len(comments)),
                    order=self.config.get("comment_order", "relevance"),
                    textFormat="plainText",
                    pageToken=next_page_token,
                )
                response = request.execute()

                for item in response.get("items", []):
                    # Top-level comment
                    snippet = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "comment_id": item["snippet"]["topLevelComment"]["id"],
                        "text": snippet["textDisplay"],
                        "author": snippet.get("authorDisplayName", ""),
                        "like_count": snippet.get("likeCount", 0),
                        "published_at": snippet.get("publishedAt", ""),
                        "parent_id": None,
                    })

                    # Replies
                    if "replies" in item:
                        for reply in item["replies"]["comments"]:
                            reply_snippet = reply["snippet"]
                            comments.append({
                                "comment_id": reply["id"],
                                "text": reply_snippet["textDisplay"],
                                "author": reply_snippet.get("authorDisplayName", ""),
                                "like_count": reply_snippet.get("likeCount", 0),
                                "published_at": reply_snippet.get("publishedAt", ""),
                                "parent_id": item["snippet"]["topLevelComment"]["id"],
                            })

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break

            except Exception as e:
                # Comments disabled on video, or other error
                if "commentsDisabled" in str(e) or "forbidden" in str(e).lower():
                    break
                raise

        return comments[:max_comments]

    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        youtube = self._get_youtube_client()

        queries = self.config.get("search_queries", [])
        max_videos_per_query = self.config.get("max_videos_per_query", 30)
        max_comments_per_video = self.config.get("max_comments_per_video", 200)

        existing_ids = self.get_existing_source_ids()
        print(f"  📦 Found {len(existing_ids)} existing docs on disk")

        documents = []
        seen_video_ids = set()
        seen_comment_ids = set(existing_ids)

        from tqdm import tqdm

        # Phase 1: Collect video IDs
        print(f"  🔎 Searching for videos across {len(queries)} queries...")
        all_videos = []
        for query in tqdm(queries, desc="  Video search", unit="queries"):
            try:
                videos = self._search_videos(youtube, query, max_results=max_videos_per_query)
                for v in videos:
                    if v["video_id"] not in seen_video_ids:
                        all_videos.append(v)
                        seen_video_ids.add(v["video_id"])
                self.rate_limit_sleep(0.5)
            except Exception as e:
                print(f"  ⚠️  Error searching for '{query}': {e}")
                continue

        print(f"  📹 Found {len(all_videos)} unique videos")

        # Phase 2: Extract comments
        for video in tqdm(all_videos, desc="  Comments", unit="videos"):
            try:
                comments = self._get_comments(
                    youtube, video["video_id"],
                    max_comments=max_comments_per_video,
                )

                for comment in comments:
                    if comment["comment_id"] in seen_comment_ids:
                        continue

                    doc = ScrapedDocument(
                        source="youtube",
                        source_type="primary",
                        source_id=comment["comment_id"],
                        author=anonymize_username(comment["author"]),
                        content=comment["text"],
                        title=video["title"],
                        rating=None,
                        timestamp=comment["published_at"],
                        url=f"https://youtube.com/watch?v={video['video_id']}",
                        metadata={
                            "video_id": video["video_id"],
                            "channel_title": video["channel_title"],
                            "upvotes": comment["like_count"],
                            "parent_id": comment["parent_id"],
                            "post_type": "reply" if comment["parent_id"] else "comment",
                        },
                    )
                    documents.append(doc)
                    seen_comment_ids.add(comment["comment_id"])

                self.rate_limit_sleep(0.2)

            except Exception as e:
                print(f"  ⚠️  Error getting comments for {video['video_id']}: {e}")
                continue

            if limit and len(documents) >= limit:
                break

        return documents[:limit] if limit else documents
