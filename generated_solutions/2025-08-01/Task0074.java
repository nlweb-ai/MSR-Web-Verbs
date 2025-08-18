import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0074 {
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
        
        // Step 1: Get weather forecast for Denver, CO on August 20, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get Denver, CO location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Denver, CO");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData denverLocation = locations.get(0);
                double lat = denverLocation.getLatitude();
                double lon = denverLocation.getLongitude();
                
                // Get weather forecast for Denver, CO
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                
                weatherInfo.addProperty("city", forecast.getCityName());
                weatherInfo.addProperty("country", forecast.getCountry());
                weatherInfo.addProperty("latitude", forecast.getLatitude());
                weatherInfo.addProperty("longitude", forecast.getLongitude());
                weatherInfo.addProperty("target_date", "August 20, 2025");
                
                // Check forecast for thunderstorms on August 20, 2025
                boolean thunderstormsPredicted = false;
                JsonArray forecastArray = new JsonArray();
                
                if (forecast.getForecasts() != null) {
                    for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                        JsonObject forecastEntry = new JsonObject();
                        forecastEntry.addProperty("date_time", entry.getDateTime().toString());
                        forecastEntry.addProperty("condition", entry.getCondition());
                        forecastEntry.addProperty("description", entry.getDescription());
                        forecastEntry.addProperty("temperature", entry.getTemperature());
                        forecastEntry.addProperty("humidity", entry.getHumidity());
                        forecastEntry.addProperty("wind_speed", entry.getWindSpeed());
                        
                        // Check if thunderstorms are predicted
                        String condition = entry.getCondition().toLowerCase();
                        String description = entry.getDescription().toLowerCase();
                        if (condition.contains("thunder") || description.contains("thunder") || 
                            condition.contains("storm") || description.contains("storm") ||
                            condition.contains("lightning") || description.contains("lightning")) {
                            thunderstormsPredicted = true;
                            forecastEntry.addProperty("has_thunderstorms", true);
                        } else {
                            forecastEntry.addProperty("has_thunderstorms", false);
                        }
                        
                        forecastArray.add(forecastEntry);
                    }
                }
                
                weatherInfo.add("forecast_entries", forecastArray);
                weatherInfo.addProperty("thunderstorms_predicted", thunderstormsPredicted);
                
                // Step 2: If thunderstorms predicted, search for surge protectors at Costco and select cheapest
                JsonObject costcoInfo = new JsonObject();
                if (thunderstormsPredicted) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult surgeResults = costco.searchProducts("surge protector");
                    
                    if (surgeResults.products != null && !surgeResults.products.isEmpty()) {
                        // Find the cheapest surge protector
                        costco_com.ProductInfo cheapestSurgeProtector = null;
                        double lowestPrice = Double.MAX_VALUE;
                        
                        JsonArray surgeProtectorsArray = new JsonArray();
                        for (costco_com.ProductInfo product : surgeResults.products) {
                            JsonObject surgeObj = new JsonObject();
                            surgeObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                surgeObj.addProperty("price", product.productPrice.amount);
                                surgeObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount < lowestPrice) {
                                    lowestPrice = product.productPrice.amount;
                                    cheapestSurgeProtector = product;
                                }
                            }
                            surgeProtectorsArray.add(surgeObj);
                        }
                        
                        costcoInfo.add("available_surge_protectors", surgeProtectorsArray);
                        costcoInfo.addProperty("surge_protectors_found", surgeResults.products.size());
                        
                        if (cheapestSurgeProtector != null) {
                            JsonObject selectedSurgeProtector = new JsonObject();
                            selectedSurgeProtector.addProperty("product_name", cheapestSurgeProtector.productName);
                            selectedSurgeProtector.addProperty("price", cheapestSurgeProtector.productPrice.amount);
                            selectedSurgeProtector.addProperty("currency", cheapestSurgeProtector.productPrice.currency);
                            selectedSurgeProtector.addProperty("selection_reason", "Cheapest surge protector found");
                            costcoInfo.add("selected_surge_protector", selectedSurgeProtector);
                        }
                    } else {
                        costcoInfo.addProperty("surge_protectors_found", 0);
                        costcoInfo.addProperty("message", "No surge protectors found at Costco");
                        if (surgeResults.error != null) {
                            costcoInfo.addProperty("error", surgeResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "No thunderstorms predicted, skipping surge protector search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find top 2 Spotify tracks about storms
                Spotify spotify = new Spotify();
                JsonObject spotifyInfo = new JsonObject();
                
                try {
                    Spotify.SpotifySearchResult searchResult = spotify.searchItems("storms", "track", "US", 10, 0, null);
                    
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
                            
                            // Step 4: For each track, search for books about electricity and pick longest title
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> electricityBooks = openLibrary.search("electricity", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (electricityBooks != null && !electricityBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo longestTitleBook = null;
                                    int longestLength = 0;
                                    
                                    for (OpenLibrary.BookInfo book : electricityBooks) {
                                        JsonObject bookObj = new JsonObject();
                                        bookObj.addProperty("title", book.title);
                                        bookObj.addProperty("title_length", book.title.length());
                                        booksArray.add(bookObj);
                                        
                                        if (book.title.length() > longestLength) {
                                            longestLength = book.title.length();
                                            longestTitleBook = book;
                                        }
                                    }
                                    
                                    trackBooksInfo.add("available_books", booksArray);
                                    trackBooksInfo.addProperty("books_found", electricityBooks.size());
                                    
                                    if (longestTitleBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", longestTitleBook.title);
                                        selectedBook.addProperty("title_length", longestTitleBook.title.length());
                                        selectedBook.addProperty("selection_reason", "Book with longest title about electricity");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about electricity found");
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
                        spotifyInfo.addProperty("message", "No tracks about storms found on Spotify");
                        if (searchResult.errorMessage != null) {
                            spotifyInfo.addProperty("error", searchResult.errorMessage);
                        }
                    }
                } catch (RuntimeException e) {
                    spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
                }
                
                result.add("spotify_and_books_search", spotifyInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Denver, CO");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather forecast: " + e.getMessage());
        }
        
        result.add("weather_forecast", weatherInfo);
        result.addProperty("task_summary", "Check Denver weather forecast for Aug 20, 2025. If thunderstorms predicted, find cheapest Costco surge protector and top 2 storm tracks with longest electricity books.");
        result.addProperty("target_date", "August 20, 2025");
        result.addProperty("location", "Denver, CO");
        
        return result;
    }
}
