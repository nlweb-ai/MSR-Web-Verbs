import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class GeniusSongRequest:
    query: str = "Bohemian Rhapsody Queen"

@dataclass(frozen=True)
class GeniusSongResult:
    song_title: str = ""
    artist: str = ""
    album: str = ""
    first_verse: str = ""

# Search for a song on Genius, click the top result, and extract
# song title, artist name, album name, and first verse of lyrics.
def genius_song(page: Page, request: GeniusSongRequest) -> GeniusSongResult:
    query = request.query
    print(f"  Search query: {query}\n")

    url = f"https://genius.com/search?q={quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Genius search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    # Find and click the first search result link
    first_result = page.locator(
        'a[class*="mini_card"], '
        'a[href*="genius.com/"][class*="result"], '
        'a[href*="-lyrics"], '
        'div[class*="search_result"] a'
    ).first

    try:
        first_result.click(timeout=5000)
    except Exception:
        # Fallback: try any link that looks like a song lyrics page
        fallback = page.locator('a[href*="-lyrics"]').first
        fallback.click(timeout=5000)

    page.wait_for_timeout(8000)
    print(f"  Song page: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    song_title = ""
    artist = ""
    album = ""
    first_verse = ""

    # Extract song title
    title_el = page.locator('h1[class*="SongHeader"], h1[class*="title"], span[class*="SongHeader"]')
    if title_el.count() > 0:
        song_title = title_el.first.inner_text(timeout=3000).strip()
    if not song_title:
        m = re.search(r'^(.+?)\s+Lyrics', body_text, re.MULTILINE)
        if m:
            song_title = m.group(1).strip()

    # Extract artist name
    artist_el = page.locator('a[class*="SongHeader"][href*="/artists/"], a[class*="Artist"], a[href*="/artists/"]')
    if artist_el.count() > 0:
        artist = artist_el.first.inner_text(timeout=3000).strip()
    if not artist:
        m = re.search(r'by\s+(.+)', body_text[:2000])
        if m:
            artist = m.group(1).strip().split('\n')[0]

    # Extract album name
    album_el = page.locator('a[class*="Album"], a[href*="/albums/"], div[class*="album"] a')
    if album_el.count() > 0:
        album = album_el.first.inner_text(timeout=3000).strip()
    if not album:
        m = re.search(r'Album\s+(.+)', body_text)
        if m:
            album = m.group(1).strip().split('\n')[0]

    # Extract first verse of lyrics
    lyrics_container = page.locator(
        'div[data-lyrics-container="true"], '
        'div[class*="Lyrics__Container"], '
        'div[class*="lyrics"] div[class*="Container"]'
    )
    if lyrics_container.count() > 0:
        # Collect text from all lyrics containers
        all_lyrics = ""
        for i in range(lyrics_container.count()):
            txt = lyrics_container.nth(i).inner_text(timeout=5000).strip()
            if txt:
                all_lyrics += txt + "\n\n"
        # Find section markers like [Intro], [Verse 1] etc. and extract the first section content
        sections = re.split(r'\[(?:Intro|Verse[^\]]*|Chorus[^\]]*|Pre-Chorus[^\]]*)\]\s*\n*', all_lyrics)
        # First real section with lyrics content (skip preamble/description)
        for sec in sections[1:]:  # skip the first split part (description before first marker)
            sec = sec.strip()
            # Take content up to next section marker or end
            sec = re.split(r'\[', sec)[0].strip()
            if sec and len(sec) > 10:
                first_verse = sec
                break
    if not first_verse:
        # Fallback: look for [Intro] or [Verse 1] section in body text
        m = re.search(r'\[(Intro|Verse[^\]]*)\]\s*\n(.+?)(?:\n\s*\n|\[)', body_text, re.DOTALL)
        if m:
            first_verse = m.group(2).strip()

    print("=" * 60)
    print(f"Genius - Song Details for \"{query}\"")
    print("=" * 60)
    print(f"  Song Title:  {song_title}")
    print(f"  Artist:      {artist}")
    print(f"  Album:       {album}")
    print(f"  First Verse: {first_verse[:200]}{'...' if len(first_verse) > 200 else ''}")

    return GeniusSongResult(
        song_title=song_title,
        artist=artist,
        album=album,
        first_verse=first_verse,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = genius_song(page, GeniusSongRequest())
        print(f"\nSong: {result.song_title} by {result.artist}")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
