import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class AnchorageTask0002 {
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
       The current function body is the refinement for the hotel selection based on distance to museums.
    */
    static JsonObject automate(BrowserContext context) {
        
        // Strategy: The task mentions wanting to select the hotel with the smallest total distance to all museums.
        // We need to get the exact addresses of museums and hotels, then calculate distances.
        // This will help the user make an informed decision about hotel selection.
        
        maps_google_com mapsInstance = new maps_google_com(context);
        NLWeb nlwebInstance = new NLWeb();
        
        JsonObject finalResult = new JsonObject();
        JsonArray factsCollected = new JsonArray();
        
        // List of museums from the known facts
        java.util.List<String> museums = java.util.Arrays.asList(
            "Anchorage Museum at Rasmuson Center, Anchorage, Alaska",
            "Alaska Native Heritage Center, Anchorage, Alaska", 
            "Alaska Aviation Museum, Anchorage, Alaska",
            "Alaska Zoo, Anchorage, Alaska",
            "Alaska Veterans Museum, Anchorage, Alaska",
            "Oscar Anderson House Museum, Anchorage, Alaska"
        );
        
        // List of hotels from the known facts
        java.util.List<String> hotels = java.util.Arrays.asList(
            "The Wildbirch Hotel - JdV by Hyatt, Anchorage, Alaska",
            "Qupqugiaq Inn, Anchorage, Alaska",
            "Luxury DT Cottage - Free Parking - Self Check-In, Anchorage, Alaska", 
            "Clarion Suites Anchorage Downtown, Anchorage, Alaska",
            "Comfort Suites Anchorage International Airport, Anchorage, Alaska"
        );
        
        try {
            // Step 1: Get exact addresses for museums using NLWeb
            String museumQuery = "What are the exact street addresses of these museums in Anchorage, Alaska: " +
                "Anchorage Museum at Rasmuson Center, Alaska Native Heritage Center, Alaska Aviation Museum, " +
                "Alaska Zoo, Alaska Veterans Museum, Oscar Anderson House Museum";
            
            String museumResponse = nlwebInstance.AskNLWeb(museumQuery);
            
            JsonObject museumFact = new JsonObject();
            museumFact.addProperty("type", "museum_addresses");
            museumFact.addProperty("query", museumQuery);
            museumFact.addProperty("addresses", museumResponse);
            factsCollected.add(museumFact);
            
            // Step 2: Get exact addresses for hotels using NLWeb
            String hotelQuery = "What are the exact street addresses of these hotels in Anchorage, Alaska: " +
                "The Wildbirch Hotel - JdV by Hyatt, Qupqugiaq Inn, Luxury DT Cottage - Free Parking - Self Check-In, " +
                "Clarion Suites Anchorage Downtown, Comfort Suites Anchorage International Airport";
            
            String hotelResponse = nlwebInstance.AskNLWeb(hotelQuery);
            
            JsonObject hotelFact = new JsonObject();
            hotelFact.addProperty("type", "hotel_addresses");
            hotelFact.addProperty("query", hotelQuery);
            hotelFact.addProperty("addresses", hotelResponse);
            factsCollected.add(hotelFact);
            
            // Step 3: Calculate distances from each hotel to each museum using Google Maps
            JsonArray distanceCalculations = new JsonArray();
            
            for (String hotel : hotels) {
                JsonObject hotelDistances = new JsonObject();
                hotelDistances.addProperty("hotel", hotel);
                JsonArray museumDistances = new JsonArray();
                double totalDistance = 0.0;
                boolean allDistancesCalculated = true;
                
                for (String museum : museums) {
                    try {
                        // Get direction and distance from hotel to museum
                        maps_google_com.DirectionResult direction = mapsInstance.get_direction(hotel, museum);
                        
                        JsonObject distanceInfo = new JsonObject();
                        distanceInfo.addProperty("museum", museum);
                        distanceInfo.addProperty("distance", direction.distance);
                        distanceInfo.addProperty("travel_time", direction.travelTime);
                        distanceInfo.addProperty("route", direction.route);
                        
                        // Extract numeric distance for total calculation (assuming format like "5.2 mi")
                        try {
                            String distanceStr = direction.distance.replaceAll("[^0-9.]", "");
                            if (!distanceStr.isEmpty()) {
                                totalDistance += Double.parseDouble(distanceStr);
                            }
                        } catch (NumberFormatException e) {
                            allDistancesCalculated = false;
                        }
                        
                        museumDistances.add(distanceInfo);
                    } catch (Exception e) {
                        allDistancesCalculated = false;
                        JsonObject errorInfo = new JsonObject();
                        errorInfo.addProperty("museum", museum);
                        errorInfo.addProperty("error", "Could not calculate distance: " + e.getMessage());
                        museumDistances.add(errorInfo);
                    }
                }
                
                hotelDistances.add("museum_distances", museumDistances);
                if (allDistancesCalculated) {
                    hotelDistances.addProperty("total_distance_miles", totalDistance);
                }
                distanceCalculations.add(hotelDistances);
            }
            
            JsonObject distanceFact = new JsonObject();
            distanceFact.addProperty("type", "hotel_museum_distances");
            distanceFact.addProperty("description", "Distance calculations from each hotel to all museums");
            distanceFact.add("distance_data", distanceCalculations);
            factsCollected.add(distanceFact);
            
            // Step 4: Use NLWeb to get recommendations for ideal hotel location
            String locationQuery = "Based on visiting museums in Anchorage Alaska (Anchorage Museum at Rasmuson Center, " +
                "Alaska Native Heritage Center, Alaska Aviation Museum, Alaska Zoo, Alaska Veterans Museum, " +
                "Oscar Anderson House Museum), which area or neighborhood in Anchorage would be the best central location " +
                "to stay to minimize travel time to all these attractions?";
            
            String locationResponse = nlwebInstance.AskNLWeb(locationQuery);
            
            JsonObject locationFact = new JsonObject();
            locationFact.addProperty("type", "optimal_hotel_location");
            locationFact.addProperty("query", locationQuery);
            locationFact.addProperty("recommendation", locationResponse);
            factsCollected.add(locationFact);
            
            finalResult.addProperty("refinement_focus", "Hotel selection based on proximity to museums");
            finalResult.addProperty("museums_count", museums.size());
            finalResult.addProperty("hotels_count", hotels.size());
            finalResult.add("facts_collected", factsCollected);
            
            // Append to known_facts.md
            appendToKnownFacts(factsCollected);
            
        } catch (Exception e) {
            JsonObject errorResult = new JsonObject();
            errorResult.addProperty("error", "Failed to complete hotel distance analysis: " + e.getMessage());
            finalResult.add("error_details", errorResult);
        }
        
        return finalResult;
    }
    
    private static void appendToKnownFacts(JsonArray facts) {
        try {
            String factsPath = "tasks\\2025-08-27\\known_facts.md";
            String timestamp = java.time.LocalDateTime.now().toString();
            
            StringBuilder content = new StringBuilder();
            content.append("\n\n## Facts collected on ").append(timestamp).append("\n");
            content.append("### Hotel Distance Analysis for Museum Visits\n\n");
            
            Gson gson = new GsonBuilder()
                .disableHtmlEscaping()
                .setPrettyPrinting()
                .create();
            
            for (int i = 0; i < facts.size(); i++) {
                content.append("```json\n");
                content.append(gson.toJson(facts.get(i)));
                content.append("\n```\n\n");
            }
            
            Files.write(Paths.get(factsPath), content.toString().getBytes(StandardCharsets.UTF_8), 
                       StandardOpenOption.CREATE, StandardOpenOption.APPEND);
                       
        } catch (IOException e) {
            System.err.println("Failed to append to known_facts.md: " + e.getMessage());
        }
    }
}
