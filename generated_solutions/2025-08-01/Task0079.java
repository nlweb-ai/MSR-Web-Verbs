import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0079 {
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
        
        // Step 1: Check current weather and air quality in New York, NY for August 11, 2025
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get New York, NY location coordinates
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("New York, NY");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData nyLocation = locations.get(0);
                double lat = nyLocation.getLatitude();
                double lon = nyLocation.getLongitude();
                
                // Get current weather for New York, NY
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
                weatherInfo.addProperty("target_date", "August 11, 2025");
                
                // Get current air pollution data
                OpenWeather.AirPollutionData airPollution = weather.getCurrentAirPollution(lat, lon);
                JsonObject airQualityInfo = new JsonObject();
                
                boolean isPoorAirQuality = false;
                if (!airPollution.getPollutionEntries().isEmpty()) {
                    OpenWeather.PollutionEntry currentPollution = airPollution.getPollutionEntries().get(0);
                    int aqi = currentPollution.getAqi();
                    
                    airQualityInfo.addProperty("aqi", aqi);
                    airQualityInfo.addProperty("date_time", currentPollution.getDateTime().toString());
                    airQualityInfo.addProperty("co", currentPollution.getCo());
                    airQualityInfo.addProperty("no2", currentPollution.getNo2());
                    airQualityInfo.addProperty("o3", currentPollution.getO3());
                    airQualityInfo.addProperty("pm2_5", currentPollution.getPm2_5());
                    airQualityInfo.addProperty("pm10", currentPollution.getPm10());
                    
                    // AQI scale: 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
                    isPoorAirQuality = aqi >= 4;
                    airQualityInfo.addProperty("is_poor_air_quality", isPoorAirQuality);
                    
                    String aqiLevel;
                    switch(aqi) {
                        case 1: aqiLevel = "Good"; break;
                        case 2: aqiLevel = "Fair"; break;
                        case 3: aqiLevel = "Moderate"; break;
                        case 4: aqiLevel = "Poor"; break;
                        case 5: aqiLevel = "Very Poor"; break;
                        default: aqiLevel = "Unknown"; break;
                    }
                    airQualityInfo.addProperty("aqi_level", aqiLevel);
                } else {
                    airQualityInfo.addProperty("error", "No air pollution data available");
                }
                
                weatherInfo.add("air_quality", airQualityInfo);
                
                // Step 2: If air quality is poor, search for air purifiers at Costco and select highest price
                JsonObject costcoInfo = new JsonObject();
                if (isPoorAirQuality) {
                    costco_com costco = new costco_com(context);
                    costco_com.ProductListResult airPurifierResults = costco.searchProducts("air purifier");
                    
                    if (airPurifierResults.products != null && !airPurifierResults.products.isEmpty()) {
                        // Find the most expensive air purifier
                        costco_com.ProductInfo mostExpensiveAirPurifier = null;
                        double highestPrice = Double.MIN_VALUE;
                        
                        JsonArray airPurifiersArray = new JsonArray();
                        for (costco_com.ProductInfo product : airPurifierResults.products) {
                            JsonObject airPurifierObj = new JsonObject();
                            airPurifierObj.addProperty("product_name", product.productName);
                            if (product.productPrice != null) {
                                airPurifierObj.addProperty("price", product.productPrice.amount);
                                airPurifierObj.addProperty("currency", product.productPrice.currency);
                                
                                if (product.productPrice.amount > highestPrice) {
                                    highestPrice = product.productPrice.amount;
                                    mostExpensiveAirPurifier = product;
                                }
                            }
                            airPurifiersArray.add(airPurifierObj);
                        }
                        
                        costcoInfo.add("available_air_purifiers", airPurifiersArray);
                        costcoInfo.addProperty("air_purifiers_found", airPurifierResults.products.size());
                        
                        if (mostExpensiveAirPurifier != null) {
                            JsonObject selectedAirPurifier = new JsonObject();
                            selectedAirPurifier.addProperty("product_name", mostExpensiveAirPurifier.productName);
                            selectedAirPurifier.addProperty("price", mostExpensiveAirPurifier.productPrice.amount);
                            selectedAirPurifier.addProperty("currency", mostExpensiveAirPurifier.productPrice.currency);
                            selectedAirPurifier.addProperty("selection_reason", "Highest price air purifier found");
                            costcoInfo.add("selected_air_purifier", selectedAirPurifier);
                        }
                    } else {
                        costcoInfo.addProperty("air_purifiers_found", 0);
                        costcoInfo.addProperty("message", "No air purifiers found at Costco");
                        if (airPurifierResults.error != null) {
                            costcoInfo.addProperty("error", airPurifierResults.error);
                        }
                    }
                } else {
                    costcoInfo.addProperty("search_performed", false);
                    costcoInfo.addProperty("reason", "Air quality not poor (AQI < 4), skipping air purifier search");
                }
                
                result.add("costco_search", costcoInfo);
                
                // Step 3: Find top 2 Spotify tracks about air
                Spotify spotify = new Spotify();
                JsonObject spotifyInfo = new JsonObject();
                
                try {
                    Spotify.SpotifySearchResult searchResult = spotify.searchItems("air", "track", "US", 10, 0, null);
                    
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
                            
                            // Step 4: For each track, search for books about pollution and pick longest title
                            OpenLibrary openLibrary = new OpenLibrary();
                            JsonObject trackBooksInfo = new JsonObject();
                            trackBooksInfo.addProperty("track_name", track.name);
                            trackBooksInfo.addProperty("track_artists", String.join(", ", track.artistNames));
                            
                            try {
                                List<OpenLibrary.BookInfo> pollutionBooks = openLibrary.search("pollution", "title,author_name,first_publish_year", "new", "en", 20, 1);
                                
                                if (pollutionBooks != null && !pollutionBooks.isEmpty()) {
                                    JsonArray booksArray = new JsonArray();
                                    OpenLibrary.BookInfo longestTitleBook = null;
                                    int longestLength = 0;
                                    
                                    for (OpenLibrary.BookInfo book : pollutionBooks) {
                                        JsonObject bookObj = new JsonObject();
                                        bookObj.addProperty("title", book.title);
                                        int titleLength = book.title.length();
                                        bookObj.addProperty("title_length", titleLength);
                                        booksArray.add(bookObj);
                                        
                                        if (titleLength > longestLength) {
                                            longestLength = titleLength;
                                            longestTitleBook = book;
                                        }
                                    }
                                    
                                    trackBooksInfo.add("available_books", booksArray);
                                    trackBooksInfo.addProperty("books_found", pollutionBooks.size());
                                    
                                    if (longestTitleBook != null) {
                                        JsonObject selectedBook = new JsonObject();
                                        selectedBook.addProperty("title", longestTitleBook.title);
                                        selectedBook.addProperty("title_length", longestTitleBook.title.length());
                                        selectedBook.addProperty("selection_reason", "Book with longest title about pollution");
                                        trackBooksInfo.add("selected_book", selectedBook);
                                    }
                                } else {
                                    trackBooksInfo.addProperty("books_found", 0);
                                    trackBooksInfo.addProperty("message", "No books about pollution found");
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
                        spotifyInfo.addProperty("message", "No tracks about air found on Spotify");
                        if (searchResult.errorMessage != null) {
                            spotifyInfo.addProperty("error", searchResult.errorMessage);
                        }
                    }
                } catch (RuntimeException e) {
                    spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
                }
                
                result.add("spotify_and_books_search", spotifyInfo);
                
            } else {
                weatherInfo.addProperty("error", "Could not find location data for New York, NY");
            }
        } catch (java.io.IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        
        result.add("weather_info", weatherInfo);
        result.addProperty("task_summary", "Check New York weather for Aug 11, 2025. If air quality poor (AQI >= 4), find highest price Costco air purifier and top 2 air tracks with longest pollution books.");
        result.addProperty("target_date", "August 11, 2025");
        result.addProperty("location", "New York, NY");
        
        return result;
    }
}
