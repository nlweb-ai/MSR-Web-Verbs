import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
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


public class AnchorageTask0001 {
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
                    //"--no-sandbox",
                    //"--disable-web-security",
                    "--disable-infobars",
                    "--disable-extensions",
                    "--start-maximized"
                ));

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
        // Refinement Strategy: Concretize the Anchorage travel plan by:
        // 1. Converting relative dates to specific dates (Tuesday next week = Sept 2, Friday = Sept 5)
        // 2. Getting museum recommendations using NLWeb API
        // 3. Searching for round trip flights SEA->ANC using Alaska Airlines
        // 4. Finding hotel options using Booking.com
        // 5. Getting weather forecast for travel dates
        // 6. Finding YouTube videos for each recommended museum
        
        JsonObject result = new JsonObject();
        JsonArray collectedFacts = new JsonArray();
        
        // Step 1: Concretize travel dates
        // Today is August 29, 2025 (Friday)
        // "Tuesday of the next week" = September 2, 2025
        // "Friday" (return) = September 5, 2025
        LocalDate departureDate = LocalDate.of(2025, 9, 2);
        LocalDate returnDate = LocalDate.of(2025, 9, 5);
        
        JsonObject datesFact = new JsonObject();
        datesFact.addProperty("type", "travel_dates");
        datesFact.addProperty("departure_date", "September 2, 2025 (Tuesday)");
        datesFact.addProperty("return_date", "September 5, 2025 (Friday)");
        datesFact.addProperty("nights_in_anchorage", 3);
        collectedFacts.add(datesFact);
        
        // Step 2: Get museum recommendations using NLWeb
        NLWeb nlweb = new NLWeb();
        String museumQuery = "I am traveling to Anchorage, Alaska for 3 days. Can you recommend 6 good museums to visit? I want to visit 2 museums per full day.";
        String museumRecommendations = null;
        try {
            museumRecommendations = nlweb.AskNLWeb(museumQuery);
        } catch (Exception e) {
            System.err.println("Error getting museum recommendations: " + e.getMessage());
        }
        
        JsonObject museumFact = new JsonObject();
        museumFact.addProperty("type", "museum_recommendations");
        museumFact.addProperty("query", museumQuery);
        museumFact.addProperty("recommendations", museumRecommendations);
        collectedFacts.add(museumFact);
        
        // Step 3: Search for flights using Alaska Airlines
        alaskaair_com alaskaAir = new alaskaair_com(context);
        // SEA = Seattle-Tacoma International Airport
        // ANC = Ted Stevens Anchorage International Airport
        alaskaair_com.SearchFlightsResult flightResult = alaskaAir.searchFlights("SEA", "ANC", departureDate, returnDate);
        
        JsonObject flightFact = new JsonObject();
        flightFact.addProperty("type", "flight_search");
        flightFact.addProperty("origin", "SEA (Seattle)");
        flightFact.addProperty("destination", "ANC (Anchorage)");
        flightFact.addProperty("outbound_date", departureDate.toString());
        flightFact.addProperty("return_date", returnDate.toString());
        if (flightResult.message != null) {
            flightFact.addProperty("message", flightResult.message);
        }
        if (flightResult.flightInfo != null) {
            flightFact.addProperty("flights_found", flightResult.flightInfo.flights.toString());
            if (flightResult.flightInfo.price != null) {
                flightFact.addProperty("price", flightResult.flightInfo.price.toString());
            }
        }
        collectedFacts.add(flightFact);
        
        // Step 4: Search for hotels using Booking.com
        booking_com booking = new booking_com(context);
        // Check-in Sept 2, Check-out Sept 5
        booking_com.HotelSearchResult hotelResult = booking.search_hotel("Anchorage, Alaska", departureDate, returnDate);
        
        JsonObject hotelFact = new JsonObject();
        hotelFact.addProperty("type", "hotel_search");
        hotelFact.addProperty("destination", hotelResult.destination);
        hotelFact.addProperty("checkin_date", hotelResult.checkinDate.toString());
        hotelFact.addProperty("checkout_date", hotelResult.checkoutDate.toString());
        hotelFact.addProperty("hotels_found", hotelResult.hotels.size());
        
        JsonArray hotelArray = new JsonArray();
        for (booking_com.HotelInfo hotel : hotelResult.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("name", hotel.hotelName);
            if (hotel.price != null) {
                hotelObj.addProperty("price", hotel.price.toString());
            }
            hotelArray.add(hotelObj);
        }
        hotelFact.add("hotel_options", hotelArray);
        collectedFacts.add(hotelFact);
        
        // Step 5: Get weather forecast for Anchorage
        OpenWeather weather = new OpenWeather();
        JsonObject weatherFact = new JsonObject();
        weatherFact.addProperty("type", "weather_forecast");
        
        try {
            // First get Anchorage coordinates using geocoding
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Anchorage,AK,US");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData anchorage = locations.get(0);
                weatherFact.addProperty("city", anchorage.getName());
                weatherFact.addProperty("state", anchorage.getState());
                weatherFact.addProperty("country", anchorage.getCountry());
                weatherFact.addProperty("latitude", anchorage.getLatitude());
                weatherFact.addProperty("longitude", anchorage.getLongitude());
                
                // Get 5-day forecast using coordinates
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(anchorage.getLatitude(), anchorage.getLongitude());
                
                JsonArray forecastArray = new JsonArray();
                for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                    // Filter for the travel dates (Sept 2-5)
                    if (entry.getDateTime().toLocalDate().isAfter(departureDate.minusDays(1)) && 
                        entry.getDateTime().toLocalDate().isBefore(returnDate.plusDays(1))) {
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
                }
                weatherFact.add("forecast_for_travel_dates", forecastArray);
            } else {
                weatherFact.addProperty("error", "Could not find location data for Anchorage, AK");
            }
        } catch (IOException | InterruptedException e) {
            weatherFact.addProperty("error", "Failed to get weather forecast: " + e.getMessage());
        }
        collectedFacts.add(weatherFact);
        
        // Step 6: Find YouTube videos for recommended museums
        youtube_com youtube = new youtube_com(context);
        
        // Parse museum recommendations and search for videos
        if (museumRecommendations != null && !museumRecommendations.isEmpty()) {
            try {
                Gson gson = new Gson();
                JsonObject museums = gson.fromJson(museumRecommendations, JsonObject.class);
                
                JsonArray videoFacts = new JsonArray();
                for (String key : museums.keySet()) {
                    String museumName = museums.get(key).getAsString();
                    String videoQuery = museumName + " Anchorage Alaska tour virtual visit";
                    
                    List<youtube_com.YouTubeVideoInfo> videos = youtube.searchVideos(videoQuery);
                    
                    JsonObject videoFact = new JsonObject();
                    videoFact.addProperty("type", "museum_video");
                    videoFact.addProperty("museum_name", museumName);
                    videoFact.addProperty("search_query", videoQuery);
                    
                    JsonArray videoArray = new JsonArray();
                    for (youtube_com.YouTubeVideoInfo video : videos) {
                        JsonObject videoObj = new JsonObject();
                        videoObj.addProperty("title", video.title);
                        videoObj.addProperty("url", video.url);
                        videoObj.addProperty("duration", video.length.toString());
                        videoArray.add(videoObj);
                    }
                    videoFact.add("videos", videoArray);
                    videoFacts.add(videoFact);
                }
                collectedFacts.add(videoFacts);
            } catch (com.google.gson.JsonSyntaxException e) {
                JsonObject errorFact = new JsonObject();
                errorFact.addProperty("type", "error");
                errorFact.addProperty("message", "Failed to parse museum recommendations for video search: " + e.getMessage());
                collectedFacts.add(errorFact);
            }
        }
        
        // Step 7: Append collected facts to known_facts.md
        try (FileWriter fw = new FileWriter("tasks\\2025-08-27\\known_facts.md", true);
             PrintWriter pw = new PrintWriter(fw)) {
            
            pw.println("\n## Facts collected on " + java.time.LocalDateTime.now().toString());
            pw.println("### Travel Planning for Anchorage Trip");
            
            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            for (int i = 0; i < collectedFacts.size(); i++) {
                pw.println("\n```json");
                pw.println(gson.toJson(collectedFacts.get(i)));
                pw.println("```");
            }
            
        } catch (IOException e) {
            System.err.println("Error writing to known_facts.md: " + e.getMessage());
        }
        
        // Prepare final result
        result.add("collected_facts", collectedFacts);
        result.addProperty("status", "completed");
        result.addProperty("refinement_strategy", "Concretized travel dates, gathered museum recommendations, searched flights and hotels, obtained weather forecast, and found YouTube videos for museums");
        
        return result;
    }
}
