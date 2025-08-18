import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0085 {
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
        JsonObject result = new JsonObject();
        
        // Step 1: Search OpenLibrary for science fiction books published in the last 2 years
        OpenLibrary openLibrary = new OpenLibrary();
        String sciFiQuery = "science fiction";
        
        JsonObject booksInfo = new JsonObject();
        try {
            java.util.List<OpenLibrary.BookInfo> books = openLibrary.search(sciFiQuery, null, "new", null, 50, 1);
            booksInfo.addProperty("search_query", sciFiQuery);
            booksInfo.addProperty("total_books_found", books.size());
            
            // Calculate number of meetings needed (1 book per meeting)
            int meetingsNeeded = books.size();
            booksInfo.addProperty("meetings_needed", meetingsNeeded);
            
            JsonArray booksArray = new JsonArray();
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                booksArray.add(bookObj);
            }
            booksInfo.add("science_fiction_books", booksArray);
        } catch (Exception e) {
            booksInfo.addProperty("error", "Failed to search sci-fi books: " + e.getMessage());
            booksInfo.add("science_fiction_books", new JsonArray());
            booksInfo.addProperty("total_books_found", 0);
            booksInfo.addProperty("meetings_needed", 0);
        }
        result.add("openlibrary_scifi_books", booksInfo);
        
        // Step 2: Search for meeting supplies and snacks at Costco
        costco_com costco = new costco_com(context);
        String[] meetingSupplies = {"meeting supplies", "snacks", "coffee"};
        
        JsonObject costcoInfo = new JsonObject();
        JsonArray suppliesArray = new JsonArray();
        
        for (String supply : meetingSupplies) {
            costco_com.ProductInfo productResult = costco.searchProduct(supply);
            JsonObject supplyObj = new JsonObject();
            supplyObj.addProperty("search_term", supply);
            
            if (productResult.error != null) {
                supplyObj.addProperty("error", productResult.error);
            } else {
                supplyObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    supplyObj.addProperty("price", productResult.productPrice.amount);
                    supplyObj.addProperty("currency", productResult.productPrice.currency);
                }
            }
            suppliesArray.add(supplyObj);
        }
        costcoInfo.add("book_club_supplies", suppliesArray);
        result.add("costco_supplies", costcoInfo);
        
        // Step 3: Find top 4 sci-fi themed tracks on Spotify
        Spotify spotify = new Spotify();
        String sciFiMusicQuery = "sci-fi science fiction space cosmic";
        
        JsonObject spotifyInfo = new JsonObject();
        try {
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems(sciFiMusicQuery, "track", null, 4, 0, null);
            if (spotifyResult.errorMessage != null) {
                spotifyInfo.addProperty("error", spotifyResult.errorMessage);
                spotifyInfo.add("scifi_tracks", new JsonArray());
            } else {
                spotifyInfo.addProperty("search_query", sciFiMusicQuery);
                JsonArray tracksArray = new JsonArray();
                for (Spotify.SpotifyTrack track : spotifyResult.tracks) {
                    JsonObject trackObj = new JsonObject();
                    trackObj.addProperty("name", track.name);
                    trackObj.addProperty("artists", String.join(", ", track.artistNames));
                    trackObj.addProperty("album", track.albumName);
                    trackObj.addProperty("popularity", track.popularity);
                    trackObj.addProperty("uri", track.uri);
                    if (track.duration != null) {
                        long minutes = track.duration.toMinutes();
                        long seconds = track.duration.getSeconds() % 60;
                        trackObj.addProperty("duration", String.format("%d:%02d", minutes, seconds));
                    }
                    tracksArray.add(trackObj);
                }
                spotifyInfo.add("scifi_tracks", tracksArray);
            }
        } catch (Exception e) {
            spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
            spotifyInfo.add("scifi_tracks", new JsonArray());
        }
        result.add("spotify_scifi_music", spotifyInfo);
        
        // Step 4: Get NASA's Near Earth Objects data for space facts
        Nasa nasa = new Nasa();
        
        JsonObject nasaInfo = new JsonObject();
        try {
            // Get NEO data for a recent date range
            java.util.List<Nasa.NeoResult> neoData = nasa.getNeoFeed("2025-08-18", "2025-08-18");
            nasaInfo.addProperty("neo_count", neoData.size());
            
            JsonArray neoArray = new JsonArray();
            for (Nasa.NeoResult neo : neoData) {
                JsonObject neoObj = new JsonObject();
                neoObj.addProperty("name", neo.name);
                neoObj.addProperty("id", neo.id);
                if (neo.closeApproachDate != null) {
                    neoObj.addProperty("close_approach_date", neo.closeApproachDate.toString());
                }
                if (neo.estimatedDiameterKm != null) {
                    neoObj.addProperty("estimated_diameter_km", neo.estimatedDiameterKm);
                }
                neoArray.add(neoObj);
            }
            nasaInfo.add("near_earth_objects", neoArray);
        } catch (IOException | InterruptedException e) {
            nasaInfo.addProperty("error", "Failed to fetch NEO data: " + e.getMessage());
            nasaInfo.add("near_earth_objects", new JsonArray());
            nasaInfo.addProperty("neo_count", 0);
        }
        result.add("nasa_neo_data", nasaInfo);
        
        // Summary for book club planning
        JsonObject clubSummary = new JsonObject();
        int totalBooks = booksInfo.has("total_books_found") ? booksInfo.get("total_books_found").getAsInt() : 0;
        int totalNeos = nasaInfo.has("neo_count") ? nasaInfo.get("neo_count").getAsInt() : 0;
        
        clubSummary.addProperty("book_club_location", "Denver, Colorado");
        clubSummary.addProperty("meeting_date", "2025-08-18");
        clubSummary.addProperty("total_scifi_books_available", totalBooks);
        clubSummary.addProperty("estimated_meetings_needed", totalBooks);
        clubSummary.addProperty("space_facts_available", totalNeos);
        clubSummary.addProperty("ambient_music_tracks", 4);
        result.add("book_club_summary", clubSummary);
        
        return result;
    }
}
