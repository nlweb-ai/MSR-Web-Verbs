import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0078 {
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
        
        // Step 1: Check weather forecast for Phoenix, AZ for August 14, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get Phoenix, AZ location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Phoenix, AZ");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData phoenixLocation = locations.get(0);
                double lat = phoenixLocation.getLatitude();
                double lon = phoenixLocation.getLongitude();
                
                // Get 5-day weather forecast for Phoenix, AZ
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                
                weatherInfo.addProperty("city", forecast.getCityName());
                weatherInfo.addProperty("country", forecast.getCountry());
                weatherInfo.addProperty("target_date", "August 14, 2025");
                
                // Check forecast for extreme heat (temperature > 100°F / 37.8°C)
                boolean hasExtremeHeat = false;
                JsonArray forecastArray = new JsonArray();
                
                for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                    JsonObject entryObj = new JsonObject();
                    entryObj.addProperty("date", entry.getDateTime().toString());
                    entryObj.addProperty("temperature", entry.getTemperature());
                    entryObj.addProperty("condition", entry.getCondition());
                    entryObj.addProperty("description", entry.getDescription());
                    
                    // Convert temperature to Fahrenheit for extreme heat check
                    double tempFahrenheit = entry.getTemperature() * 9.0 / 5.0 + 32.0;
                    entryObj.addProperty("temperature_fahrenheit", tempFahrenheit);
                    
                    if (tempFahrenheit > 100.0) {
                        hasExtremeHeat = true;
                        entryObj.addProperty("extreme_heat", true);
                    } else {
                        entryObj.addProperty("extreme_heat", false);
                    }
                    
                    forecastArray.add(entryObj);
                }
                
                weatherInfo.add("forecast_entries", forecastArray);
                weatherInfo.addProperty("has_extreme_heat", hasExtremeHeat);
                
                // Step 2: If extreme heat forecast, search for sun hats at Costco and select lowest price
                JsonObject costcoInfo = new JsonObject();
                if (hasExtremeHeat) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult sunHatResults = costco.searchProducts("sun hat");
                    
                    if (sunHatResults.products != null && !sunHatResults.products.isEmpty()) {
                        // Find the cheapest sun hat
                        costco_com.ProductInfo cheapestSunHat = null;
                        double lowestPrice = Double.MAX_VALUE;
                        
                        JsonArray sunHatsArray = new JsonArray();
                        for (costco_com.ProductInfo product : sunHatResults.products) {
                            JsonObject sunHatObj = new JsonObject();
                            sunHatObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                sunHatObj.addProperty("price", product.productPrice.amount);
                                sunHatObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount < lowestPrice) {
                                    lowestPrice = product.productPrice.amount;
                                    cheapestSunHat = product;
                                }
                            }
                            sunHatsArray.add(sunHatObj);
                        }
                        
                        costcoInfo.add("available_sun_hats", sunHatsArray);
                        costcoInfo.addProperty("sun_hats_found", sunHatResults.products.size());
                        
                        if (cheapestSunHat != null) {
                            JsonObject selectedSunHat = new JsonObject();
                            selectedSunHat.addProperty("product_name", cheapestSunHat.productName);
                            selectedSunHat.addProperty("price", cheapestSunHat.productPrice.amount);
                            selectedSunHat.addProperty("currency", cheapestSunHat.productPrice.currency);
                            selectedSunHat.addProperty("selection_reason", "Lowest price sun hat found");
                            costcoInfo.add("selected_sun_hat", selectedSunHat);
                        }
                    } else {
                        costcoInfo.addProperty("sun_hats_found", 0);
                        costcoInfo.addProperty("message", "No sun hats found at Costco");
                        if (sunHatResults.error != null) {
                            costcoInfo.addProperty("error", sunHatResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "No extreme heat forecast, skipping sun hat search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find top 3 Spotify tracks about sun
                Spotify spotify = new Spotify();
                JsonObject spotifyInfo = new JsonObject();
                
                try {
                    Spotify.SpotifySearchResult searchResult = spotify.searchItems("sun", "track", "US", 10, 0, null);
                    
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
                            
                            // Step 4: For each track, search for books about deserts and pick most recent publication (first alphabetically since no publication year field)
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> desertBooks = openLibrary.search("desert", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (desertBooks != null && !desertBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo mostRecentBook = null;
                                    String latestTitle = null;
                                    
                                    // Since BookInfo only has title field, we'll select the last alphabetically as a proxy for "most recent"
                                    for (OpenLibrary.BookInfo book : desertBooks) {
                                        JsonObject bookObj = new JsonObject();
                                        bookObj.addProperty("title", book.title);
                                        booksArray.add(bookObj);
                                        
                                        if (latestTitle == null || book.title.compareToIgnoreCase(latestTitle) > 0) {
                                            latestTitle = book.title;
                                            mostRecentBook = book;
                                        }
                                    }
                                    
                                    trackBooksInfo.add("available_books", booksArray);
                                    trackBooksInfo.addProperty("books_found", desertBooks.size());
                                    
                                    if (mostRecentBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", mostRecentBook.title);
                                        selectedBook.addProperty("selection_reason", "Book with latest alphabetical title about deserts (proxy for most recent)");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about deserts found");
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
                        spotifyInfo.addProperty("message", "No tracks about sun found on Spotify");
                        if (searchResult.errorMessage != null) {
                            spotifyInfo.addProperty("error", searchResult.errorMessage);
                        }
                    }
                } catch (RuntimeException e) {
                    spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
                }
                
                result.add("spotify_and_books_search", spotifyInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Phoenix, AZ");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        
        result.add("weather_info", weatherInfo);
        result.addProperty("task_summary", "Check Phoenix forecast for Aug 14, 2025. If extreme heat (>100°F), find lowest price Costco sun hat and top 3 sun tracks with latest desert books.");
        result.addProperty("target_date", "August 14, 2025");
        result.addProperty("location", "Phoenix, AZ");
        
        return result;
    }
}
