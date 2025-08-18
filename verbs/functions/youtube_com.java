import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Locator;

public class youtube_com extends com_base {
    /**
     * Represents information about a YouTube video result.
     */
    public class YouTubeVideoInfo {
        /** The title of the video. */
        public String title;
        /** The duration/length of the video. */
        public Duration length;
        /** The URL of the video. */
        public String url;

        public YouTubeVideoInfo(String title, String lengthStr, String url) {
            this.title = title;
            this.length = parseDuration(lengthStr);
            this.url = url;
        }

        private Duration parseDuration(String s) {
            if (s == null || s.isEmpty()) return Duration.ZERO;
            String[] parts = s.split(":");
            int h = 0, m = 0, sec = 0;
            if (parts.length == 3) {
                h = Integer.parseInt(parts[0]);
                m = Integer.parseInt(parts[1]);
                sec = Integer.parseInt(parts[2]);
            } else if (parts.length == 2) {
                m = Integer.parseInt(parts[0]);
                sec = Integer.parseInt(parts[1]);
            } else if (parts.length == 1) {
                sec = Integer.parseInt(parts[0]);
            }
            return Duration.ofHours(h).plusMinutes(m).plusSeconds(sec);
        }

        @Override
        public String toString() {
            long s = length.getSeconds();
            long h = s / 3600;
            long m = (s % 3600) / 60;
            long sec = s % 60;
            String lenStr = h > 0 ? String.format("%d:%02d:%02d", h, m, sec) : String.format("%d:%02d", m, sec);
            return String.format("YouTubeVideoInfo{title='%s', length='%s', url='%s'}", title, lenStr, url);
        }
    }
    public youtube_com(BrowserContext _context) {
        super(_context);
    }

    /**
     * Searches YouTube for a query and returns the top 5 video results as a list of YouTubeVideoInfo objects.
     *
     * @param query The search query (e.g., "quantum physics").
     * @return List of YouTubeVideoInfo objects containing title, length, and url for each video.
     */
    public List<YouTubeVideoInfo> searchVideos(String query) {
        List<YouTubeVideoInfo> videos = new ArrayList<>();
        try {
            page.navigate("https://www.youtube.com/");
            // Find the search box and enter the query
            Locator searchBox = page.locator("input[name='search_query']");
            if (searchBox.count() == 0) {
                searchBox = page.locator(".ytSearchboxComponentInput");
            }
            searchBox.first().click();
            searchBox.first().fill(query);
            searchBox.first().press("Enter");
            page.waitForTimeout(4000);

            // For each of the first 5 video results
            for (int i = 1; i <= 5; i++) {
                // Find the badge/length element for the i-th video
                String badgeSelector = String.format("#contents > .style-scope:nth-child(%d) > #dismissible .badge-shape-wiz__text", i);
                Locator badge = page.locator(badgeSelector);
                if (badge.count() > 0) {
                    // Go up to the video container
                    Locator videoContainer = badge.first().locator("..").locator("..")
                        .locator("..").locator("..").locator("..").locator("..").locator("..").locator("..").first();
                    // Get video length
                    String length = badge.first().innerText();
                    // Get video title
                    Locator titleLocator = videoContainer.locator("#video-title");
                    String title = titleLocator.count() > 0 ? titleLocator.first().innerText() : "No title found";
                    // Get video URL
                    String url = titleLocator.count() > 0 ? titleLocator.first().getAttribute("href") : null;
                    if (url != null && !url.startsWith("http")) {
                        url = "https://youtube.com" + url;
                    }
                    videos.add(new YouTubeVideoInfo(title, length, url != null ? url : "No url found"));
                }
            }
        } catch (Exception e) {
            videos.clear();
            videos.add(new YouTubeVideoInfo("Error: " + e.getMessage(), "", ""));
        }
        return videos;
    }
}
