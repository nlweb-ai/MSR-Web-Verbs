import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0076 {
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
        
        // Step 1: Check current weather in Chicago, IL for August 10, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get Chicago, IL location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Chicago, IL");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData chicagoLocation = locations.get(0);
                double lat = chicagoLocation.getLatitude();
                double lon = chicagoLocation.getLongitude();
                
                // Get current weather for Chicago, IL
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
                weatherInfo.addProperty("target_date", "August 10, 2025");
                
                // Check if wind speed is above 20 mph
                double windSpeed = currentWeather.getWindSpeed();
                boolean isAbove20MphWind = windSpeed > 20.0;
                weatherInfo.addProperty("above_20_mph_wind", isAbove20MphWind);
                
                // Step 2: If wind above 20 mph, search for windbreakers at Costco and select highest price
                JsonObject costcoInfo = new JsonObject();
                if (isAbove20MphWind) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult windreakerResults = costco.searchProducts("windbreaker");
                    
                    if (windreakerResults.products != null && !windreakerResults.products.isEmpty()) {
                        // Find the most expensive windbreaker
                        costco_com.ProductInfo mostExpensiveWindbreaker = null;
                        double highestPrice = Double.MIN_VALUE;
                        
                        JsonArray windbreakersArray = new JsonArray();
                        for (costco_com.ProductInfo product : windreakerResults.products) {
                            JsonObject windreakerObj = new JsonObject();
                            windreakerObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                windreakerObj.addProperty("price", product.productPrice.amount);
                                windreakerObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount > highestPrice) {
                                    highestPrice = product.productPrice.amount;
                                    mostExpensiveWindbreaker = product;
                                }
                            }
                            windbreakersArray.add(windreakerObj);
                        }
                        
                        costcoInfo.add("available_windbreakers", windbreakersArray);
                        costcoInfo.addProperty("windbreakers_found", windreakerResults.products.size());
                        
                        if (mostExpensiveWindbreaker != null) {
                            JsonObject selectedWindbreaker = new JsonObject();
                            selectedWindbreaker.addProperty("product_name", mostExpensiveWindbreaker.productName);
                            selectedWindbreaker.addProperty("price", mostExpensiveWindbreaker.productPrice.amount);
                            selectedWindbreaker.addProperty("currency", mostExpensiveWindbreaker.productPrice.currency);
                            selectedWindbreaker.addProperty("selection_reason", "Highest price windbreaker found");
                            costcoInfo.add("selected_windbreaker", selectedWindbreaker);
                        }
                    } else {
                        costcoInfo.addProperty("windbreakers_found", 0);
                        costcoInfo.addProperty("message", "No windbreakers found at Costco");
                        if (windreakerResults.error != null) {
                            costcoInfo.addProperty("error", windreakerResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "Wind speed not above 20 mph, skipping windbreaker search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find top 2 Spotify tracks about wind
                Spotify spotify = new Spotify();
                JsonObject spotifyInfo = new JsonObject();
                
                try {
                    Spotify.SpotifySearchResult searchResult = spotify.searchItems("wind", "track", "US", 10, 0, null);
                    
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
                            
                            // Step 4: For each track, search for books about weather and pick first alphabetically
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> weatherBooks = openLibrary.search("weather", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (weatherBooks != null && !weatherBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo firstAlphabeticalBook = null;
                                    String earliestTitle = null;
                                    
                                    for (OpenLibrary.BookInfo book : weatherBooks) {
                                        JsonObject bookObj = new JsonObject();
                                        bookObj.addProperty("title", book.title);
                                        booksArray.add(bookObj);
                                        
                                        if (earliestTitle == null || book.title.compareToIgnoreCase(earliestTitle) < 0) {
                                            earliestTitle = book.title;
                                            firstAlphabeticalBook = book;
                                        }
                                    }
                                    
                                    trackBooksInfo.add("available_books", booksArray);
                                    trackBooksInfo.addProperty("books_found", weatherBooks.size());
                                    
                                    if (firstAlphabeticalBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", firstAlphabeticalBook.title);
                                        selectedBook.addProperty("selection_reason", "Book with earliest alphabetical title about weather");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about weather found");
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
                        spotifyInfo.addProperty("message", "No tracks about wind found on Spotify");
                        if (searchResult.errorMessage != null) {
                            spotifyInfo.addProperty("error", searchResult.errorMessage);
                        }
                    }
                } catch (RuntimeException e) {
                    spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
                }
                
                result.add("spotify_and_books_search", spotifyInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Chicago, IL");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        
        result.add("weather_info", weatherInfo);
        result.addProperty("task_summary", "Check Chicago weather for Aug 10, 2025. If wind above 20 mph, find highest price Costco windbreaker and top 2 wind tracks with first alphabetical weather books.");
        result.addProperty("target_date", "August 10, 2025");
        result.addProperty("location", "Chicago, IL");
        
        return result;
    }
}
