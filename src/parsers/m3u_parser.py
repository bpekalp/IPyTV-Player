"""
M3U Playlist Parser
Parses M3U playlist files and categorizes streams
"""

import re
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse, unquote


class M3UParser:
    def __init__(self):
        self.channels = []
        self.movies = []
        self.series = []

    def parse_from_url(self, m3u_url: str) -> bool:
        """Parse M3U playlist from URL"""
        try:
            response = requests.get(m3u_url, timeout=30)
            response.raise_for_status()
            return self.parse_content(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch M3U: {e}")
            return False

    def parse_from_file(self, file_path: str) -> bool:
        """Parse M3U playlist from file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.parse_content(content)
        except IOError as e:
            print(f"Failed to read M3U file: {e}")
            return False

    def parse_content(self, content: str) -> bool:
        """Parse M3U playlist content"""
        self.channels.clear()
        self.movies.clear()
        self.series.clear()

        lines = content.strip().split("\n")

        if not lines or not lines[0].startswith("#EXTM3U"):
            print("Invalid M3U format")
            return False

        current_item = {}

        for line in lines[1:]:
            line = line.strip()

            if line.startswith("#EXTINF:"):
                current_item = self._parse_extinf_line(line)
            elif line and not line.startswith("#"):
                if current_item:
                    current_item["url"] = line
                    self._categorize_item(current_item)
                    current_item = {}

        return True

    def _parse_extinf_line(self, line: str) -> Dict:
        """Parse EXTINF line and extract metadata"""
        # Example: #EXTINF:-1 tvg-id="channel.id" tvg-name="Channel Name" tvg-logo="logo.png" group-title="Category",Display Name

        item = {}

        # Extract duration (usually -1 for streams)
        duration_match = re.search(r"#EXTINF:([^,\s]+)", line)
        if duration_match:
            item["duration"] = duration_match.group(1)

        # Extract attributes
        attributes = re.findall(r'(\w+(?:-\w+)*)="([^"]*)"', line)
        for attr, value in attributes:
            item[attr.replace("-", "_")] = value

        # Extract title (after the last comma)
        title_match = re.search(r",([^,]+)$", line)
        if title_match:
            item["title"] = title_match.group(1).strip()
        else:
            item["title"] = "Unknown"

        return item

    def _categorize_item(self, item: Dict):
        """Categorize item into channels, movies, or series"""
        group_title = item.get("group_title", "").lower()
        title = item.get("title", "").lower()
        url = item.get("url", "")

        # Determine category based on various indicators
        if self._is_movie(group_title, title, url):
            item["category"] = "movie"
            self.movies.append(item)
        elif self._is_series(group_title, title, url):
            item["category"] = "series"
            self.series.append(item)
        else:
            item["category"] = "live"
            self.channels.append(item)

    def _is_movie(self, group_title: str, title: str, url: str) -> bool:
        """Determine if item is a movie"""
        movie_indicators = [
            "movie",
            "film",
            "cinema",
            "vod",
            "on demand",
            "hollywood",
            "bollywood",
            "action",
            "comedy",
            "drama",
            "horror",
            "thriller",
            "sci-fi",
            "animation",
            "documentary",
            "adventure",
        ]

        # Check group title
        for indicator in movie_indicators:
            if indicator in group_title:
                return True

        # Check if URL suggests it's a movie (common patterns)
        if "/movie/" in url or ".mp4" in url or ".mkv" in url:
            return True

        return False

    def _is_series(self, group_title: str, title: str, url: str) -> bool:
        """Determine if item is a series/TV show"""
        series_indicators = [
            "series",
            "tv",
            "show",
            "season",
            "episode",
            "drama series",
            "comedy series",
            "reality",
            "documentary series",
        ]

        # Check group title
        for indicator in series_indicators:
            if indicator in group_title:
                return True

        # Check title for season/episode patterns
        if re.search(r"s\d+e\d+|season\s+\d+|episode\s+\d+", title):
            return True

        # Check if URL suggests it's a series
        if "/series/" in url:
            return True

        return False

    def get_categories(self, content_type: str) -> List[str]:
        """Get unique categories for given content type"""
        if content_type == "live":
            items = self.channels
        elif content_type == "movie":
            items = self.movies
        elif content_type == "series":
            items = self.series
        else:
            return []

        categories = set()
        for item in items:
            group_title = item.get("group_title", "Uncategorized")
            if group_title:
                categories.add(group_title)

        return sorted(list(categories))

    def get_items_by_category(
        self, content_type: str, category: str = None
    ) -> List[Dict]:
        """Get items filtered by content type and optionally by category"""
        if content_type == "live":
            items = self.channels
        elif content_type == "movie":
            items = self.movies
        elif content_type == "series":
            items = self.series
        else:
            return []

        if category:
            return [item for item in items if item.get("group_title") == category]
        else:
            return items.copy()

    def search_items(self, query: str, content_type: str = None) -> List[Dict]:
        """Search items by title"""
        query = query.lower()
        results = []

        search_lists = []
        if content_type == "live" or not content_type:
            search_lists.append(self.channels)
        if content_type == "movie" or not content_type:
            search_lists.append(self.movies)
        if content_type == "series" or not content_type:
            search_lists.append(self.series)

        for item_list in search_lists:
            for item in item_list:
                title = item.get("title", "").lower()
                if query in title:
                    results.append(item)

        return results

    def get_stats(self) -> Dict:
        """Get statistics about parsed content"""
        return {
            "live_channels": len(self.channels),
            "movies": len(self.movies),
            "series": len(self.series),
            "total": len(self.channels) + len(self.movies) + len(self.series),
        }
