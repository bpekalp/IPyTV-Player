"""
XMLTV EPG Parser
Parses XMLTV Electronic Program Guide data and extracts categories
"""

import xml.etree.ElementTree as ET
import requests
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dateutil import parser as date_parser


class XMLTVParser:
    def __init__(self):
        self.channels = {}
        self.programmes = []
        self.categories = set()

    def parse_from_url(self, xmltv_url: str) -> bool:
        """Parse XMLTV data from URL"""
        try:
            response = requests.get(xmltv_url, timeout=60)
            response.raise_for_status()
            return self.parse_content(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch XMLTV: {e}")
            return False

    def parse_from_file(self, file_path: str) -> bool:
        """Parse XMLTV data from file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.parse_content(content)
        except IOError as e:
            print(f"Failed to read XMLTV file: {e}")
            return False

    def parse_content(self, content: str) -> bool:
        """Parse XMLTV content"""
        try:
            self.channels.clear()
            self.programmes.clear()
            self.categories.clear()

            root = ET.fromstring(content)

            # Parse channels
            for channel_elem in root.findall("channel"):
                channel_id = channel_elem.get("id")
                if not channel_id:
                    continue

                channel_data = {
                    "id": channel_id,
                    "display_names": [],
                    "icons": [],
                    "urls": [],
                }

                # Get display names
                for display_name in channel_elem.findall("display-name"):
                    if display_name.text:
                        channel_data["display_names"].append(display_name.text.strip())

                # Get icons
                for icon in channel_elem.findall("icon"):
                    src = icon.get("src")
                    if src:
                        channel_data["icons"].append(src)

                # Get URLs
                for url in channel_elem.findall("url"):
                    if url.text:
                        channel_data["urls"].append(url.text.strip())

                self.channels[channel_id] = channel_data

            # Parse programmes
            for programme_elem in root.findall("programme"):
                programme_data = self._parse_programme(programme_elem)
                if programme_data:
                    self.programmes.append(programme_data)

                    # Extract categories from programme
                    for category in programme_data.get("categories", []):
                        self.categories.add(category)

            return True

        except ET.ParseError as e:
            print(f"Failed to parse XMLTV: {e}")
            return False
        except Exception as e:
            print(f"Error parsing XMLTV: {e}")
            return False

    def _parse_programme(self, programme_elem) -> Optional[Dict]:
        """Parse a programme element"""
        channel = programme_elem.get("channel")
        start = programme_elem.get("start")
        stop = programme_elem.get("stop")

        if not all([channel, start]):
            return None

        programme_data = {
            "channel": channel,
            "start": self._parse_datetime(start),
            "stop": self._parse_datetime(stop) if stop else None,
            "titles": [],
            "sub_titles": [],
            "descriptions": [],
            "categories": [],
            "countries": [],
            "languages": [],
            "icons": [],
            "ratings": [],
            "credits": {},
        }

        # Parse titles
        for title in programme_elem.findall("title"):
            if title.text:
                programme_data["titles"].append(
                    {"text": title.text.strip(), "lang": title.get("lang", "en")}
                )

        # Parse sub-titles
        for sub_title in programme_elem.findall("sub-title"):
            if sub_title.text:
                programme_data["sub_titles"].append(
                    {
                        "text": sub_title.text.strip(),
                        "lang": sub_title.get("lang", "en"),
                    }
                )

        # Parse descriptions
        for desc in programme_elem.findall("desc"):
            if desc.text:
                programme_data["descriptions"].append(
                    {"text": desc.text.strip(), "lang": desc.get("lang", "en")}
                )

        # Parse categories
        for category in programme_elem.findall("category"):
            if category.text:
                programme_data["categories"].append(category.text.strip())

        # Parse countries
        for country in programme_elem.findall("country"):
            if country.text:
                programme_data["countries"].append(country.text.strip())

        # Parse languages
        for language in programme_elem.findall("language"):
            if language.text:
                programme_data["languages"].append(language.text.strip())

        # Parse icons
        for icon in programme_elem.findall("icon"):
            src = icon.get("src")
            if src:
                programme_data["icons"].append(src)

        # Parse ratings
        for rating in programme_elem.findall("rating"):
            rating_data = {"system": rating.get("system"), "value": None, "icons": []}

            value_elem = rating.find("value")
            if value_elem is not None and value_elem.text:
                rating_data["value"] = value_elem.text.strip()

            for icon in rating.findall("icon"):
                src = icon.get("src")
                if src:
                    rating_data["icons"].append(src)

            programme_data["ratings"].append(rating_data)

        # Parse credits
        credits_elem = programme_elem.find("credits")
        if credits_elem is not None:
            for role in [
                "director",
                "actor",
                "writer",
                "adapter",
                "producer",
                "composer",
                "editor",
                "presenter",
                "commentator",
                "guest",
            ]:
                people = []
                for person in credits_elem.findall(role):
                    if person.text:
                        people.append(person.text.strip())
                if people:
                    programme_data["credits"][role] = people

        return programme_data

    def _parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse XMLTV datetime format"""
        if not datetime_str:
            return None

        try:
            # XMLTV format: YYYYMMDDHHMMSS +TIMEZONE
            if len(datetime_str) >= 14:
                # Extract timezone if present
                if "+" in datetime_str or "-" in datetime_str[-5:]:
                    dt_part = datetime_str[:14]
                    tz_part = datetime_str[14:].strip()
                else:
                    dt_part = datetime_str[:14]
                    tz_part = None

                # Parse the datetime part
                dt = datetime.strptime(dt_part, "%Y%m%d%H%M%S")

                # Add timezone if present
                if tz_part:
                    try:
                        # Parse timezone offset
                        sign = 1 if tz_part[0] == "+" else -1
                        hours = int(tz_part[1:3])
                        minutes = int(tz_part[3:5]) if len(tz_part) >= 5 else 0
                        offset_minutes = sign * (hours * 60 + minutes)
                        dt = dt.replace(
                            tzinfo=timezone(datetime.timedelta(minutes=offset_minutes))
                        )
                    except (ValueError, IndexError):
                        pass

                return dt
            else:
                # Try generic parsing
                return date_parser.parse(datetime_str)

        except (ValueError, date_parser.ParserError):
            print(f"Failed to parse datetime: {datetime_str}")
            return None

    def get_channel(self, channel_id: str) -> Optional[Dict]:
        """Get channel information by ID"""
        return self.channels.get(channel_id)

    def get_programmes_by_channel(
        self, channel_id: str, start_time: datetime = None, end_time: datetime = None
    ) -> List[Dict]:
        """Get programmes for a specific channel within time range"""
        programmes = []

        for programme in self.programmes:
            if programme["channel"] != channel_id:
                continue

            prog_start = programme.get("start")
            if not prog_start:
                continue

            # Apply time filters
            if start_time and prog_start < start_time:
                continue
            if end_time and prog_start > end_time:
                continue

            programmes.append(programme)

        return sorted(programmes, key=lambda x: x.get("start", datetime.min))

    def get_programmes_by_category(self, category: str) -> List[Dict]:
        """Get all programmes in a specific category"""
        programmes = []

        for programme in self.programmes:
            if category in programme.get("categories", []):
                programmes.append(programme)

        return programmes

    def get_current_programme(
        self, channel_id: str, current_time: datetime = None
    ) -> Optional[Dict]:
        """Get currently airing programme for a channel"""
        if not current_time:
            current_time = datetime.now(timezone.utc)

        for programme in self.programmes:
            if programme["channel"] != channel_id:
                continue

            start = programme.get("start")
            stop = programme.get("stop")

            if not start:
                continue

            if start <= current_time and (not stop or current_time <= stop):
                return programme

        return None

    def get_categories(self) -> List[str]:
        """Get all unique categories found in the EPG"""
        return sorted(list(self.categories))

    def search_programmes(self, query: str, search_in: List[str] = None) -> List[Dict]:
        """Search programmes by title, description, etc."""
        if not search_in:
            search_in = ["titles", "descriptions", "categories"]

        query = query.lower()
        results = []

        for programme in self.programmes:
            match_found = False

            # Search in titles
            if "titles" in search_in:
                for title in programme.get("titles", []):
                    if query in title.get("text", "").lower():
                        match_found = True
                        break

            # Search in descriptions
            if not match_found and "descriptions" in search_in:
                for desc in programme.get("descriptions", []):
                    if query in desc.get("text", "").lower():
                        match_found = True
                        break

            # Search in categories
            if not match_found and "categories" in search_in:
                for category in programme.get("categories", []):
                    if query in category.lower():
                        match_found = True
                        break

            if match_found:
                results.append(programme)

        return results

    def get_stats(self) -> Dict:
        """Get statistics about parsed EPG data"""
        return {
            "channels": len(self.channels),
            "programmes": len(self.programmes),
            "categories": len(self.categories),
            "channels_with_programmes": len(set(p["channel"] for p in self.programmes)),
        }
