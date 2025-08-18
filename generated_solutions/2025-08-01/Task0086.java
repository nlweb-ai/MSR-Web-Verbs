import java.io.IOException;
import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0086 {
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
        
        // Step 1: Search for flights from Chicago to Miami for August 30, 2025
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate flightDate = LocalDate.of(2025, 8, 30);
        LocalDate returnDate = LocalDate.of(2025, 8, 31);
        
        alaskaair_com.SearchFlightsResult flightResult = alaska.searchFlights("ORD", "MIA", flightDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        if (flightResult.message != null) {
            flightInfo.addProperty("message", flightResult.message);
            flightInfo.addProperty("estimated_flight_cost", 0.0);
        } else if (flightResult.flightInfo != null) {
            JsonArray flightsArray = new JsonArray();
            for (String flight : flightResult.flightInfo.flights) {
                flightsArray.add(flight);
            }
            flightInfo.add("available_flights", flightsArray);
            if (flightResult.flightInfo.price != null) {
                flightInfo.addProperty("estimated_flight_cost", flightResult.flightInfo.price.amount);
                flightInfo.addProperty("currency", flightResult.flightInfo.price.currency);
            } else {
                flightInfo.addProperty("estimated_flight_cost", 0.0);
            }
        }
        result.add("chicago_to_miami_flights", flightInfo);
        
        // Step 2: Search for large accommodations in Miami for 12 people
        booking_com booking = new booking_com(context);
        LocalDate checkinDate = LocalDate.of(2025, 8, 30);
        LocalDate checkoutDate = LocalDate.of(2025, 8, 31);
        
        booking_com.HotelSearchResult hotelResult = booking.search_hotel("Miami, Florida", checkinDate, checkoutDate);
        
        JsonObject accommodationInfo = new JsonObject();
        accommodationInfo.addProperty("destination", hotelResult.destination);
        accommodationInfo.addProperty("checkin_date", hotelResult.checkinDate.toString());
        accommodationInfo.addProperty("checkout_date", hotelResult.checkoutDate.toString());
        accommodationInfo.addProperty("required_capacity", 12);
        
        JsonArray accommodationsArray = new JsonArray();
        double totalAccommodationCost = 0.0;
        int accommodationCount = 0;
        
        for (booking_com.HotelInfo hotel : hotelResult.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotel_name", hotel.hotelName);
            if (hotel.price != null) {
                hotelObj.addProperty("price_per_night", hotel.price.amount);
                hotelObj.addProperty("currency", hotel.price.currency);
                totalAccommodationCost += hotel.price.amount;
                accommodationCount++;
            }
            accommodationsArray.add(hotelObj);
        }
        accommodationInfo.add("accommodations", accommodationsArray);
        
        // Calculate cost per person
        double avgAccommodationCost = accommodationCount > 0 ? totalAccommodationCost / accommodationCount : 0.0;
        double flightCost = flightInfo.has("estimated_flight_cost") ? flightInfo.get("estimated_flight_cost").getAsDouble() : 0.0;
        double totalCostPerPerson = (avgAccommodationCost / 12) + flightCost; // Accommodation divided by 12, plus individual flight cost
        
        accommodationInfo.addProperty("average_accommodation_cost", avgAccommodationCost);
        accommodationInfo.addProperty("cost_per_person", totalCostPerPerson);
        result.add("miami_accommodations", accommodationInfo);
        
        // Step 3: Search Amazon for party supplies and decorations
        amazon_com amazon = new amazon_com(context);
        String partySupplies = "family reunion party supplies decorations";
        
        amazon_com.CartResult partyItems = amazon.addItemToCart(partySupplies);
        
        JsonObject partyInfo = new JsonObject();
        partyInfo.addProperty("search_term", partySupplies);
        JsonArray partyItemsArray = new JsonArray();
        for (amazon_com.CartItem item : partyItems.items) {
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("item_name", item.itemName);
            if (item.price != null) {
                itemObj.addProperty("price", item.price.amount);
                itemObj.addProperty("currency", item.price.currency);
            }
            partyItemsArray.add(itemObj);
        }
        partyInfo.add("party_supplies", partyItemsArray);
        result.add("amazon_party_supplies", partyInfo);
        
        // Step 4: Check current weather in Miami
        OpenWeather weather = new OpenWeather();
        
        JsonObject weatherInfo = new JsonObject();
        try {
            // Get location coordinates for Miami
            java.util.List<OpenWeather.LocationData> locations = weather.getLocationsByName("Miami, Florida");
            if (locations.isEmpty()) {
                weatherInfo.addProperty("error", "Miami location not found");
            } else {
                OpenWeather.LocationData miamiLocation = locations.get(0);
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(
                    miamiLocation.getLatitude(), miamiLocation.getLongitude());
                
                weatherInfo.addProperty("city", currentWeather.getCityName());
                weatherInfo.addProperty("temperature", currentWeather.getTemperature());
                weatherInfo.addProperty("condition", currentWeather.getCondition());
                weatherInfo.addProperty("description", currentWeather.getDescription());
                weatherInfo.addProperty("humidity", currentWeather.getHumidity());
                weatherInfo.addProperty("wind_speed", currentWeather.getWindSpeed());
                
                // Recommendations based on weather
                String recommendation = getWeatherRecommendation(currentWeather.getTemperature(), 
                                                               currentWeather.getCondition());
                weatherInfo.addProperty("activity_recommendation", recommendation);
            }
        } catch (IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to fetch Miami weather: " + e.getMessage());
        }
        result.add("miami_weather", weatherInfo);
        
        // Family reunion summary
        JsonObject reunionSummary = new JsonObject();
        reunionSummary.addProperty("event_type", "Family Reunion");
        reunionSummary.addProperty("location", "Miami, Florida");
        reunionSummary.addProperty("date", "2025-08-30");
        reunionSummary.addProperty("expected_attendees", 12);
        reunionSummary.addProperty("estimated_cost_per_person", totalCostPerPerson);
        reunionSummary.addProperty("flight_route", "Chicago (ORD) to Miami (MIA)");
        result.add("reunion_summary", reunionSummary);
        
        return result;
    }
    
    // Helper method to provide weather-based recommendations
    private static String getWeatherRecommendation(double temperature, String condition) {
        String conditionLower = condition.toLowerCase();
        if (conditionLower.contains("rain") || conditionLower.contains("storm")) {
            return "Indoor activities recommended - consider hotel conference rooms or covered venues";
        } else if (temperature > 85.0) {
            return "Hot weather - plan morning or evening outdoor activities, ensure hydration";
        } else if (temperature > 70.0) {
            return "Perfect weather for outdoor activities - beach, parks, outdoor dining";
        } else {
            return "Mild weather - comfortable for both indoor and outdoor activities";
        }
    }
}
