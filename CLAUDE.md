# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Server Management
```bash
# Start development server
python run.py

# Kill server on port 8000 if needed
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
# Alternative
pkill -f "uvicorn server:app"
```

### Testing
```bash
# Run YouTube API integration test (requires YOUTUBE_VIDEO_ID env var)
YOUTUBE_VIDEO_ID=動画ID python test_integration.py
```

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv obs_comment_caster
source obs_comment_caster/bin/activate  # Windows: .\obs_comment_caster\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env to set YOUTUBE_API_KEY
```

## Architecture Overview

This is a real-time YouTube live chat display system for OBS Studio streaming, built with FastAPI and WebSockets.

### Core Components

**server.py** - Main FastAPI application with ConnectionManager class that:
- Manages WebSocket connections for admin panel and display overlay
- Fetches YouTube live chat messages via YouTube Data API v3
- Handles message broadcasting to connected clients
- Manages sound notification and message display toggles

**youtube_utils.py** - YouTube API wrapper (YouTubeAPI class) that:
- Handles live chat ID retrieval from video/channel IDs
- Fetches and processes live chat messages with quota tracking
- Manages processed message deduplication
- Supports both regular chat and super chat messages

**Templates Structure**:
- `admin.html` - Management interface for selecting/controlling comments
- `chat_overlay.html` - OBS browser source overlay for displaying selected comments
- `emoji_map.json` - Maps `:emoji:` codes to image paths
- `sounds/` - Audio notification files

### WebSocket Communication Flow

1. **Admin Panel** (`/ws/admin`) sends:
   - `select_comment` - Display specific comment on overlay
   - `toggle_messages` - Enable/disable automatic message display
   - `toggle_sound` - Enable/disable sound notifications

2. **Display Overlay** (`/ws/display`) receives:
   - `selected_comment` - Shows manually selected comment
   - `chat` - Shows automatic live chat messages (if enabled)
   - `toggle_messages` - Controls automatic message visibility

### Configuration

**config.py** contains:
- `MESSAGE_FETCH_INTERVAL` - YouTube API polling interval (default: 3 seconds)
- `MAX_PROCESSED_MESSAGES` - Message deduplication cache size (default: 1000)
- `DEFAULT_PROFILE_IMAGE` - Fallback avatar URL

### Live Chat Integration

The system requires:
1. YouTube Data API v3 key in `.env` file
2. Live stream URL input in admin panel
3. OBS browser source pointing to `http://localhost:8000/`

URL formats supported:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`
- `https://youtu.be/VIDEO_ID`

### Key Development Notes

- Server runs on port 8000 by default
- WebSocket connections are managed per client type (admin/display)
- Sound notifications use HTML5 Audio API with `.wav` files
- Emoji replacement uses regex matching against emoji_map.json
- YouTube API quota usage is tracked and logged
- Message deduplication prevents duplicate displays
- Admin panel URL: `http://localhost:8000/admin`
- Overlay URL for OBS: `http://localhost:8000/`