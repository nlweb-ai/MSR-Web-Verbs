import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0082 {
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
        
        // Step 1: Get NASA's Astronomy Picture of the Day for inspiration
        Nasa nasa = new Nasa();
        String targetDate = "2025-08-12"; // August 12, 2025
        
        JsonObject apodInfo = new JsonObject();
        try {
            Nasa.ApodResult apodResult = nasa.getApod(targetDate, true);
            apodInfo.addProperty("title", apodResult.title);
            apodInfo.addProperty("url", apodResult.url);
            apodInfo.addProperty("explanation", apodResult.explanation);
            apodInfo.addProperty("date", apodResult.date.toString());
            
            // Determine space theme based on title and explanation
            String theme = determineSpaceTheme(apodResult.title, apodResult.explanation);
            apodInfo.addProperty("space_theme", theme);
        } catch (IOException | InterruptedException e) {
            apodInfo.addProperty("error", "Failed to fetch APOD: " + e.getMessage());
            apodInfo.addProperty("space_theme", "stars"); // default theme
        }
        result.add("nasa_apod", apodInfo);
        
        // Step 2: Search Amazon for kitchen supplies related to space theme
        amazon_com amazon = new amazon_com(context);
        String spaceTheme = apodInfo.has("space_theme") ? apodInfo.get("space_theme").getAsString() : "stars";
        String kitchenSearchTerm = getKitchenSearchTerm(spaceTheme);
        
        amazon_com.CartResult kitchenSupplies = amazon.addItemToCart(kitchenSearchTerm);
        
        JsonObject kitchenInfo = new JsonObject();
        kitchenInfo.addProperty("search_term", kitchenSearchTerm);
        JsonArray kitchenItemsArray = new JsonArray();
        for (amazon_com.CartItem item : kitchenSupplies.items) {
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("item_name", item.itemName);
            if (item.price != null) {
                itemObj.addProperty("price", item.price.amount);
                itemObj.addProperty("currency", item.price.currency);
            }
            kitchenItemsArray.add(itemObj);
        }
        kitchenInfo.add("kitchen_supplies", kitchenItemsArray);
        result.add("amazon_kitchen_search", kitchenInfo);
        
        // Step 3: Search OpenLibrary for cooking and baking books related to space theme
        OpenLibrary openLibrary = new OpenLibrary();
        String bookQuery = "space cooking baking recipes";
        
        JsonObject booksInfo = new JsonObject();
        try {
            java.util.List<OpenLibrary.BookInfo> books = openLibrary.search(bookQuery, null, null, null, 10, 1);
            booksInfo.addProperty("search_query", bookQuery);
            JsonArray booksArray = new JsonArray();
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                booksArray.add(bookObj);
            }
            booksInfo.add("books", booksArray);
        } catch (Exception e) {
            booksInfo.addProperty("error", "Failed to search books: " + e.getMessage());
            booksInfo.add("books", new JsonArray());
        }
        result.add("openlibrary_books", booksInfo);
        
        // Step 4: Search Spotify for top 3 cooking/baking playlists
        Spotify spotify = new Spotify();
        String playlistQuery = "cooking baking kitchen";
        
        JsonObject spotifyInfo = new JsonObject();
        try {
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems(playlistQuery, "playlist", null, 3, 0, null);
            if (spotifyResult.errorMessage != null) {
                spotifyInfo.addProperty("error", spotifyResult.errorMessage);
                spotifyInfo.add("playlists", new JsonArray());
            } else {
                spotifyInfo.addProperty("search_query", playlistQuery);
                JsonArray playlistsArray = new JsonArray();
                for (Spotify.SpotifyPlaylist playlist : spotifyResult.playlists) {
                    JsonObject playlistObj = new JsonObject();
                    playlistObj.addProperty("name", playlist.name);
                    playlistObj.addProperty("description", playlist.description);
                    playlistObj.addProperty("owner", playlist.ownerName);
                    playlistObj.addProperty("total_tracks", playlist.totalTracks);
                    playlistObj.addProperty("uri", playlist.uri);
                    playlistsArray.add(playlistObj);
                }
                spotifyInfo.add("playlists", playlistsArray);
            }
        } catch (Exception e) {
            spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
            spotifyInfo.add("playlists", new JsonArray());
        }
        result.add("spotify_playlists", spotifyInfo);
        
        return result;
    }
    
    // Helper method to determine space theme based on APOD content
    private static String determineSpaceTheme(String title, String explanation) {
        String content = (title + " " + explanation).toLowerCase();
        if (content.contains("planet") || content.contains("mars") || content.contains("venus") || 
            content.contains("jupiter") || content.contains("saturn") || content.contains("mercury") ||
            content.contains("neptune") || content.contains("uranus")) {
            return "planets";
        } else if (content.contains("galaxy") || content.contains("galaxies") || content.contains("milky way") ||
                   content.contains("andromeda") || content.contains("spiral")) {
            return "galaxies";
        } else {
            return "stars";
        }
    }
    
    // Helper method to get kitchen search term based on space theme
    private static String getKitchenSearchTerm(String theme) {
        switch (theme) {
            case "planets":
                return "planet-shaped baking molds";
            case "galaxies":
                return "galaxy swirl cake pans";
            default:
                return "star-shaped cookie cutters";
        }
    }
}
