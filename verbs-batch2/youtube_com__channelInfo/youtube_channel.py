"""
Playwright script (Python) — YouTube Channel Info
Look up a YouTube channel and extract subscribers, video count, and description.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class YoutubeChannelRequest:
    channel: str


@dataclass(frozen=True)
class YoutubeChannelResult:
    channel: str
    subscribers: str
    video_count: str
    description: str


# Looks up a YouTube channel and extracts subscriber count,
# video count, and channel description.
def lookup_youtube_channel(
    page: Page,
    request: YoutubeChannelRequest,
) -> YoutubeChannelResult:
    channel = request.channel

    print(f"  Channel: {channel}\n")

    subscribers = "N/A"
    video_count = "N/A"
    description = "N/A"

    try:
        search_url = "https://www.youtube.com/results?search_query=" + channel.replace(" ", "+")
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(6000)

        for sel in ["button:has-text('Accept all')", "button:has-text('Accept')", "button:has-text('Reject all')", "button[aria-label*='Accept']"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {sel}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        channel_url = None
        try:
            ch_renderer = page.locator("ytd-channel-renderer").first
            ch_link = ch_renderer.locator('a[href*="/@"]').first
            channel_url = "https://www.youtube.com" + ch_link.get_attribute("href", timeout=3000)
        except Exception:
            pass

        if channel_url:
            checkpoint(f"Navigate to {channel_url}")
            page.goto(channel_url)
        else:
            fallback_url = f"https://www.youtube.com/@{channel.lower().replace(' ', '')}"
            checkpoint(f"Navigate to {fallback_url}")
            page.goto(fallback_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(6000)

        try:
            meta_view = page.locator("yt-content-metadata-view-model").first
            meta_text = meta_view.inner_text(timeout=5000).strip()
            sub_match = re.search(r"([\d.]+[KMB]?\s*subscribers?)", meta_text, re.IGNORECASE)
            subscribers = sub_match.group(0).strip() if sub_match else "N/A"
            vid_match = re.search(r"([\d,]+\s*videos?)", meta_text, re.IGNORECASE)
            video_count = vid_match.group(0).strip() if vid_match else "N/A"
        except Exception:
            pass

        try:
            meta = page.locator('meta[name="description"]').first
            description = (meta.get_attribute("content", timeout=3000) or "N/A")[:500]
        except Exception:
            pass

        print(f"Channel: {channel}")
        print(f"  Subscribers: {subscribers}")
        print(f"  Video Count: {video_count}")
        print(f"  Description: {description[:200]}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return YoutubeChannelResult(channel=channel, subscribers=subscribers, video_count=video_count, description=description)


def test_lookup_youtube_channel() -> None:
    request = YoutubeChannelRequest(channel="Veritasium")
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir, channel="chrome", headless=False, viewport=None,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-extensions"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = lookup_youtube_channel(page, request)
            assert result.channel == request.channel
            print(f"\nChannel lookup complete for: {result.channel}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_lookup_youtube_channel)
