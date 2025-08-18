import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0055 {
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
        
        try {
            // Step 1: Get weather forecast for Boulder for August 16-17, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> boulderLocations = weather.getLocationsByName("Boulder, CO");
            
            JsonObject weatherForecast = new JsonObject();
            if (!boulderLocations.isEmpty()) {
                OpenWeather.LocationData boulder = boulderLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(boulder.getLatitude(), boulder.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("hiking_dates", "August 16-17, 2025");
                
                JsonArray forecastArray = new JsonArray();
                for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                    JsonObject forecastEntry = new JsonObject();
                    forecastEntry.addProperty("date_time", entry.getDateTime().toString());
                    forecastEntry.addProperty("condition", entry.getCondition());
                    forecastEntry.addProperty("description", entry.getDescription());
                    forecastEntry.addProperty("temperature", entry.getTemperature());
                    forecastEntry.addProperty("temp_min", entry.getTempMin());
                    forecastEntry.addProperty("temp_max", entry.getTempMax());
                    forecastEntry.addProperty("humidity", entry.getHumidity());
                    forecastEntry.addProperty("wind_speed", entry.getWindSpeed());
                    
                    // Mark if this is during hiking weekend
                    String dateStr = entry.getDateTime().toString();
                    if (dateStr.contains("2025-08-16") || dateStr.contains("2025-08-17")) {
                        forecastEntry.addProperty("is_hiking_weekend", true);
                    }
                    
                    forecastArray.add(forecastEntry);
                }
                weatherForecast.add("forecasts", forecastArray);
                weatherForecast.addProperty("hiking_preparation", "Weather conditions for trip planning");
            } else {
                weatherForecast.addProperty("error", "Could not find location data for Boulder, CO");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 2: Find 5 nearest hiking trails to hotel location
            maps_google_com maps = new maps_google_com(context);
            String hotelLocation = "Boulder, CO"; // Using city center as hotel reference
            maps_google_com.NearestBusinessesResult hikingTrails = maps.get_nearestBusinesses(hotelLocation, "hiking trail", 5);
            
            JsonObject trailsInfo = new JsonObject();
            trailsInfo.addProperty("hotel_location", hotelLocation);
            trailsInfo.addProperty("search_type", "hiking trails");
            trailsInfo.addProperty("requested_count", 5);
            
            JsonArray trailsArray = new JsonArray();
            String closestTrailhead = null;
            
            for (maps_google_com.BusinessInfo trail : hikingTrails.businesses) {
                JsonObject trailObj = new JsonObject();
                trailObj.addProperty("name", trail.name);
                trailObj.addProperty("address", trail.address);
                
                // Get directions from hotel to trail
                maps_google_com.DirectionResult direction = maps.get_direction(hotelLocation, trail.address);
                trailObj.addProperty("distance_from_hotel", direction.distance);
                trailObj.addProperty("travel_time", direction.travelTime);
                trailObj.addProperty("route", direction.route);
                
                // Save the first trail as closest trailhead for gear store search
                if (closestTrailhead == null) {
                    closestTrailhead = trail.address;
                }
                
                trailsArray.add(trailObj);
            }
            
            trailsInfo.add("trails", trailsArray);
            trailsInfo.addProperty("trails_found", trailsArray.size());
            result.add("hiking_trails", trailsInfo);
            
            // Step 3: Find 3 closest outdoor gear stores to the trailhead
            JsonObject gearStoresInfo = new JsonObject();
            if (closestTrailhead != null) {
                maps_google_com.NearestBusinessesResult gearStores = maps.get_nearestBusinesses(closestTrailhead, "outdoor gear store", 3);
                
                gearStoresInfo.addProperty("reference_trailhead", closestTrailhead);
                gearStoresInfo.addProperty("search_type", "outdoor gear stores");
                gearStoresInfo.addProperty("requested_count", 3);
                
                JsonArray storesArray = new JsonArray();
                for (maps_google_com.BusinessInfo store : gearStores.businesses) {
                    JsonObject storeObj = new JsonObject();
                    storeObj.addProperty("name", store.name);
                    storeObj.addProperty("address", store.address);
                    
                    // Get directions from trailhead to gear store
                    maps_google_com.DirectionResult direction = maps.get_direction(closestTrailhead, store.address);
                    storeObj.addProperty("distance_from_trailhead", direction.distance);
                    storeObj.addProperty("travel_time", direction.travelTime);
                    storeObj.addProperty("route", direction.route);
                    
                    storesArray.add(storeObj);
                }
                
                gearStoresInfo.add("gear_stores", storesArray);
                gearStoresInfo.addProperty("stores_found", storesArray.size());
            } else {
                gearStoresInfo.addProperty("error", "No trailhead available for gear store search");
            }
            result.add("gear_stores", gearStoresInfo);
            
            // Step 4: Search for recent news about Boulder hiking trail conditions
            News news = new News();
            News.NewsResponse trailNews = news.searchEverything("Boulder hiking trail conditions closures", "en", 10);
            
            JsonObject trailConditions = new JsonObject();
            trailConditions.addProperty("search_query", "Boulder hiking trail conditions closures");
            trailConditions.addProperty("purpose", "Check for trail closures or hazards");
            trailConditions.addProperty("total_results", trailNews.totalResults);
            trailConditions.addProperty("status", trailNews.status);
            
            JsonArray newsArray = new JsonArray();
            if (trailNews.articles != null) {
                int articleCount = Math.min(5, trailNews.articles.size());
                for (int i = 0; i < articleCount; i++) {
                    News.NewsArticle article = trailNews.articles.get(i);
                    JsonObject articleObj = new JsonObject();
                    articleObj.addProperty("title", article.title);
                    articleObj.addProperty("description", article.description);
                    articleObj.addProperty("url", article.url);
                    articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : "Unknown");
                    articleObj.addProperty("source", article.source);
                    articleObj.addProperty("relevance", "Trail safety and conditions information");
                    newsArray.add(articleObj);
                }
            }
            
            trailConditions.add("recent_news", newsArray);
            trailConditions.addProperty("articles_found", newsArray.size());
            result.add("trail_conditions_news", trailConditions);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("trip_type", "Weekend Hiking Trip");
            summary.addProperty("destination", "Boulder, Colorado");
            summary.addProperty("dates", "August 16-17, 2025");
            summary.addProperty("weather_forecast_available", !boulderLocations.isEmpty());
            summary.addProperty("hiking_trails_found", hikingTrails.businesses.size());
            summary.addProperty("gear_stores_found", gearStoresInfo.has("stores_found") ? 
                gearStoresInfo.get("stores_found").getAsInt() : 0);
            summary.addProperty("trail_condition_articles", newsArray.size());
            summary.addProperty("trip_preparation_status", "Ready for outdoor adventure");
            result.add("hiking_trip_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
