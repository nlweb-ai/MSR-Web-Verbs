import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0080 {
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
        
        // Step 1: Check weather forecast for Los Angeles, CA for August 13, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get Los Angeles, CA location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Los Angeles, CA");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData laLocation = locations.get(0);
                double lat = laLocation.getLatitude();
                double lon = laLocation.getLongitude();
                
                // Get 5-day weather forecast for Los Angeles, CA
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                
                weatherInfo.addProperty("city", forecast.getCityName());
                weatherInfo.addProperty("country", forecast.getCountry());
                weatherInfo.addProperty("target_date", "August 13, 2025");
                
                // Check forecast for high UV conditions (clear/sunny weather with low cloudiness)
                boolean hasHighUV = false;
                JsonArray forecastArray = new JsonArray();
                
                for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                    JsonObject entryObj = new JsonObject();
                    entryObj.addProperty("date", entry.getDateTime().toString());
                    entryObj.addProperty("temperature", entry.getTemperature());
                    entryObj.addProperty("condition", entry.getCondition());
                    entryObj.addProperty("description", entry.getDescription());
                    entryObj.addProperty("cloudiness", entry.getCloudiness());
                    
                    // High UV proxy: clear/sunny conditions with low cloudiness (<30%)
                    String condition = entry.getCondition().toLowerCase();
                    int cloudiness = entry.getCloudiness();
                    boolean isHighUVCondition = (condition.contains("clear") || condition.contains("sun")) && cloudiness < 30;
                    
                    entryObj.addProperty("high_uv_condition", isHighUVCondition);
                    
                    if (isHighUVCondition) {
                        hasHighUV = true;
                    }
                    
                    forecastArray.add(entryObj);
                }
                
                weatherInfo.add("forecast_entries", forecastArray);
                weatherInfo.addProperty("has_high_uv", hasHighUV);
                weatherInfo.addProperty("uv_determination_method", "Based on clear/sunny conditions with low cloudiness (<30%)");
                
                // Step 2: If high UV forecast, search for sunscreen at Costco and select lowest price
                JsonObject costcoInfo = new JsonObject();
                if (hasHighUV) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult sunscreenResults = costco.searchProducts("sunscreen");
                    
                    if (sunscreenResults.products != null && !sunscreenResults.products.isEmpty()) {
                        // Find the cheapest sunscreen
                        costco_com.ProductInfo cheapestSunscreen = null;
                        double lowestPrice = Double.MAX_VALUE;
                        
                        JsonArray sunscreensArray = new JsonArray();
                        for (costco_com.ProductInfo product : sunscreenResults.products) {
                            JsonObject sunscreenObj = new JsonObject();
                            sunscreenObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                sunscreenObj.addProperty("price", product.productPrice.amount);
                                sunscreenObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount < lowestPrice) {
                                    lowestPrice = product.productPrice.amount;
                                    cheapestSunscreen = product;
                                }
                            }
                            sunscreensArray.add(sunscreenObj);
                        }
                        
                        costcoInfo.add("available_sunscreens", sunscreensArray);
                        costcoInfo.addProperty("sunscreens_found", sunscreenResults.products.size());
                        
                        if (cheapestSunscreen != null) {
                            JsonObject selectedSunscreen = new JsonObject();
                            selectedSunscreen.addProperty("product_name", cheapestSunscreen.productName);
                            selectedSunscreen.addProperty("price", cheapestSunscreen.productPrice.amount);
                            selectedSunscreen.addProperty("currency", cheapestSunscreen.productPrice.currency);
                            selectedSunscreen.addProperty("selection_reason", "Lowest price sunscreen found");
                            costcoInfo.add("selected_sunscreen", selectedSunscreen);
                        }
                    } else {
                        costcoInfo.addProperty("sunscreens_found", 0);
                        costcoInfo.addProperty("message", "No sunscreens found at Costco");
                        if (sunscreenResults.error != null) {
                            costcoInfo.addProperty("error", sunscreenResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "No high UV conditions forecast, skipping sunscreen search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find top 3 Spotify tracks about summer
                Spotify spotify = new Spotify();
                JsonObject spotifyInfo = new JsonObject();
                
                try {
                    Spotify.SpotifySearchResult searchResult = spotify.searchItems("summer", "track", "US", 10, 0, null);
                    
                    if (searchResult.tracks != null && !searchResult.tracks.isEmpty()) {
                        // Get top 3 tracks (assuming they're already sorted by relevance)
                        List<Spotify.SpotifyTrack> topTracks = searchResult.tracks.subList(0, Math.min(3, searchResult.tracks.size()));
                        
                        JsonArray tracksArray = new JsonArray();
                        JsonArray booksSearchResults = new JsonArray();
                        
                        for (Spotify.SpotifyTrack track : topTracks) {
                            JsonObject trackObj = new JsonObject();
                            trackObj.addProperty("name", track.name);
                            trackObj.addProperty("artists", String.join(", ", track.artistNames));
                            trackObj.addProperty("popularity", track.popularity);
                            trackObj.addProperty("uri", track.uri);
                            tracksArray.add(trackObj);
                            
                            // Step 4: For each track, search for books about skin care and pick shortest title
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> skinCareBooks = openLibrary.search("skin care", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (skinCareBooks != null && !skinCareBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo shortestTitleBook = null;
                                    int shortestLength = Integer.MAX_VALUE;
                                    
                                    for (OpenLibrary.BookInfo book : skinCareBooks) {
                                        JsonObject bookObj = new JsonObject();
                                        bookObj.addProperty("title", book.title);
                                        int titleLength = book.title.length();
                                        bookObj.addProperty("title_length", titleLength);
                                        booksArray.add(bookObj);
                                        
                                        if (titleLength < shortestLength) {
                                            shortestLength = titleLength;
                                            shortestTitleBook = book;
                                        }
                                    }
                                    
                                    trackBooksInfo.add("available_books", booksArray);
                                    trackBooksInfo.addProperty("books_found", skinCareBooks.size());
                                    
                                    if (shortestTitleBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", shortestTitleBook.title);
                                        selectedBook.addProperty("title_length", shortestTitleBook.title.length());
                                        selectedBook.addProperty("selection_reason", "Book with shortest title about skin care");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about skin care found");
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
                        spotifyInfo.addProperty("message", "No tracks about summer found on Spotify");
                        if (searchResult.errorMessage != null) {
                            spotifyInfo.addProperty("error", searchResult.errorMessage);
                        }
                    }
                } catch (RuntimeException e) {
                    spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
                }
                
                result.add("spotify_and_books_search", spotifyInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Los Angeles, CA");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        
        result.add("weather_info", weatherInfo);
        result.addProperty("task_summary", "Check Los Angeles forecast for Aug 13, 2025. If high UV (clear/sunny <30% clouds), find lowest price Costco sunscreen and top 3 summer tracks with shortest skin care books.");
        result.addProperty("target_date", "August 13, 2025");
        result.addProperty("location", "Los Angeles, CA");
        
        return result;
    }
}
