import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0001 {
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
        
        // Step 1: Search for flights from Seattle to Orlando for September 10-17, 2025
        alaskaair_com flights = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 9, 10);
        LocalDate returnDate = LocalDate.of(2025, 9, 17);
        
        alaskaair_com.SearchFlightsResult flightSearch = flights.searchFlights("SEA", "MCO", outboundDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        if (flightSearch.message != null) {
            flightInfo.addProperty("message", flightSearch.message);
        } else if (flightSearch.flightInfo != null) {
            JsonArray flightArray = new JsonArray();
            for (String flight : flightSearch.flightInfo.flights) {
                flightArray.add(flight);
            }
            flightInfo.add("flights", flightArray);
            if (flightSearch.flightInfo.price != null) {
                JsonObject priceObj = new JsonObject();
                priceObj.addProperty("amount", flightSearch.flightInfo.price.amount);
                priceObj.addProperty("currency", flightSearch.flightInfo.price.currency);
                flightInfo.add("price", priceObj);
            }
        }
        result.add("flight_search", flightInfo);
        
        // Step 2: Look for hotels in Orlando during the stay from August 10-17, 2025
        booking_com hotels = new booking_com(context);
        booking_com.HotelSearchResult hotelSearch = hotels.search_hotel("Orlando, Florida", outboundDate, returnDate);
        
        JsonObject hotelInfo = new JsonObject();
        hotelInfo.addProperty("destination", hotelSearch.destination);
        hotelInfo.addProperty("check_in_date", hotelSearch.checkinDate.toString());
        hotelInfo.addProperty("check_out_date", hotelSearch.checkoutDate.toString());
        
        JsonArray hotelArray = new JsonArray();
        for (booking_com.HotelInfo hotel : hotelSearch.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotel_name", hotel.hotelName);
            if (hotel.price != null) {
                JsonObject priceObj = new JsonObject();
                priceObj.addProperty("amount", hotel.price.amount);
                priceObj.addProperty("currency", hotel.price.currency);
                hotelObj.add("price", priceObj);
            }
            hotelArray.add(hotelObj);
        }
        hotelInfo.add("hotels", hotelArray);
        result.add("hotel_search", hotelInfo);
        
        // Step 3: Check the weather forecast for Orlando during the trip
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // First get the location coordinates for Orlando
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Orlando, FL");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData location = locations.get(0);
                double lat = location.getLatitude();
                double lon = location.getLongitude();
                
                // Get weather forecast using coordinates
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                
                weatherInfo.addProperty("city", forecast.getCityName());
                weatherInfo.addProperty("country", forecast.getCountry());
                weatherInfo.addProperty("latitude", forecast.getLatitude());
                weatherInfo.addProperty("longitude", forecast.getLongitude());
                
                JsonArray forecastArray = new JsonArray();
                for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                    JsonObject forecastObj = new JsonObject();
                    forecastObj.addProperty("date_time", entry.getDateTime().toString());
                    forecastObj.addProperty("condition", entry.getCondition());
                    forecastObj.addProperty("description", entry.getDescription());
                    forecastObj.addProperty("temperature", entry.getTemperature());
                    forecastObj.addProperty("temp_min", entry.getTempMin());
                    forecastObj.addProperty("temp_max", entry.getTempMax());
                    forecastObj.addProperty("humidity", entry.getHumidity());
                    forecastObj.addProperty("wind_speed", entry.getWindSpeed());
                    forecastArray.add(forecastObj);
                }
                weatherInfo.add("forecast", forecastArray);
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Orlando, FL");
            }
        } catch (Exception e) {
            weatherInfo.addProperty("error", "Failed to get weather forecast: " + e.getMessage());
        }
        result.add("weather_forecast", weatherInfo);
        
        // Step 4: Find nearby theme parks and attractions around Orlando
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult themeParks = maps.get_nearestBusinesses("Orlando, Florida", "theme park", 10);
        maps_google_com.NearestBusinessesResult attractions = maps.get_nearestBusinesses("Orlando, Florida", "tourist attraction", 10);
        
        JsonObject entertainmentInfo = new JsonObject();
        
        JsonArray themeParksArray = new JsonArray();
        for (maps_google_com.BusinessInfo park : themeParks.businesses) {
            JsonObject parkObj = new JsonObject();
            parkObj.addProperty("name", park.name);
            parkObj.addProperty("address", park.address);
            themeParksArray.add(parkObj);
        }
        entertainmentInfo.add("theme_parks", themeParksArray);
        
        JsonArray attractionsArray = new JsonArray();
        for (maps_google_com.BusinessInfo attraction : attractions.businesses) {
            JsonObject attractionObj = new JsonObject();
            attractionObj.addProperty("name", attraction.name);
            attractionObj.addProperty("address", attraction.address);
            attractionsArray.add(attractionObj);
        }
        entertainmentInfo.add("attractions", attractionsArray);
        result.add("entertainment_options", entertainmentInfo);
        
        return result;
    }
}
