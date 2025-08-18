import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0075 {
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
        
        // Step 1: Check current weather in San Francisco, CA for August 8, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get San Francisco, CA location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("San Francisco, CA");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData sfLocation = locations.get(0);
                double lat = sfLocation.getLatitude();
                double lon = sfLocation.getLongitude();
                
                // Get current weather for San Francisco, CA
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(lat, lon);
                
                weatherInfo.addProperty("city", currentWeather.getCityName());
                weatherInfo.addProperty("country", currentWeather.getCountry());
                weatherInfo.addProperty("date", currentWeather.getDate().toString());
                weatherInfo.addProperty("condition", currentWeather.getCondition());
                weatherInfo.addProperty("description", currentWeather.getDescription());
                weatherInfo.addProperty("temperature", currentWeather.getTemperature());
                weatherInfo.addProperty("feels_like", currentWeather.getFeelsLike());
                weatherInfo.addProperty("humidity", currentWeather.getHumidity());
                weatherInfo.addProperty("wind_speed", currentWeather.getWindSpeed());
                weatherInfo.addProperty("cloudiness", currentWeather.getCloudiness());
                weatherInfo.addProperty("target_date", "August 8, 2025");
                
                // Check if humidity is above 80%
                int humidity = currentWeather.getHumidity();
                boolean isAbove80Humidity = humidity > 80;
                weatherInfo.addProperty("above_80_percent_humidity", isAbove80Humidity);
                
                // Step 2: If humidity above 80%, search for dehumidifiers at Costco and select lowest price
                JsonObject costcoInfo = new JsonObject();
                if (isAbove80Humidity) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult dehumidifierResults = costco.searchProducts("dehumidifier");
                    
                    if (dehumidifierResults.products != null && !dehumidifierResults.products.isEmpty()) {
                        // Find the cheapest dehumidifier
                        costco_com.ProductInfo cheapestDehumidifier = null;
                        double lowestPrice = Double.MAX_VALUE;
                        
                        JsonArray dehumidifiersArray = new JsonArray();
                        for (costco_com.ProductInfo product : dehumidifierResults.products) {
                            JsonObject dehumidifierObj = new JsonObject();
                            dehumidifierObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                dehumidifierObj.addProperty("price", product.productPrice.amount);
                                dehumidifierObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount < lowestPrice) {
                                    lowestPrice = product.productPrice.amount;
                                    cheapestDehumidifier = product;
                                }
                            }
                            dehumidifiersArray.add(dehumidifierObj);
                        }
                        
                        costcoInfo.add("available_dehumidifiers", dehumidifiersArray);
                        costcoInfo.addProperty("dehumidifiers_found", dehumidifierResults.products.size());
                        
                        if (cheapestDehumidifier != null) {
                            JsonObject selectedDehumidifier = new JsonObject();
                            selectedDehumidifier.addProperty("product_name", cheapestDehumidifier.productName);
                            selectedDehumidifier.addProperty("price", cheapestDehumidifier.productPrice.amount);
                            selectedDehumidifier.addProperty("currency", cheapestDehumidifier.productPrice.currency);
                            selectedDehumidifier.addProperty("selection_reason", "Lowest price dehumidifier found");
                            costcoInfo.add("selected_dehumidifier", selectedDehumidifier);
                        }
                    } else {
                        costcoInfo.addProperty("dehumidifiers_found", 0);
                        costcoInfo.addProperty("message", "No dehumidifiers found at Costco");
                        if (dehumidifierResults.error != null) {
                            costcoInfo.addProperty("error", dehumidifierResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "Humidity not above 80%, skipping dehumidifier search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find top 2 Spotify tracks about fog
                Spotify spotify = new Spotify();
                JsonObject spotifyInfo = new JsonObject();
                
                try {
                    Spotify.SpotifySearchResult searchResult = spotify.searchItems("fog", "track", "US", 10, 0, null);
                    
                    if (searchResult.tracks != null && !searchResult.tracks.isEmpty()) {
                        // Get top 2 tracks (assuming they're already sorted by relevance)
                        List<Spotify.SpotifyTrack> topTracks = searchResult.tracks.subList(0, Math.min(2, searchResult.tracks.size()));
                        
                        JsonArray tracksArray = new JsonArray();
                        JsonArray booksSearchResults = new JsonArray();
                        
                        for (Spotify.SpotifyTrack track : topTracks) {
                            JsonObject trackObj = new JsonObject();
                            trackObj.addProperty("name", track.name);
                            trackObj.addProperty("artists", String.join(", ", track.artistNames));
                            trackObj.addProperty("popularity", track.popularity);
                            trackObj.addProperty("uri", track.uri);
                            tracksArray.add(trackObj);
                            
                            // Step 4: For each track, search for books about climate and pick most words in title
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> climateBooks = openLibrary.search("climate", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (climateBooks != null && !climateBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo mostWordsBook = null;
                                    int mostWords = 0;
                                    
                                    for (OpenLibrary.BookInfo book : climateBooks) {
                                        JsonObject bookObj = new JsonObject();
                                        bookObj.addProperty("title", book.title);
                                        
                                        // Count words in title (split by spaces and count non-empty parts)
                                        int wordCount = countWordsInTitle(book.title);
                                        bookObj.addProperty("word_count", wordCount);
                                        booksArray.add(bookObj);
                                        
                                        if (wordCount > mostWords) {
                                            mostWords = wordCount;
                                            mostWordsBook = book;
                                        }
                                    }
                                    
                                    trackBooksInfo.add("available_books", booksArray);
                                    trackBooksInfo.addProperty("books_found", climateBooks.size());
                                    
                                    if (mostWordsBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", mostWordsBook.title);
                                        selectedBook.addProperty("word_count", countWordsInTitle(mostWordsBook.title));
                                        selectedBook.addProperty("selection_reason", "Book with most words in title about climate");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about climate found");
                                }
                            } catch (java.io.IOException | InterruptedException e) {
                                trackBooksInfo.addProperty("error", "Failed to search books: " + e.getMessage());
                            }
                            
                            booksSearchResults.add(trackBooksInfo);
                        }
                        
                        spotifyInfo.add("top_tracks", tracksArray);
                        spotifyInfo.addProperty("tracks_found", topTracks.size());
                        spotifyInfo.add("books_for_tracks", booksSearchResults);
                    } else {
                        spotifyInfo.addProperty("tracks_found", 0);
                        spotifyInfo.addProperty("message", "No tracks about fog found on Spotify");
                        if (searchResult.errorMessage != null) {
                            spotifyInfo.addProperty("error", searchResult.errorMessage);
                        }
                    }
                } catch (RuntimeException e) {
                    spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
                }
                
                result.add("spotify_and_books_search", spotifyInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for San Francisco, CA");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        
        result.add("weather_info", weatherInfo);
        result.addProperty("task_summary", "Check San Francisco weather for Aug 8, 2025. If humidity above 80%, find lowest price Costco dehumidifier and top 2 fog tracks with most words in climate books.");
        result.addProperty("target_date", "August 8, 2025");
        result.addProperty("location", "San Francisco, CA");
        
        return result;
    }
    
    /**
     * Helper method to count words in a title
     * Splits by whitespace and counts non-empty parts
     */
    private static int countWordsInTitle(String title) {
        if (title == null || title.trim().isEmpty()) {
            return 0;
        }
        
        // Split by whitespace and filter out empty strings
        String[] words = title.trim().split("\\s+");
        return words.length;
    }
}
