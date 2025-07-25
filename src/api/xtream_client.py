"""
Xtream Codes API Client
Handles authentication and data fetching from Xtream Codes servers.
"""

import requests
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin
import json


class XtreamCodesClient:
    def __init__(self, server_url: str, username: str, password: str):
        self.server_url = server_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.player_api_url = f"{self.server_url}/player_api.php"

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            params.update({"username": self.username, "password": self.password})
            response = self.session.get(self.player_api_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except json.JSONDecodeError:
            print("Invalid JSON response from server")
            return None

    def get_server_info(self) -> Optional[Dict]:
        """Get server information and user details"""
        return self._make_request({})

    def get_live_categories(self) -> List[Dict]:
        """Get live TV categories"""
        data = self._make_request({"action": "get_live_categories"})
        return data if data else []

    def get_vod_categories(self) -> List[Dict]:
        """Get VOD (Movies) categories"""
        data = self._make_request({"action": "get_vod_categories"})
        return data if data else []

    def get_series_categories(self) -> List[Dict]:
        """Get Series categories"""
        data = self._make_request({"action": "get_series_categories"})
        return data if data else []

    def get_live_streams(self, category_id: Optional[int] = None) -> List[Dict]:
        """Get live TV streams"""
        params = {"action": "get_live_streams"}
        if category_id:
            params["category_id"] = category_id
        data = self._make_request(params)
        return data if data else []

    def get_vod_streams(self, category_id: Optional[int] = None) -> List[Dict]:
        """Get VOD streams"""
        params = {"action": "get_vod_streams"}
        if category_id:
            params["category_id"] = category_id
        data = self._make_request(params)
        return data if data else []

    def get_series(self, category_id: Optional[int] = None) -> List[Dict]:
        """Get series"""
        params = {"action": "get_series"}
        if category_id:
            params["category_id"] = category_id
        data = self._make_request(params)
        return data if data else []

    def get_series_info(self, series_id: int) -> Optional[Dict]:
        """Get detailed series information including episodes"""
        return self._make_request({"action": "get_series_info", "series_id": series_id})

    def get_vod_info(self, vod_id: int) -> Optional[Dict]:
        """Get detailed VOD information"""
        return self._make_request({"action": "get_vod_info", "vod_id": vod_id})

    def get_xmltv_url(self) -> str:
        """Get XMLTV EPG URL"""
        return f"{self.server_url}/xmltv.php?username={self.username}&password={self.password}"

    def get_m3u_url(self) -> str:
        """Get M3U playlist URL"""
        return f"{self.server_url}/get.php?username={self.username}&password={self.password}&type=m3u_plus&output=ts"

    def get_stream_url(self, stream_id: int, stream_type: str = "live") -> str:
        """Generate stream URL for playback"""
        if stream_type == "live":
            return (
                f"{self.server_url}/live/{self.username}/{self.password}/{stream_id}.ts"
            )
        elif stream_type == "movie":
            return f"{self.server_url}/movie/{self.username}/{self.password}/{stream_id}.mp4"
        elif stream_type == "series":
            return f"{self.server_url}/series/{self.username}/{self.password}/{stream_id}.mp4"
        return ""
