import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0083 {
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
        
        // Step 1: Check weather forecast for San Francisco on August 20, 2025
        OpenWeather weather = new OpenWeather();
        String location = "San Francisco, CA";
        
        JsonObject weatherInfo = new JsonObject();
        try {
            // First get location coordinates for San Francisco
            java.util.List<OpenWeather.LocationData> locations = weather.getLocationsByName(location);
            if (locations.isEmpty()) {
                weatherInfo.addProperty("error", "Location not found: " + location);
                weatherInfo.addProperty("suitable_for_outdoor_dining", false);
            } else {
                OpenWeather.LocationData sfLocation = locations.get(0);
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(
                    sfLocation.getLatitude(), sfLocation.getLongitude());
                
                weatherInfo.addProperty("city", currentWeather.getCityName());
                weatherInfo.addProperty("country", currentWeather.getCountry());
                weatherInfo.addProperty("temperature", currentWeather.getTemperature());
                weatherInfo.addProperty("condition", currentWeather.getCondition());
                weatherInfo.addProperty("description", currentWeather.getDescription());
                weatherInfo.addProperty("humidity", currentWeather.getHumidity());
                
                // Determine if suitable for outdoor dining (>65°F and no rain)
                boolean suitableForOutdoor = currentWeather.getTemperature() > 65.0 && 
                                           !currentWeather.getCondition().toLowerCase().contains("rain");
                weatherInfo.addProperty("suitable_for_outdoor_dining", suitableForOutdoor);
            }
            
        } catch (IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to fetch weather: " + e.getMessage());
            weatherInfo.addProperty("suitable_for_outdoor_dining", false); // default to indoor
        }
        result.add("weather_forecast", weatherInfo);
        
        // Step 2: Search for outdoor dining restaurants near Golden Gate Park (if weather is suitable)
        boolean outdoorSuitable = weatherInfo.has("suitable_for_outdoor_dining") && 
                                 weatherInfo.get("suitable_for_outdoor_dining").getAsBoolean();
        
        maps_google_com maps = new maps_google_com(context);
        String searchLocation = "Golden Gate Park, San Francisco";
        String businessType = outdoorSuitable ? "outdoor dining restaurant" : "restaurant";
        int maxRestaurants = 8;
        
        maps_google_com.NearestBusinessesResult restaurantResult = maps.get_nearestBusinesses(
            searchLocation, businessType, maxRestaurants);
        
        JsonObject restaurantInfo = new JsonObject();
        restaurantInfo.addProperty("search_location", restaurantResult.referencePoint);
        restaurantInfo.addProperty("business_type", restaurantResult.businessDescription);
        restaurantInfo.addProperty("dining_type", outdoorSuitable ? "outdoor" : "indoor");
        
        JsonArray restaurantsArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : restaurantResult.businesses) {
            JsonObject restaurantObj = new JsonObject();
            restaurantObj.addProperty("name", business.name);
            restaurantObj.addProperty("address", business.address);
            restaurantsArray.add(restaurantObj);
        }
        restaurantInfo.add("restaurants", restaurantsArray);
        result.add("restaurant_search", restaurantInfo);
        
        // Step 3: Search Costco for romantic dinner supplies
        costco_com costco = new costco_com(context);
        String[] romanticSupplies = {"candles", "flowers", "wine"};
        
        JsonObject costcoInfo = new JsonObject();
        JsonArray suppliesArray = new JsonArray();
        
        for (String supply : romanticSupplies) {
            costco_com.ProductInfo productResult = costco.searchProduct(supply);
            JsonObject supplyObj = new JsonObject();
            supplyObj.addProperty("search_term", supply);
            
            if (productResult.error != null) {
                supplyObj.addProperty("error", productResult.error);
            } else {
                supplyObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    supplyObj.addProperty("price", productResult.productPrice.amount);
                    supplyObj.addProperty("currency", productResult.productPrice.currency);
                }
            }
            suppliesArray.add(supplyObj);
        }
        costcoInfo.add("romantic_supplies", suppliesArray);
        result.add("costco_supplies", costcoInfo);
        
        // Step 4: Search Spotify for top 5 love songs
        Spotify spotify = new Spotify();
        String loveQuery = "love songs romantic";
        
        JsonObject spotifyInfo = new JsonObject();
        try {
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems(loveQuery, "track", null, 5, 0, null);
            if (spotifyResult.errorMessage != null) {
                spotifyInfo.addProperty("error", spotifyResult.errorMessage);
                spotifyInfo.add("love_songs", new JsonArray());
            } else {
                spotifyInfo.addProperty("search_query", loveQuery);
                JsonArray songsArray = new JsonArray();
                for (Spotify.SpotifyTrack track : spotifyResult.tracks) {
                    JsonObject songObj = new JsonObject();
                    songObj.addProperty("name", track.name);
                    songObj.addProperty("artists", String.join(", ", track.artistNames));
                    songObj.addProperty("album", track.albumName);
                    songObj.addProperty("popularity", track.popularity);
                    songObj.addProperty("uri", track.uri);
                    if (track.duration != null) {
                        long minutes = track.duration.toMinutes();
                        long seconds = track.duration.getSeconds() % 60;
                        songObj.addProperty("duration", String.format("%d:%02d", minutes, seconds));
                    }
                    songsArray.add(songObj);
                }
                spotifyInfo.add("love_songs", songsArray);
            }
        } catch (Exception e) {
            spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
            spotifyInfo.add("love_songs", new JsonArray());
        }
        result.add("spotify_love_songs", spotifyInfo);
        
        return result;
    }
}
