import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0031 {
    static BrowserContext context = null;
    static java.util.Scanner scanner= new java.util.Scanner(System.in);
    public static void main(String[] args) {
        
        try (Playwright playwright = Playwright.create()) {
            String userDataDir = System.getProperty("user.home") +"\\AppData\\Local\\Google\\Chrome\\User Data\\Default";

            BrowserType.LaunchPersistentContextOptions options = new BrowserType.LaunchPersistentContextOptions().setChannel("chrome").setHeadless(false).setArgs(java.util.Arrays.asList("--start-maximized"));

            //please add the following option to the options:
            //new Browser.NewContextOptions().setViewportSize(null)
            options.setViewportSize(null);
            
            context = playwright.chromium().launchPersistentContext(Paths.get(userDataDir), options);


            //browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(false).setArgs(java.util.Arrays.asList("--start-maximized")));
            //Browser browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("msedge").setHeadless(false).setArgs(java.util.Arrays.asList("--start-maximized")));

            JsonObject result = automate(context);
            Gson gson = new GsonBuilder()
                .disableHtmlEscaping()
                .setPrettyPrinting()
                .create();
            String prettyResult = gson.toJson(result);
            System.out.println("Final output: " + prettyResult);
            System.out.print("Press Enter to exit...");
            scanner.nextLine(); 
            
            context.close();
        }
    }

    /* Do not modify anything above this line. 
       The following "automate(...)" function is the one you should modify. 
       The current function body is just an example specifically about youtube.
    */
    static JsonObject automate(BrowserContext context) {
        JsonObject output = new JsonObject();
        
        try {
            // Step 1: Search for books by Agatha Christie using OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            List<OpenLibrary.BookInfo> books = openLibrary.search("Agatha Christie", null, null, "en", 10, 1);
            
            JsonArray bookArray = new JsonArray();
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                bookArray.add(bookObj);
            }
            output.add("agatha_christie_books", bookArray);
            
            // Step 2: Find recent news articles about Agatha Christie using News
            News news = new News();
            LocalDate fromDate = LocalDate.of(2025, 7, 1); // Search from beginning of 2024
            LocalDate toDate = LocalDate.of(2025, 8, 1);   // Up to current date
            News.NewsResponse newsResponse = news.searchEverything("Agatha Christie", null, null, null, 
                                                                 null, fromDate, toDate, "en", 
                                                                 "publishedAt", 10, 1);
            
            JsonArray newsArray = new JsonArray();
            if (newsResponse != null && newsResponse.articles != null) {
                for (News.NewsArticle article : newsResponse.articles) {
                    JsonObject articleObj = new JsonObject();
                    articleObj.addProperty("title", article.title);
                    articleObj.addProperty("description", article.description);
                    articleObj.addProperty("url", article.url);
                    articleObj.addProperty("source", article.source);
                    articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                    newsArray.add(articleObj);
                }
            }
            output.add("recent_news", newsArray);
            
            // Step 3: Find playlists inspired by Agatha Christie novels using Spotify
            Spotify spotify = new Spotify();
            List<Spotify.SpotifyPlaylist> playlists1 = spotify.searchPlaylists("Agatha Christie", "US", 5);
            List<Spotify.SpotifyPlaylist> playlists2 = spotify.searchPlaylists("mystery novel", "US", 5);
            List<Spotify.SpotifyPlaylist> playlists3 = spotify.searchPlaylists("detective fiction", "US", 5);
            
            JsonArray playlistArray = new JsonArray();
            
            // Add Agatha Christie playlists
            if (playlists1 != null) {
                for (Spotify.SpotifyPlaylist playlist : playlists1) {
                    JsonObject playlistObj = new JsonObject();
                    playlistObj.addProperty("name", playlist.name);
                    playlistObj.addProperty("description", playlist.description);
                    playlistObj.addProperty("owner", playlist.ownerName);
                    playlistObj.addProperty("totalTracks", playlist.totalTracks);
                    playlistObj.addProperty("category", "Agatha Christie");
                    playlistArray.add(playlistObj);
                }
            }
            
            // Add mystery novel playlists
            if (playlists2 != null) {
                for (Spotify.SpotifyPlaylist playlist : playlists2) {
                    JsonObject playlistObj = new JsonObject();
                    playlistObj.addProperty("name", playlist.name);
                    playlistObj.addProperty("description", playlist.description);
                    playlistObj.addProperty("owner", playlist.ownerName);
                    playlistObj.addProperty("totalTracks", playlist.totalTracks);
                    playlistObj.addProperty("category", "Mystery Novel");
                    playlistArray.add(playlistObj);
                }
            }
            
            // Add detective fiction playlists
            if (playlists3 != null) {
                for (Spotify.SpotifyPlaylist playlist : playlists3) {
                    JsonObject playlistObj = new JsonObject();
                    playlistObj.addProperty("name", playlist.name);
                    playlistObj.addProperty("description", playlist.description);
                    playlistObj.addProperty("owner", playlist.ownerName);
                    playlistObj.addProperty("totalTracks", playlist.totalTracks);
                    playlistObj.addProperty("category", "Detective Fiction");
                    playlistArray.add(playlistObj);
                }
            }
            
            output.add("music_playlists", playlistArray);
            
            // Step 4: Find interesting facts about Agatha Christie using Wikimedia
            Wikimedia wikimedia = new Wikimedia();
            Wikimedia.SearchResult searchResult = wikimedia.search("Agatha Christie", "en", 10);
            
            JsonArray factsArray = new JsonArray();
            if (searchResult != null && searchResult.titles != null) {
                for (String title : searchResult.titles) {
                    // Get page info for each relevant title
                    Wikimedia.PageInfo pageInfo = wikimedia.getPage(title);
                    if (pageInfo != null) {
                        JsonObject factObj = new JsonObject();
                        factObj.addProperty("title", pageInfo.title);
                        factObj.addProperty("htmlUrl", pageInfo.htmlUrl);
                        factObj.addProperty("lastModified", pageInfo.lastModified != null ? pageInfo.lastModified.toString() : null);
                        factsArray.add(factObj);
                    }
                }
            }
            output.add("wikipedia_facts", factsArray);
            
            // Step 5: Create summary and recommendations
            JsonObject summary = new JsonObject();
            summary.addProperty("event", "Book Club Meeting - Agatha Christie Focus");
            summary.addProperty("date", "August 10, 2025");
            summary.addProperty("location", "Seattle");
            summary.addProperty("theme", "Agatha Christie and Mystery Fiction");
            
            JsonObject recommendations = new JsonObject();
            
            // Book recommendations
            JsonArray bookRecommendations = new JsonArray();
            if (!books.isEmpty()) {
                for (int i = 0; i < Math.min(5, books.size()); i++) {
                    bookRecommendations.add(books.get(i).title);
                }
            }
            recommendations.add("top_book_selections", bookRecommendations);
            
            // Music recommendations
            JsonArray musicRecommendations = new JsonArray();
            if (playlists1 != null && !playlists1.isEmpty()) {
                for (int i = 0; i < Math.min(3, playlists1.size()); i++) {
                    musicRecommendations.add(playlists1.get(i).name);
                }
            }
            recommendations.add("recommended_playlists", musicRecommendations);
            
            // Discussion topics from news
            JsonArray discussionTopics = new JsonArray();
            if (newsResponse != null && newsResponse.articles != null) {
                for (int i = 0; i < Math.min(3, newsResponse.articles.size()); i++) {
                    discussionTopics.add(newsResponse.articles.get(i).title);
                }
            }
            recommendations.add("discussion_topics_from_news", discussionTopics);
            
            summary.add("recommendations", recommendations);
            output.add("book_club_summary", summary);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
