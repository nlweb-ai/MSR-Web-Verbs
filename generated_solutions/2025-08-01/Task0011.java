import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0011 {
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
        
        // 1. Search for hotels in Portland, Oregon for August 15-17
        booking_com booking = new booking_com(context);
        LocalDate checkinDate = LocalDate.of(2025, 8, 15);
        LocalDate checkoutDate = LocalDate.of(2025, 8, 17);
        
        booking_com.HotelSearchResult hotelResults = booking.search_hotel("Portland, Oregon", checkinDate, checkoutDate);
        
        JsonObject hotelInfo = new JsonObject();
        hotelInfo.addProperty("destination", hotelResults.destination);
        hotelInfo.addProperty("checkinDate", hotelResults.checkinDate.toString());
        hotelInfo.addProperty("checkoutDate", hotelResults.checkoutDate.toString());
        
        JsonArray hotelsArray = new JsonArray();
        double totalBudget = 0.0;
        double minPrice = Double.MAX_VALUE;
        double maxPrice = 0.0;
        
        for (booking_com.HotelInfo hotel : hotelResults.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotelName", hotel.hotelName);
            if (hotel.price != null) {
                hotelObj.addProperty("priceAmount", hotel.price.amount);
                hotelObj.addProperty("priceCurrency", hotel.price.currency);
                totalBudget += hotel.price.amount;
                minPrice = Math.min(minPrice, hotel.price.amount);
                maxPrice = Math.max(maxPrice, hotel.price.amount);
            } else {
                hotelObj.addProperty("priceAmount", (String) null);
                hotelObj.addProperty("priceCurrency", (String) null);
            }
            hotelsArray.add(hotelObj);
        }
        
        hotelInfo.add("hotels", hotelsArray);
        
        // Calculate accommodation budget
        JsonObject budgetInfo = new JsonObject();
        if (!hotelResults.hotels.isEmpty() && minPrice != Double.MAX_VALUE) {
            double averagePrice = totalBudget / hotelResults.hotels.size();
            budgetInfo.addProperty("totalHotelsFound", hotelResults.hotels.size());
            budgetInfo.addProperty("averagePrice", Math.round(averagePrice * 100.0) / 100.0);
            budgetInfo.addProperty("minPrice", Math.round(minPrice * 100.0) / 100.0);
            budgetInfo.addProperty("maxPrice", Math.round(maxPrice * 100.0) / 100.0);
            // Assuming a budget calculation based on average price for 2 nights
            double estimatedAccommodationCost = averagePrice * 2;
            budgetInfo.addProperty("estimatedAccommodationCost", Math.round(estimatedAccommodationCost * 100.0) / 100.0);
        }
        
        result.add("hotelSearch", hotelInfo);
        result.add("accommodationBudget", budgetInfo);
        
        // 2. Check current weather in Portland
        try {
            OpenWeather weather = new OpenWeather();
            // Portland, Oregon coordinates (approximate)
            double portlandLat = 45.5152;
            double portlandLon = -122.6784;
            
            OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(portlandLat, portlandLon);
            
            JsonObject weatherInfo = new JsonObject();
            weatherInfo.addProperty("cityName", currentWeather.getCityName());
            weatherInfo.addProperty("country", currentWeather.getCountry());
            weatherInfo.addProperty("date", currentWeather.getDate().toString());
            weatherInfo.addProperty("condition", currentWeather.getCondition());
            weatherInfo.addProperty("description", currentWeather.getDescription());
            weatherInfo.addProperty("temperature", Math.round(currentWeather.getTemperature() * 100.0) / 100.0);
            weatherInfo.addProperty("feelsLike", Math.round(currentWeather.getFeelsLike() * 100.0) / 100.0);
            weatherInfo.addProperty("tempMin", Math.round(currentWeather.getTempMin() * 100.0) / 100.0);
            weatherInfo.addProperty("tempMax", Math.round(currentWeather.getTempMax() * 100.0) / 100.0);
            weatherInfo.addProperty("humidity", currentWeather.getHumidity());
            weatherInfo.addProperty("windSpeed", Math.round(currentWeather.getWindSpeed() * 100.0) / 100.0);
            weatherInfo.addProperty("cloudiness", currentWeather.getCloudiness());
            
            result.add("currentWeather", weatherInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject weatherError = new JsonObject();
            weatherError.addProperty("error", "Failed to get weather data: " + e.getMessage());
            result.add("currentWeather", weatherError);
        }
        
        // 3. Find restaurants and cafes near downtown Portland
        maps_google_com maps = new maps_google_com(context);
        
        maps_google_com.NearestBusinessesResult restaurants = maps.get_nearestBusinesses(
            "downtown Portland, Oregon", "restaurant", 10);
        
        JsonObject restaurantsInfo = new JsonObject();
        restaurantsInfo.addProperty("referencePoint", restaurants.referencePoint);
        restaurantsInfo.addProperty("businessDescription", restaurants.businessDescription);
        
        JsonArray restaurantsArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : restaurants.businesses) {
            JsonObject businessObj = new JsonObject();
            businessObj.addProperty("name", business.name);
            businessObj.addProperty("address", business.address);
            restaurantsArray.add(businessObj);
        }
        restaurantsInfo.add("restaurants", restaurantsArray);
        
        // Also search for cafes
        maps_google_com.NearestBusinessesResult cafes = maps.get_nearestBusinesses(
            "downtown Portland, Oregon", "cafe", 10);
        
        JsonObject cafesInfo = new JsonObject();
        cafesInfo.addProperty("referencePoint", cafes.referencePoint);
        cafesInfo.addProperty("businessDescription", cafes.businessDescription);
        
        JsonArray cafesArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : cafes.businesses) {
            JsonObject businessObj = new JsonObject();
            businessObj.addProperty("name", business.name);
            businessObj.addProperty("address", business.address);
            cafesArray.add(businessObj);
        }
        cafesInfo.add("cafes", cafesArray);
        
        JsonObject diningInfo = new JsonObject();
        diningInfo.add("restaurants", restaurantsInfo);
        diningInfo.add("cafes", cafesInfo);
        result.add("dining", diningInfo);
        
        // 4. Clear Amazon cart for travel essentials
        amazon_com amazon = new amazon_com(context);
        try {
            amazon.clearCart();
            JsonObject cartInfo = new JsonObject();
            cartInfo.addProperty("status", "Cart cleared successfully");
            cartInfo.addProperty("message", "Cart is now ready for travel-specific items");
            result.add("cartStatus", cartInfo);
        } catch (RuntimeException e) {
            JsonObject cartError = new JsonObject();
            cartError.addProperty("status", "Failed to clear cart");
            cartError.addProperty("error", e.getMessage());
            result.add("cartStatus", cartError);
        }
        
        return result;
    }
}
