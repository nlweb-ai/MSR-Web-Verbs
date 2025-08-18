import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0072 {
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
        
        // Step 1: Check weather forecast for Seattle, WA on August 12, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get Seattle, WA location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Seattle, WA");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData seattleLocation = locations.get(0);
                double lat = seattleLocation.getLatitude();
                double lon = seattleLocation.getLongitude();
                
                // Get weather forecast for Seattle, WA
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                
                weatherInfo.addProperty("city", forecast.getCityName());
                weatherInfo.addProperty("country", forecast.getCountry());
                weatherInfo.addProperty("latitude", forecast.getLatitude());
                weatherInfo.addProperty("longitude", forecast.getLongitude());
                weatherInfo.addProperty("target_date", "August 12, 2025");
                
                // Check forecast for rain on August 12, 2025
                boolean rainPredicted = false;
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
                        
                        // Check if rain is predicted (looking for rain keywords)
                        String condition = entry.getCondition().toLowerCase();
                        String description = entry.getDescription().toLowerCase();
                        if (condition.contains("rain") || description.contains("rain") || 
                            condition.contains("shower") || description.contains("shower") ||
                            condition.contains("drizzle") || description.contains("drizzle")) {
                            rainPredicted = true;
                            forecastEntry.addProperty("has_rain", true);
                        } else {
                            forecastEntry.addProperty("has_rain", false);
                        }
                        
                        forecastArray.add(forecastEntry);
                    }
                }
                
                weatherInfo.add("forecast_entries", forecastArray);
                weatherInfo.addProperty("rain_predicted", rainPredicted);
                
                // Step 2: If rain predicted, search for raincoats at Costco and select most expensive
                JsonObject costcoInfo = new JsonObject();
                if (rainPredicted) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult raincoatResults = costco.searchProducts("raincoat");
                    
                    if (raincoatResults.products != null && !raincoatResults.products.isEmpty()) {
                        // Find the most expensive raincoat
                        costco_com.ProductInfo mostExpensiveRaincoat = null;
                        double highestPrice = 0.0;
                        
                        JsonArray raincoatsArray = new JsonArray();
                        for (costco_com.ProductInfo product : raincoatResults.products) {
                            JsonObject raincoatObj = new JsonObject();
                            raincoatObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                raincoatObj.addProperty("price", product.productPrice.amount);
                                raincoatObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount > highestPrice) {
                                    highestPrice = product.productPrice.amount;
                                    mostExpensiveRaincoat = product;
                                }
                            }
                            raincoatsArray.add(raincoatObj);
                        }
                        
                        costcoInfo.add("available_raincoats", raincoatsArray);
                        costcoInfo.addProperty("raincoats_found", raincoatResults.products.size());
                        
                        if (mostExpensiveRaincoat != null) {
                            JsonObject selectedRaincoat = new JsonObject();
                            selectedRaincoat.addProperty("product_name", mostExpensiveRaincoat.productName);
                            selectedRaincoat.addProperty("price", mostExpensiveRaincoat.productPrice.amount);
                            selectedRaincoat.addProperty("currency", mostExpensiveRaincoat.productPrice.currency);
                            selectedRaincoat.addProperty("selection_reason", "Most expensive raincoat found");
                            costcoInfo.add("selected_raincoat", selectedRaincoat);
                        }
                    } else {
                        costcoInfo.addProperty("raincoats_found", 0);
                        costcoInfo.addProperty("message", "No raincoats found at Costco");
                        if (raincoatResults.error != null) {
                            costcoInfo.addProperty("error", raincoatResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "No rain predicted, skipping raincoat search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find top 2 Spotify tracks about rain
                Spotify spotify = new Spotify();
                JsonObject spotifyInfo = new JsonObject();
                
                try {
                    Spotify.SpotifySearchResult searchResult = spotify.searchItems("rain", "track", "US", 10, 0, null);
                    
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
                            
                            // Step 4: For each track, search for books about rain and pick latest publication year
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> rainBooks = openLibrary.search("rain", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (rainBooks != null && !rainBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo latestBook = null;
                                    String latestTitle = "";
                                    
                                    // Note: Since OpenLibrary.BookInfo only has title, we'll select based on title containing publication info
                                    // In a real scenario, we'd need publication year data
                                    for (OpenLibrary.BookInfo book : rainBooks) {
                                        JsonObject bookObj = new JsonObject();
                                        bookObj.addProperty("title", book.title);
                                        booksArray.add(bookObj);
                                        
                                        // Select first book as "latest" (since we sorted by "new")
                                        if (latestBook == null) {
                                            latestBook = book;
                                            latestTitle = book.title;
                                        }
                                    }
                                    
                                    trackBooksInfo.add("available_books", booksArray);
                                    trackBooksInfo.addProperty("books_found", rainBooks.size());
                                    
                                    if (latestBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", latestTitle);
                                        selectedBook.addProperty("selection_reason", "Latest publication (first in 'new' sorted results)");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about rain found");
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
                        spotifyInfo.addProperty("message", "No tracks about rain found on Spotify");
                        if (searchResult.errorMessage != null) {
                            spotifyInfo.addProperty("error", searchResult.errorMessage);
                        }
                    }
                } catch (RuntimeException e) {
                    spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
                }
                
                result.add("spotify_and_books_search", spotifyInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Seattle, WA");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather forecast: " + e.getMessage());
        }
        
        result.add("weather_forecast", weatherInfo);
        result.addProperty("task_summary", "Check Seattle weather forecast for Aug 12, 2025. If rain predicted, find most expensive Costco raincoat and top 2 rain tracks with latest rain books.");
        result.addProperty("target_date", "August 12, 2025");
        result.addProperty("location", "Seattle, WA");
        
        return result;
    }
}
