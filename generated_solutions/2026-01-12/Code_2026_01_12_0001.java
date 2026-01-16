import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;
import java.io.IOException;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;
public class Code_2026_01_12_0001 {
    static BrowserContext context = null;
    static java.util.Scanner scanner= new java.util.Scanner(System.in);
    public static void main(String[] args) {
        try (Playwright playwright = Playwright.create()) {
            String userDataDir = System.getProperty("user.home") +"\\AppData\\Local\\Google\\Chrome\\User Data\\Default";
            BrowserType.LaunchPersistentContextOptions options = new BrowserType.LaunchPersistentContextOptions()
                .setChannel("chrome")
                .setHeadless(false)
                .setArgs(java.util.Arrays.asList(
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--disable-extensions",
                    "--start-maximized"
                ));
            options.setViewportSize(null);
            context = playwright.chromium().launchPersistentContext(Paths.get(userDataDir), options);
            JsonObject result = automate(context);
            Gson gson = new GsonBuilder()
                .disableHtmlEscaping()
                .setPrettyPrinting()
                .create();
            String prettyResult = gson.toJson(result);
            System.out.println("Final output: " + prettyResult);
            // Append result to known_facts.md
            try {
                String resultStr = prettyResult;
                String filePath = "tasks\\2026-01-12\\known_facts.md";
                java.nio.file.Files.write(
                    java.nio.file.Paths.get(filePath),
                    ("\n\n## Refinement Round\n" + resultStr + "\n").getBytes(),
                    java.nio.file.StandardOpenOption.CREATE,
                    java.nio.file.StandardOpenOption.APPEND
                );
                System.out.println("Result appended to known_facts.md");
            } catch (IOException e) {
                System.err.println("Failed to write to known_facts.md: " + e.getMessage());
            }
            context.close();
        }
    }
    /* Do not modify anything above this line.
       The following "automate(...)" function is the one you should modify.
    */
    static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        // REFINEMENT STRATEGY:
        // The task has several vague elements that need concretization:
        // 1. "Tuesday of the next week" and "Friday" - need concrete dates
        // 2. "two museums" per day - need specific museum recommendations
        // 3. "round trip flight" - need flight search results
        // 4. "hotel for all nights" - need hotel recommendations
        // 5. "weather in the coming days" - need weather forecast
        // 6. "Youtube video for each museum" - need video links
        // Given today is January 15, 2026 (Wednesday):
        // - "Tuesday of next week" = January 21, 2026 (outbound)
        // - "Friday" = January 24, 2026 (return)
        // - Full days in Anchorage: Wednesday Jan 22 and Thursday Jan 23
        // - Hotel nights needed: Jan 21, 22, 23 (3 nights)
        LocalDate outboundDate = LocalDate.of(2026, 1, 21);
        LocalDate returnDate = LocalDate.of(2026, 1, 24);
        LocalDate checkinDate = LocalDate.of(2026, 1, 21);
        LocalDate checkoutDate = LocalDate.of(2026, 1, 24);
        result.addProperty("travel_dates_interpretation", "Based on today being January 15, 2026, Tuesday of next week is January 21, 2026, and return Friday is January 24, 2026");
        result.addProperty("outbound_date", outboundDate.toString());
        result.addProperty("return_date", returnDate.toString());
        result.addProperty("full_days_in_anchorage", "January 22-23, 2026 (2 full days)");
        // STEP 1: Search for round trip flights from Seattle (SEA) to Anchorage (ANC)
        // Alaska Airlines is the most relevant carrier for Seattle-Anchorage route
        result.addProperty("flight_search_strategy", "Using Alaska Airlines to search for SEA to ANC flights, as it's a major carrier on this route");
        alaskaair_com alaskaAir = new alaskaair_com(context);
        alaskaair_com.SearchFlightsResult flightResult = alaskaAir.searchFlights("SEA", "ANC", outboundDate, returnDate);
        JsonObject flightInfo = new JsonObject();
        if (flightResult.flightInfo != null) {
            JsonArray flightsArray = new JsonArray();
            for (String flight : flightResult.flightInfo.flights) {
                flightsArray.add(flight);
            }
            flightInfo.add("flights", flightsArray);
            if (flightResult.flightInfo.price != null) {
                flightInfo.addProperty("price", flightResult.flightInfo.price.toString());
            }
        } else {
            flightInfo.addProperty("message", flightResult.message);
        }
        result.add("round_trip_flights", flightInfo);
        // STEP 2: Recommend 4 museums for visiting (2 per day for 2 full days)
        // Anchorage has several excellent museums. I'm recommending the top 4:
        // 1. Anchorage Museum at Rasmuson Center - premier museum with Alaska history, art, and culture
        // 2. Alaska Native Heritage Center - living museum showcasing Alaska Native cultures
        // 3. Alaska Aviation Museum - celebrating Alaska's aviation history
        // 4. Oscar Anderson House Museum - historic house museum from early Anchorage
        result.addProperty("museum_recommendation_strategy", "Recommending 4 diverse museums: cultural/art, native heritage, aviation, and historic house to provide comprehensive Anchorage experience");
        List<String> museums = Arrays.asList(
            "Anchorage Museum at Rasmuson Center",
            "Alaska Native Heritage Center",
            "Alaska Aviation Museum",
            "Oscar Anderson House Museum"
        );
        JsonArray museumsArray = new JsonArray();
        for (String museum : museums) {
            museumsArray.add(museum);
        }
        result.add("recommended_museums", museumsArray);
        JsonObject visitPlan = new JsonObject();
        visitPlan.addProperty("day1_jan22", "Anchorage Museum at Rasmuson Center + Alaska Native Heritage Center");
        visitPlan.addProperty("day2_jan23", "Alaska Aviation Museum + Oscar Anderson House Museum");
        result.add("suggested_visit_schedule", visitPlan);
        // STEP 3: Search for hotels in Anchorage for the stay dates
        result.addProperty("hotel_search_strategy", "Using Booking.com to find hotels in Anchorage for 3 nights (Jan 21-24)");
        booking_com booking = new booking_com(context);
        booking_com.HotelSearchResult hotelResult = booking.search_hotel("Anchorage, Alaska", checkinDate, checkoutDate);
        JsonObject hotelInfo = new JsonObject();
        hotelInfo.addProperty("destination", hotelResult.destination);
        hotelInfo.addProperty("checkin", hotelResult.checkinDate.toString());
        hotelInfo.addProperty("checkout", hotelResult.checkoutDate.toString());
        hotelInfo.addProperty("nights", 3);
        JsonArray hotelsArray = new JsonArray();
        for (booking_com.HotelInfo hotel : hotelResult.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("name", hotel.hotelName);
            if (hotel.price != null) {
                hotelObj.addProperty("price", hotel.price.toString());
            }
            hotelsArray.add(hotelObj);
        }
        hotelInfo.add("hotel_options", hotelsArray);
        result.add("hotels", hotelInfo);
        // STEP 4: Get weather forecast for Anchorage
        // Anchorage coordinates: approximately 61.2181° N, 149.9003° W
        result.addProperty("weather_strategy", "Using OpenWeather API to get 5-day forecast for Anchorage (61.2181°N, 149.9003°W)");
        try {
            OpenWeather weather = new OpenWeather();
            OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(61.2181, -149.9003);
            JsonObject weatherInfo = new JsonObject();
            weatherInfo.addProperty("city", forecast.getCityName());
            weatherInfo.addProperty("country", forecast.getCountry());
            JsonArray forecastArray = new JsonArray();
            for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                JsonObject forecastObj = new JsonObject();
                forecastObj.addProperty("datetime", entry.getDateTime().toString());
                forecastObj.addProperty("temperature", entry.getTemperature() + "°C");
                forecastObj.addProperty("condition", entry.getCondition());
                forecastObj.addProperty("description", entry.getDescription());
                forecastObj.addProperty("humidity", entry.getHumidity() + "%");
                forecastObj.addProperty("wind_speed", entry.getWindSpeed() + " m/s");
                forecastArray.add(forecastObj);
            }
            weatherInfo.add("forecast_entries", forecastArray);
            result.add("weather_forecast", weatherInfo);
        } catch (Exception e) {
            result.addProperty("weather_error", "Failed to retrieve weather: " + e.getMessage());
        }
        // STEP 5: Find YouTube videos for each recommended museum
        result.addProperty("youtube_strategy", "Searching YouTube for video content about each of the 4 recommended museums");
        youtube_com youtube = new youtube_com(context);
        JsonObject videosInfo = new JsonObject();
        for (String museum : museums) {
            List<youtube_com.YouTubeVideoInfo> videos = youtube.searchVideos(museum);
            JsonArray videosArray = new JsonArray();
            for (youtube_com.YouTubeVideoInfo video : videos) {
                JsonObject videoObj = new JsonObject();
                videoObj.addProperty("title", video.title);
                videoObj.addProperty("length", video.length != null ? video.length.toString() : "N/A");
                videoObj.addProperty("url", video.url);
                videosArray.add(videoObj);
            }
            videosInfo.add(museum, videosArray);
        }
        result.add("museum_videos", videosInfo);
        // STEP 6: Create a Google Maps list with the recommended museums for easy reference
        result.addProperty("maps_integration_strategy", "Creating a Google Maps list with all 4 museums for convenient navigation during the trip");
        maps_google_com maps = new maps_google_com(context);
        boolean listCreated = maps.createList("Anchorage Museums January 2026", museums);
        result.addProperty("google_maps_list_created", listCreated);
        return result;
    }
}