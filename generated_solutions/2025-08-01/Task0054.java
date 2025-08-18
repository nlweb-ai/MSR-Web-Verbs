import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0054 {
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
            // Step 1: Search for school supplies at Costco and calculate total cost
            costco_com costco = new costco_com(context);
            
            JsonObject schoolSupplies = new JsonObject();
            JsonArray suppliesArray = new JsonArray();
            double totalCost = 0.0;
            
            // Search for different school supply items
            String[] supplyItems = {"backpack", "notebook", "lunch box"};
            
            for (String item : supplyItems) {
                costco_com.ProductListResult productResult = costco.searchProducts(item);
                
                JsonObject itemCategory = new JsonObject();
                itemCategory.addProperty("category", item);
                itemCategory.addProperty("search_successful", productResult.products != null && !productResult.products.isEmpty());
                
                JsonArray productsArray = new JsonArray();
                if (productResult.products != null && !productResult.products.isEmpty()) {
                    // Take the first product as recommended
                    costco_com.ProductInfo product = productResult.products.get(0);
                    
                    JsonObject productObj = new JsonObject();
                    productObj.addProperty("name", product.productName);
                    productObj.addProperty("price", product.productPrice.amount);
                    productObj.addProperty("currency", product.productPrice.currency);
                    productObj.addProperty("recommended", true);
                    
                    productsArray.add(productObj);
                    totalCost += product.productPrice.amount;
                    
                    // Add a few more options
                    for (int i = 1; i < Math.min(3, productResult.products.size()); i++) {
                        costco_com.ProductInfo altProduct = productResult.products.get(i);
                        JsonObject altProductObj = new JsonObject();
                        altProductObj.addProperty("name", altProduct.productName);
                        altProductObj.addProperty("price", altProduct.productPrice.amount);
                        altProductObj.addProperty("currency", altProduct.productPrice.currency);
                        altProductObj.addProperty("recommended", false);
                        productsArray.add(altProductObj);
                    }
                }
                
                itemCategory.add("products", productsArray);
                suppliesArray.add(itemCategory);
            }
            
            schoolSupplies.add("supply_categories", suppliesArray);
            schoolSupplies.addProperty("total_cost", totalCost);
            schoolSupplies.addProperty("currency", "USD");
            schoolSupplies.addProperty("shopping_guide", "Back-to-school essentials from Costco");
            result.add("school_supplies", schoolSupplies);
            
            // Step 2: Get weather forecast for Dallas for August 19-23, 2025 (first week of school)
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> dallasLocations = weather.getLocationsByName("Dallas, TX");
            
            JsonObject weatherForecast = new JsonObject();
            if (!dallasLocations.isEmpty()) {
                OpenWeather.LocationData dallas = dallasLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(dallas.getLatitude(), dallas.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("school_week", "August 19-23, 2025");
                
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
                    
                    // Mark if this is during school week
                    String dateStr = entry.getDateTime().toString();
                    if (dateStr.contains("2025-08-19") || dateStr.contains("2025-08-20") || 
                        dateStr.contains("2025-08-21") || dateStr.contains("2025-08-22") || 
                        dateStr.contains("2025-08-23")) {
                        forecastEntry.addProperty("is_school_week", true);
                    }
                    
                    forecastArray.add(forecastEntry);
                }
                weatherForecast.add("forecasts", forecastArray);
                weatherForecast.addProperty("planning_note", "Weather forecast for first week of school");
            } else {
                weatherForecast.addProperty("error", "Could not find location data for Dallas, TX");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Set preferred warehouse to closest Dallas Costco location
            costco_com.WarehouseStatusResult warehouseStatus = costco.setPreferredWarehouse("Dallas, TX");
            
            JsonObject warehouseInfo = new JsonObject();
            warehouseInfo.addProperty("location_query", "Dallas, TX");
            warehouseInfo.addProperty("warehouse_found", warehouseStatus.error == null);
            
            if (warehouseStatus.error == null) {
                warehouseInfo.addProperty("status", warehouseStatus.status);
                warehouseInfo.addProperty("recommendation", "Visit the closest Dallas Costco for school supply shopping");
            } else {
                warehouseInfo.addProperty("status", warehouseStatus.error);
            }
            result.add("warehouse_info", warehouseInfo);
            
            // Step 4: Search YouTube for back-to-school tips and select 3 helpful videos
            youtube_com youtube = new youtube_com(context);
            List<youtube_com.YouTubeVideoInfo> backToSchoolVideos = youtube.searchVideos("back to school tips for students");
            
            JsonObject educationalVideos = new JsonObject();
            educationalVideos.addProperty("search_query", "back to school tips for students");
            educationalVideos.addProperty("target_videos", 3);
            
            JsonArray videosArray = new JsonArray();
            int videoCount = Math.min(3, backToSchoolVideos.size());
            
            for (int i = 0; i < videoCount; i++) {
                youtube_com.YouTubeVideoInfo video = backToSchoolVideos.get(i);
                JsonObject videoObj = new JsonObject();
                videoObj.addProperty("title", video.title);
                videoObj.addProperty("url", video.url);
                
                // Format duration
                if (video.length != null) {
                    long s = video.length.getSeconds();
                    long h = s / 3600;
                    long m = (s % 3600) / 60;
                    long sec = s % 60;
                    String lenStr = h > 0 ? String.format("%d:%02d:%02d", h, m, sec) : String.format("%d:%02d", m, sec);
                    videoObj.addProperty("duration", lenStr);
                }
                
                videoObj.addProperty("recommendation_reason", "Educational content for back-to-school preparation");
                videosArray.add(videoObj);
            }
            
            educationalVideos.add("recommended_videos", videosArray);
            educationalVideos.addProperty("videos_found", videoCount);
            result.add("educational_videos", educationalVideos);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("guide_title", "Back-to-School Shopping Guide for Dallas, Texas");
            summary.addProperty("school_year_start", "August 19, 2025");
            summary.addProperty("target_audience", "Parents preparing for new school year");
            summary.addProperty("total_supply_cost", totalCost);
            summary.addProperty("supply_categories_covered", suppliesArray.size());
            summary.addProperty("weather_forecast_available", !dallasLocations.isEmpty());
            summary.addProperty("warehouse_status", warehouseStatus.error == null ? "Available" : "Issue");
            summary.addProperty("educational_videos_recommended", videoCount);
            result.add("shopping_guide_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
