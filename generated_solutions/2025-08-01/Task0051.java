import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0051 {
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
            // Step 1: Search for apartments in Seattle, WA with budget $1800-$2500
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentResult = redfin.searchApartments("Seattle, WA", 1800, 2500);
            
            JsonArray apartmentsArray = new JsonArray();
            List<redfin_com.ApartmentInfo> topApartments = new ArrayList<>();
            
            if (apartmentResult.apartments != null && !apartmentResult.apartments.isEmpty()) {
                // Get top 3 apartments (they should already be sorted by relevance/price)
                int count = Math.min(3, apartmentResult.apartments.size());
                for (int i = 0; i < count; i++) {
                    redfin_com.ApartmentInfo apartment = apartmentResult.apartments.get(i);
                    topApartments.add(apartment);
                    
                    JsonObject apartmentObj = new JsonObject();
                    apartmentObj.addProperty("address", apartment.address);
                    apartmentObj.addProperty("price", apartment.price.amount);
                    apartmentObj.addProperty("currency", apartment.price.currency);
                    apartmentObj.addProperty("url", apartment.url);
                    apartmentsArray.add(apartmentObj);
                }
            }
            result.add("top_apartments", apartmentsArray);
            
            // Step 2: Get 7-day weather forecast for Seattle starting August 18, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> seattleLocations = weather.getLocationsByName("Seattle, WA");
            
            JsonObject weatherForecast = new JsonObject();
            if (!seattleLocations.isEmpty()) {
                OpenWeather.LocationData seattle = seattleLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(seattle.getLatitude(), seattle.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                
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
                    forecastArray.add(forecastEntry);
                }
                weatherForecast.add("forecasts", forecastArray);
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Find 5 nearest coffee shops to the best apartment
            JsonObject coffeeShopsInfo = new JsonObject();
            if (!topApartments.isEmpty()) {
                String bestApartmentAddress = topApartments.get(0).address;
                
                maps_google_com maps = new maps_google_com(context);
                maps_google_com.NearestBusinessesResult coffeeShopsResult = maps.get_nearestBusinesses(bestApartmentAddress, "coffee shop", 5);
                
                coffeeShopsInfo.addProperty("reference_apartment", bestApartmentAddress);
                coffeeShopsInfo.addProperty("business_description", coffeeShopsResult.businessDescription);
                
                JsonArray coffeeShopsArray = new JsonArray();
                double totalDistance = 0.0;
                int validDistances = 0;
                
                for (maps_google_com.BusinessInfo business : coffeeShopsResult.businesses) {
                    JsonObject coffeeShop = new JsonObject();
                    coffeeShop.addProperty("name", business.name);
                    coffeeShop.addProperty("address", business.address);
                    
                    // Get walking distance from apartment to coffee shop
                    maps_google_com.DirectionResult direction = maps.get_direction(bestApartmentAddress, business.address);
                    coffeeShop.addProperty("walking_distance", direction.distance);
                    coffeeShop.addProperty("walking_time", direction.travelTime);
                    
                    // Try to extract numeric distance for average calculation
                    try {
                        String distanceStr = direction.distance.replaceAll("[^0-9.]", "");
                        if (!distanceStr.isEmpty()) {
                            double distance = Double.parseDouble(distanceStr);
                            totalDistance += distance;
                            validDistances++;
                        }
                    } catch (NumberFormatException e) {
                        // Ignore if we can't parse the distance
                    }
                    
                    coffeeShopsArray.add(coffeeShop);
                }
                
                coffeeShopsInfo.add("coffee_shops", coffeeShopsArray);
                
                if (validDistances > 0) {
                    double averageDistance = totalDistance / validDistances;
                    coffeeShopsInfo.addProperty("average_walking_distance", String.format("%.2f miles", averageDistance));
                }
            }
            result.add("coffee_shops", coffeeShopsInfo);
            
            // Step 4: Search for books about Seattle's history and create reading list
            OpenLibrary library = new OpenLibrary();
            List<OpenLibrary.BookInfo> historyBooks = library.search("Seattle history", "title,author_name", "new", "en", 10, 1);
            
            JsonArray readingListArray = new JsonArray();
            int bookCount = Math.min(5, historyBooks.size());
            for (int i = 0; i < bookCount; i++) {
                OpenLibrary.BookInfo book = historyBooks.get(i);
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                bookObj.addProperty("recommendation_reason", "Recommended for learning about Seattle's history");
                readingListArray.add(bookObj);
            }
            
            JsonObject readingList = new JsonObject();
            readingList.addProperty("topic", "Seattle History");
            readingList.addProperty("total_books", bookCount);
            readingList.add("books", readingListArray);
            result.add("reading_list", readingList);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("move_in_date", "August 18, 2025");
            summary.addProperty("location", "Seattle, Washington");
            summary.addProperty("budget_range", "$1800 - $2500");
            summary.addProperty("apartments_found", apartmentsArray.size());
            summary.addProperty("weather_forecast_available", weatherForecast.has("forecasts"));
            summary.addProperty("coffee_shops_found", coffeeShopsInfo.has("coffee_shops") ? 
                coffeeShopsInfo.getAsJsonArray("coffee_shops").size() : 0);
            summary.addProperty("reading_list_books", bookCount);
            result.add("summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
