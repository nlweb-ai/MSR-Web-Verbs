import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0060 {
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
            // Step 1: Find 5 local farms or farmers markets near Sacramento
            maps_google_com maps = new maps_google_com(context);
            String festivalLocation = "Sacramento, CA";
            maps_google_com.NearestBusinessesResult localFarms = maps.get_nearestBusinesses(festivalLocation, "farm farmers market", 5);
            
            JsonObject farmsInfo = new JsonObject();
            farmsInfo.addProperty("festival_location", festivalLocation);
            farmsInfo.addProperty("search_type", "local farms and farmers markets");
            farmsInfo.addProperty("requested_count", 5);
            farmsInfo.addProperty("purpose", "Fresh produce sourcing for food festival");
            
            JsonArray farmsArray = new JsonArray();
            for (maps_google_com.BusinessInfo farm : localFarms.businesses) {
                JsonObject farmObj = new JsonObject();
                farmObj.addProperty("name", farm.name);
                farmObj.addProperty("address", farm.address);
                
                // Get directions from festival location to farm
                maps_google_com.DirectionResult direction = maps.get_direction(festivalLocation, farm.address);
                farmObj.addProperty("distance_from_festival", direction.distance);
                farmObj.addProperty("travel_time", direction.travelTime);
                farmObj.addProperty("route", direction.route);
                farmObj.addProperty("produce_potential", "Fresh local ingredients for festival");
                
                farmsArray.add(farmObj);
            }
            
            farmsInfo.add("local_farms", farmsArray);
            farmsInfo.addProperty("farms_found", farmsArray.size());
            result.add("local_produce_sources", farmsInfo);
            
            // Step 2: Get weather forecast for Sacramento on August 30, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> sacramentoLocations = weather.getLocationsByName("Sacramento, CA");
            
            JsonObject weatherForecast = new JsonObject();
            if (!sacramentoLocations.isEmpty()) {
                OpenWeather.LocationData sacramento = sacramentoLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(sacramento.getLatitude(), sacramento.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("festival_date", "August 30, 2025");
                
                JsonArray forecastArray = new JsonArray();
                boolean foundFestivalDate = false;
                
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
                    
                    // Check if this is the festival date
                    String dateStr = entry.getDateTime().toString();
                    if (dateStr.contains("2025-08-30")) {
                        forecastEntry.addProperty("is_festival_date", true);
                        forecastEntry.addProperty("tent_shade_planning", "Plan for outdoor food festival setup");
                        foundFestivalDate = true;
                    }
                    
                    forecastArray.add(forecastEntry);
                }
                
                weatherForecast.add("forecasts", forecastArray);
                weatherForecast.addProperty("festival_planning_note", foundFestivalDate ? "Weather data available for festival date" : "General forecast for event planning");
                weatherForecast.addProperty("shade_recommendation", "Consider tents or shade structures based on conditions");
            } else {
                weatherForecast.addProperty("error", "Could not find location data for Sacramento, CA");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Find 3 closest kitchen supply stores to festival venue
            maps_google_com.NearestBusinessesResult kitchenSupplies = maps.get_nearestBusinesses(festivalLocation, "kitchen supply store", 3);
            
            JsonObject kitchenStoresInfo = new JsonObject();
            kitchenStoresInfo.addProperty("festival_venue", festivalLocation);
            kitchenStoresInfo.addProperty("search_type", "kitchen supply stores");
            kitchenStoresInfo.addProperty("requested_count", 3);
            kitchenStoresInfo.addProperty("purpose", "Festival cooking equipment and supplies");
            
            JsonArray storesArray = new JsonArray();
            for (maps_google_com.BusinessInfo store : kitchenSupplies.businesses) {
                JsonObject storeObj = new JsonObject();
                storeObj.addProperty("name", store.name);
                storeObj.addProperty("address", store.address);
                
                // Get directions from festival venue to kitchen store
                maps_google_com.DirectionResult direction = maps.get_direction(festivalLocation, store.address);
                storeObj.addProperty("distance_from_venue", direction.distance);
                storeObj.addProperty("travel_time", direction.travelTime);
                storeObj.addProperty("route", direction.route);
                storeObj.addProperty("supply_value", "Essential cooking equipment for festival vendors");
                
                storesArray.add(storeObj);
            }
            
            kitchenStoresInfo.add("kitchen_stores", storesArray);
            kitchenStoresInfo.addProperty("stores_found", storesArray.size());
            result.add("kitchen_supplies", kitchenStoresInfo);
            
            // Step 4: Search for recent news about California agriculture
            News news = new News();
            News.NewsResponse agricultureNews = news.searchEverything("California agriculture farming", "en", 15);
            
            JsonObject agricultureInfo = new JsonObject();
            agricultureInfo.addProperty("news_topic", "California Agriculture");
            agricultureInfo.addProperty("purpose", "Educational content for festival attendees");
            agricultureInfo.addProperty("festival_relevance", "Highlighting local farming and agriculture");
            agricultureInfo.addProperty("total_results", agricultureNews.totalResults);
            agricultureInfo.addProperty("status", agricultureNews.status);
            
            JsonArray articlesArray = new JsonArray();
            if (agricultureNews.articles != null) {
                int articleCount = Math.min(8, agricultureNews.articles.size());
                for (int i = 0; i < articleCount; i++) {
                    News.NewsArticle article = agricultureNews.articles.get(i);
                    JsonObject articleObj = new JsonObject();
                    articleObj.addProperty("title", article.title);
                    articleObj.addProperty("description", article.description);
                    articleObj.addProperty("url", article.url);
                    articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : "Unknown");
                    articleObj.addProperty("source", article.source);
                    articleObj.addProperty("festival_value", "Educational content about local agriculture");
                    articleObj.addProperty("attendee_interest", "Connects food to local farming practices");
                    articlesArray.add(articleObj);
                }
            }
            
            agricultureInfo.add("recent_articles", articlesArray);
            agricultureInfo.addProperty("articles_collected", articlesArray.size());
            agricultureInfo.addProperty("educational_impact", "Enhances festival with agricultural awareness");
            result.add("agriculture_news", agricultureInfo);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("event", "Local Food Festival");
            summary.addProperty("location", "Sacramento, California");
            summary.addProperty("date", "August 30, 2025");
            summary.addProperty("theme", "Local agriculture and fresh produce");
            summary.addProperty("farms_identified", localFarms.businesses.size());
            summary.addProperty("weather_forecast_available", !sacramentoLocations.isEmpty());
            summary.addProperty("kitchen_supply_stores", kitchenSupplies.businesses.size());
            summary.addProperty("agriculture_articles", articlesArray.size());
            summary.addProperty("festival_readiness", "Fully prepared to celebrate California agriculture");
            result.add("food_festival_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
