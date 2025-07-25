# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application

```bash
python run.py
```

The application requires VLC media player to be installed on the system for video playback functionality.

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Key Dependencies

- **PyQt6**: GUI framework for the desktop application
- **python-vlc**: Python bindings for VLC media player (streaming backend)
- **requests**: HTTP client for Xtream Codes API communication
- **lxml**: XML parsing for XMLTV EPG data
- **python-dateutil**: Date/time parsing for EPG scheduling

## Architecture Overview

### Core Application Flow

The application follows a threaded architecture where the main GUI remains responsive while data loading occurs in background threads. The entry point is `run.py` which imports from `src/main.py`.

### Key Components Architecture

**API Layer** (`src/api/`):

- `XtreamCodesClient`: Handles all Xtream Codes API communication including authentication, fetching categories, streams, and generating playback URLs. Uses persistent sessions and implements error handling with timeouts.

**GUI Layer** (`src/gui/`):

- `MainWindow`: Central application window that coordinates between all components. Implements threaded data loading via `DataLoaderThread` to prevent UI blocking.
- `MediaPlayerWidget`: VLC-based media player with full playback controls, position tracking, and volume management.
- `LoginDialog`: Credential input interface for Xtream Codes servers.
- `StreamsWidget`: Content browser with search, filtering, and stream selection functionality.
- `CategoryFilterWidget`: Advanced filtering system supporting search, categories, genres, years, and content-specific filters.

**Data Parsing Layer** (`src/parsers/`):

- `M3UParser`: Parses M3U playlists and automatically categorizes content into Movies, Series, and Live TV based on metadata patterns and URL analysis.
- `XMLTVParser`: Extracts EPG data from XMLTV format, parses program schedules, and extracts categories/subcategories from EPG headers.

**Utilities** (`src/utils/`):

- `Settings`: Platform-specific persistent configuration management with JSON storage, credential handling, and default value merging.

### Data Flow Architecture

1. **Authentication**: User credentials are captured via `LoginDialog` and passed to `XtreamCodesClient`
2. **Data Loading**: `DataLoaderThread` fetches all content categories and streams from Xtream API in background
3. **Content Organization**: Data is automatically categorized into three main sections (Live TV, Movies, Series) in the tree navigation
4. **Stream Selection**: User selects content from `StreamsWidget` which generates appropriate stream URLs via `XtreamCodesClient`
5. **Playback**: Stream URLs are passed to `MediaPlayerWidget` which uses VLC for actual media streaming

### Threading Model

- **Main Thread**: Handles all GUI operations and user interactions
- **DataLoaderThread**: Background loading of categories and streams from Xtream API
- **VLC Thread**: Media playback is handled internally by VLC player instance

### Settings and State Management

Settings are persisted using platform-specific directories (AppData on Windows, ~/.config on Linux, ~/Library/Application Support on macOS). Credentials can be saved but should be encrypted in production deployments.

### Content Categorization Logic

The application uses intelligent categorization by analyzing:

- M3U `group-title` attributes for primary categorization
- URL patterns (e.g., `/movie/`, `/series/`, `/live/`) for content type detection
- XMLTV category tags for subcategory extraction
- Title patterns (season/episode indicators) for series identification

### Error Handling Patterns

- API failures are handled gracefully with user-friendly error messages
- Network timeouts use configurable values (30s for API, 60s for streams)
- Missing dependencies (like VLC) should be detected and reported to users
- Invalid server responses are caught and logged without crashing the application
