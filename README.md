# Spotify Data Tools

Collection of Python scripts for working with the Spotify API to transfer playlists, liked tracks, albums, and integrate with Jellyfin.

## Features

- **Account Migration**: Transfer playlists, liked tracks, albums, and followed artists between Spotify accounts
- **Jellyfin Integration**: Sync Spotify playlists with Jellyfin media server
- **Data Export**: Export comprehensive Spotify statistics and listening history
- **Bulk Operations**: Handle large libraries with progress tracking

## Prerequisites

- Python 3.7+
- Spotify Developer Account with API credentials
- (Optional) Jellyfin server for media integration

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Required packages:
   - `spotipy` - Spotify Web API wrapper
   - `python-dotenv` - Environment variable management
   - `tqdm` - Progress bars
   - `requests` - HTTP library

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your credentials:**
   - Get Spotify API credentials from https://developer.spotify.com/dashboard
   - Create two apps (source and target) if transferring between accounts
   - Add your Jellyfin API key if using spotJelly.py

## Scripts

### spotify_account_transfer.py (formerly cheech.py)

Transfers data between two Spotify accounts.

**Transfers:**
- [x] Playlists (with all tracks)
- [x] Liked tracks
- [x] Saved albums
- [x] Followed artists
- [x] Subscribed podcasts

**Usage:**
```bash
python3 spotify_account_transfer.py
```

**Environment variables required:**
- `SOURCE_CLIENT_ID`, `SOURCE_CLIENT_SECRET`, `SOURCE_USERNAME`
- `TARGET_CLIENT_ID`, `TARGET_CLIENT_SECRET`, `TARGET_USERNAME`

### spotify_to_jellyfin.py (formerly spotJelly.py)

Syncs Spotify playlists with Jellyfin media server.

**Usage:**
```bash
python3 spotify_to_jellyfin.py
```

**Environment variables required:**
- `SOURCE_CLIENT_ID`, `SOURCE_CLIENT_SECRET`
- `JELLYFIN_API_KEY`, `JELLYFIN_URL`

### spotify_data_export.py (formerly zfa.py)

Exports all Spotify data (statistics, top tracks/artists, listening history) to a text file.

**Exports:**
- [x] Top tracks and artists
- [x] Recently played tracks
- [x] Followed podcasts
- [x] Saved albums and tracks
- [x] Artist occurrences
- [x] Track play count rankings

**Usage:**
```bash
python3 spotify_data_export.py
```

**Environment variables required:**
- `SOURCE_CLIENT_ID`, `SOURCE_CLIENT_SECRET`, `SOURCE_USERNAME`

**Output:** Creates `all_spotify_data.txt` with all exported data.

### Archived Files

The following files have been archived (`.bak` extension):
- `spotify_account_transfer_old.py.bak` - Old test version of account transfer
- `windows_wallpaper_changer.py.bak` - Windows utility (unrelated to Spotify)

## Authentication Flow

1. Run the script
2. A browser window opens for Spotify OAuth
3. Authorize the application
4. You'll be redirected to localhost (this is normal)
5. Copy the full redirected URL back to the terminal
6. Script proceeds with data transfer

## Security Notes

- Never commit `.env` file with real credentials
- Cache files (`.cache-*`) contain tokens - excluded from git
- Production data files (`*.txt`) are excluded from version control
- Keep API keys and client secrets private

## Troubleshooting

**"Missing required environment variables":**
- Ensure `.env` file exists and contains all required variables
- Check variable names match exactly (case-sensitive)

**"Redirect URI mismatch":**
- Verify redirect URIs in `.env` match those configured in Spotify Developer Dashboard
- Default: `http://localhost:8080/callback` (source), `http://localhost:8081/callback` (target)

**Rate limiting:**
- Spotify API has rate limits
- Scripts include automatic retries and delays
- Large transfers may take time

**OAuth cache issues:**
- Delete `.cache-*` files if authentication fails
- Re-authenticate when prompted

## API Rate Limits

Spotify API limits:
- 180 requests per minute per user
- Scripts handle pagination automatically
- Progress bars show transfer status

## Development Notes

**v2.0 Changes (2026-01-30):**
Scripts renamed to descriptive names:
   - `cheech.py` -> `spotify_account_transfer.py`
   - `spotJelly.py` -> `spotify_to_jellyfin.py`
   - `zfa.py` -> `spotify_data_export.py`

Security improvements:
   - Removed hardcoded credentials from `spotify_data_export.py`
   - All scripts now use environment variables
   - Credentials never committed to repository

Code cleanup:
   - Archived redundant test files
   - Removed unrelated scripts
   - Translated French comments to English

**Future Improvements:**
1. Add unit tests for core functions
2. Implement retry logic for API failures
3. Add export to JSON format option

## Contributing

This is a private repository for personal use. Ensure:
- No production credentials are committed
- No personal Spotify data is pushed
- All sensitive files are in `.gitignore`

## License

Private project - not for public distribution.
