import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0073 {
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
        
        // Step 1: Check current weather in Miami, FL for August 15, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get Miami, FL location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Miami, FL");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData miamiLocation = locations.get(0);
                double lat = miamiLocation.getLatitude();
                double lon = miamiLocation.getLongitude();
                
                // Get current weather for Miami, FL
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(lat, lon);
                
                weatherInfo.addProperty("city", currentWeather.getCityName());
                weatherInfo.addProperty("country", currentWeather.getCountry());
                weatherInfo.addProperty("date", currentWeather.getDate().toString());
                weatherInfo.addProperty("condition", currentWeather.getCondition());
                weatherInfo.addProperty("description", currentWeather.getDescription());
                weatherInfo.addProperty("temperature_celsius", currentWeather.getTemperature());
                
                // Convert Celsius to Fahrenheit (F = C * 9/5 + 32)
                double temperatureFahrenheit = currentWeather.getTemperature() * 9.0 / 5.0 + 32.0;
                weatherInfo.addProperty("temperature_fahrenheit", Math.round(temperatureFahrenheit * 100.0) / 100.0);
                
                weatherInfo.addProperty("feels_like", currentWeather.getFeelsLike());
                weatherInfo.addProperty("humidity", currentWeather.getHumidity());
                weatherInfo.addProperty("wind_speed", currentWeather.getWindSpeed());
                weatherInfo.addProperty("cloudiness", currentWeather.getCloudiness());
                weatherInfo.addProperty("target_date", "August 15, 2025");
                
                // Check if temperature is above 90°F
                boolean isAbove90F = temperatureFahrenheit > 90.0;
                weatherInfo.addProperty("above_90_fahrenheit", isAbove90F);
                
                // Step 2: If temperature above 90°F, search for air conditioners at Costco and select highest price
                JsonObject costcoInfo = new JsonObject();
                if (isAbove90F) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult acResults = costco.searchProducts("air conditioner");
                    
                    if (acResults.products != null && !acResults.products.isEmpty()) {
                        // Find the most expensive air conditioner
                        costco_com.ProductInfo mostExpensiveAC = null;
                        double highestPrice = 0.0;
                        
                        JsonArray acsArray = new JsonArray();
                        for (costco_com.ProductInfo product : acResults.products) {
                            JsonObject acObj = new JsonObject();
                            acObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                acObj.addProperty("price", product.productPrice.amount);
                                acObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount > highestPrice) {
                                    highestPrice = product.productPrice.amount;
                                    mostExpensiveAC = product;
                                }
                            }
                            acsArray.add(acObj);
                        }
                        
                        costcoInfo.add("available_air_conditioners", acsArray);
                        costcoInfo.addProperty("air_conditioners_found", acResults.products.size());
                        
                        if (mostExpensiveAC != null) {
                            JsonObject selectedAC = new JsonObject();
                            selectedAC.addProperty("product_name", mostExpensiveAC.productName);
                            selectedAC.addProperty("price", mostExpensiveAC.productPrice.amount);
                            selectedAC.addProperty("currency", mostExpensiveAC.productPrice.currency);
                            selectedAC.addProperty("selection_reason", "Most expensive air conditioner found");
                            costcoInfo.add("selected_air_conditioner", selectedAC);
                        }
                    } else {
                        costcoInfo.addProperty("air_conditioners_found", 0);
                        costcoInfo.addProperty("message", "No air conditioners found at Costco");
                        if (acResults.error != null) {
                            costcoInfo.addProperty("error", acResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "Temperature not above 90°F, skipping air conditioner search");
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
                            
                            // Step 4: For each track, search for books about heat and pick shortest title
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> heatBooks = openLibrary.search("heat", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (heatBooks != null && !heatBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo shortestTitleBook = null;
                                    int shortestLength = Integer.MAX_VALUE;
                                    
                                    for (OpenLibrary.BookInfo book : heatBooks) {
                                        JsonObject bookObj = new JsonObject();
                                        bookObj.addProperty("title", book.title);
                                        bookObj.addProperty("title_length", book.title.length());
                                        booksArray.add(bookObj);
                                        
                                        if (book.title.length() < shortestLength) {
                                            shortestLength = book.title.length();
                                            shortestTitleBook = book;
                                        }
                                    }
                                    
                                    trackBooksInfo.add("available_books", booksArray);
                                    trackBooksInfo.addProperty("books_found", heatBooks.size());
                                    
                                    if (shortestTitleBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", shortestTitleBook.title);
                                        selectedBook.addProperty("title_length", shortestTitleBook.title.length());
                                        selectedBook.addProperty("selection_reason", "Book with shortest title about heat");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about heat found");
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
                weatherInfo.addProperty("error", "Could not find location data for Miami, FL");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        
        result.add("weather_info", weatherInfo);
        result.addProperty("task_summary", "Check Miami weather for Aug 15, 2025. If temp above 90°F, find most expensive Costco AC and top 3 summer tracks with shortest heat books.");
        result.addProperty("target_date", "August 15, 2025");
        result.addProperty("location", "Miami, FL");
        
        return result;
    }
}
