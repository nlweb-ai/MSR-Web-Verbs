import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0077 {
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
        
        // Step 1: Check current weather in Boston, MA for August 12, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get Boston, MA location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Boston, MA");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData bostonLocation = locations.get(0);
                double lat = bostonLocation.getLatitude();
                double lon = bostonLocation.getLongitude();
                
                // Get current weather for Boston, MA
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
                weatherInfo.addProperty("target_date", "August 12, 2025");
                
                // Check if temperature is below 60°F
                // Temperature is in Celsius, convert to Fahrenheit: F = C * 9/5 + 32
                double tempCelsius = currentWeather.getTemperature();
                double tempFahrenheit = tempCelsius * 9.0 / 5.0 + 32.0;
                boolean isBelow60F = tempFahrenheit < 60.0;
                weatherInfo.addProperty("temperature_fahrenheit", tempFahrenheit);
                weatherInfo.addProperty("below_60_fahrenheit", isBelow60F);
                
                // Step 2: If temperature below 60°F, search for heaters at Costco and select cheapest
                JsonObject costcoInfo = new JsonObject();
                if (isBelow60F) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult heaterResults = costco.searchProducts("heater");
                    
                    if (heaterResults.products != null && !heaterResults.products.isEmpty()) {
                        // Find the cheapest heater
                        costco_com.ProductInfo cheapestHeater = null;
                        double lowestPrice = Double.MAX_VALUE;
                        
                        JsonArray heatersArray = new JsonArray();
                        for (costco_com.ProductInfo product : heaterResults.products) {
                            JsonObject heaterObj = new JsonObject();
                            heaterObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                heaterObj.addProperty("price", product.productPrice.amount);
                                heaterObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount < lowestPrice) {
                                    lowestPrice = product.productPrice.amount;
                                    cheapestHeater = product;
                                }
                            }
                            heatersArray.add(heaterObj);
                        }
                        
                        costcoInfo.add("available_heaters", heatersArray);
                        costcoInfo.addProperty("heaters_found", heaterResults.products.size());
                        
                        if (cheapestHeater != null) {
                            JsonObject selectedHeater = new JsonObject();
                            selectedHeater.addProperty("product_name", cheapestHeater.productName);
                            selectedHeater.addProperty("price", cheapestHeater.productPrice.amount);
                            selectedHeater.addProperty("currency", cheapestHeater.productPrice.currency);
                            selectedHeater.addProperty("selection_reason", "Cheapest heater found");
                            costcoInfo.add("selected_heater", selectedHeater);
                        }
                    } else {
                        costcoInfo.addProperty("heaters_found", 0);
                        costcoInfo.addProperty("message", "No heaters found at Costco");
                        if (heaterResults.error != null) {
                            costcoInfo.addProperty("error", heaterResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "Temperature not below 60°F, skipping heater search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find top 2 Spotify tracks about winter
                Spotify spotify = new Spotify();
                JsonObject spotifyInfo = new JsonObject();
                
                try {
                    Spotify.SpotifySearchResult searchResult = spotify.searchItems("winter", "track", "US", 10, 0, null);
                    
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
                            
                            // Step 4: For each track, search for books about snow and pick shortest title
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> snowBooks = openLibrary.search("snow", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (snowBooks != null && !snowBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo shortestTitleBook = null;
                                    int shortestLength = Integer.MAX_VALUE;
                                    
                                    for (OpenLibrary.BookInfo book : snowBooks) {
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
                                    trackBooksInfo.addProperty("books_found", snowBooks.size());
                                    
                                    if (shortestTitleBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", shortestTitleBook.title);
                                        selectedBook.addProperty("title_length", shortestTitleBook.title.length());
                                        selectedBook.addProperty("selection_reason", "Book with shortest title about snow");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about snow found");
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
                        spotifyInfo.addProperty("message", "No tracks about winter found on Spotify");
                        if (searchResult.errorMessage != null) {
                            spotifyInfo.addProperty("error", searchResult.errorMessage);
                        }
                    }
                } catch (RuntimeException e) {
                    spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
                }
                
                result.add("spotify_and_books_search", spotifyInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Boston, MA");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        
        result.add("weather_info", weatherInfo);
        result.addProperty("task_summary", "Check Boston weather for Aug 12, 2025. If temperature below 60°F, find cheapest Costco heater and top 2 winter tracks with shortest snow books.");
        result.addProperty("target_date", "August 12, 2025");
        result.addProperty("location", "Boston, MA");
        
        return result;
    }
}
