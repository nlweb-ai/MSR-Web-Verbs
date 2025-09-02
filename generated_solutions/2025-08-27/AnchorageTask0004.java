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


public class AnchorageTask0004 {
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
       The current function body addresses creating a Google Maps list and sending an itinerary via Teams.
    */
    static JsonObject automate(BrowserContext context) {
        
        // Strategy: The task has two new concrete requirements:
        // 1. Create a Google Maps list named "Anchorage 2025" with airport, hotel, and museums
        // 2. Compose and send a formatted itinerary to johndoe@contoso.com via Microsoft Teams
        // These actions will help organize the trip locations and communicate the final plan.
        
        maps_google_com mapsInstance = new maps_google_com(context);
        teams_microsoft_com teamsInstance = new teams_microsoft_com(context);
        
        JsonObject finalResult = new JsonObject();
        JsonArray factsCollected = new JsonArray();
        
        try {
            // Step 1: Delete existing "Anchorage 2025" list if it exists
            boolean deleteResult = mapsInstance.deleteList("Anchorage 2025");
            
            JsonObject deleteFact = new JsonObject();
            deleteFact.addProperty("type", "maps_list_cleanup");
            deleteFact.addProperty("list_name", "Anchorage 2025");
            deleteFact.addProperty("delete_success", deleteResult);
            factsCollected.add(deleteFact);
            
            // Step 2: Create list of places to add to Google Maps
            java.util.List<String> places = java.util.Arrays.asList(
                "Ted Stevens Anchorage International Airport, Anchorage, AK",
                "The Wildbirch Hotel - JdV by Hyatt, Anchorage, AK", 
                "Anchorage Museum at Rasmuson Center, Anchorage, AK",
                "Alaska Native Heritage Center, Anchorage, AK",
                "Alaska Aviation Museum, Anchorage, AK",
                "Alaska Zoo, Anchorage, AK",
                "Alaska Veterans Museum, Anchorage, AK",
                "Oscar Anderson House Museum, Anchorage, AK"
            );
            
            // Step 3: Create the new Google Maps list
            boolean createResult = mapsInstance.createList("Anchorage 2025", places);
            
            JsonObject createFact = new JsonObject();
            createFact.addProperty("type", "maps_list_creation");
            createFact.addProperty("list_name", "Anchorage 2025");
            createFact.addProperty("create_success", createResult);
            createFact.addProperty("places_count", places.size());
            
            JsonArray placesArray = new JsonArray();
            for (String place : places) {
                placesArray.add(place);
            }
            createFact.add("places_added", placesArray);
            factsCollected.add(createFact);
            
            // Step 4: Compose a nicely formatted itinerary
            StringBuilder itinerary = new StringBuilder();
            itinerary.append("🗓️ **ANCHORAGE ALASKA TRIP ITINERARY**\n");
            itinerary.append("📅 **September 2-5, 2025** | 3 nights, 4 days\n\n");
            
            itinerary.append("✈️ **FLIGHT DETAILS**\n");
            itinerary.append("• Outbound: AS 173, Sep 2 (Tue), Seattle → Anchorage, 3h 45m\n");
            itinerary.append("• Return: AS 148, Sep 5 (Fri), Anchorage → Seattle, 3h 32m\n");
            itinerary.append("• Total Cost: $657.90 USD\n\n");
            
            itinerary.append("🏨 **ACCOMMODATION**\n");
            itinerary.append("• The Wildbirch Hotel - JdV by Hyatt\n");
            itinerary.append("• Downtown Anchorage (optimal location for museums)\n");
            itinerary.append("• 3 nights: $922.00 USD\n");
            itinerary.append("• Walking distance to 3 museums!\n\n");
            
            itinerary.append("🏛️ **MUSEUM VISITS** (2 per day)\n");
            itinerary.append("**Day 1 (Sep 2):** Arrival day - light activities\n");
            itinerary.append("**Day 2 (Sep 3):**\n");
            itinerary.append("• Morning: Anchorage Museum at Rasmuson Center (0.3 mi walk)\n");
            itinerary.append("• Afternoon: Alaska Veterans Museum (0.1 mi walk)\n\n");
            itinerary.append("**Day 3 (Sep 4):**\n");
            itinerary.append("• Morning: Alaska Native Heritage Center (6.8 mi drive)\n");
            itinerary.append("• Afternoon: Alaska Aviation Museum (6.6 mi drive)\n\n");
            itinerary.append("**Day 4 (Sep 5):**\n");
            itinerary.append("• Morning: Oscar Anderson House Museum (0.8 mi walk)\n");
            itinerary.append("• Early afternoon: Alaska Zoo (9.6 mi drive) - before departure\n\n");
            
            itinerary.append("🛍️ **SHOPPING**\n");
            itinerary.append("• Costco Anchorage: Kids winter jackets available\n");
            itinerary.append("• Best options: Lands' End ($11.99), Gerry ($17.99), Eddie Bauer ($18.99)\n");
            itinerary.append("• Recommended gear: base layers, fleece, waterproof outer layer\n\n");
            
            itinerary.append("🗺️ **GOOGLE MAPS**\n");
            itinerary.append("• Custom list created: \"Anchorage 2025\"\n");
            itinerary.append("• Includes: airport, hotel, all 6 museums\n");
            itinerary.append("• Easy navigation for the entire trip!\n\n");
            
            itinerary.append("💰 **ESTIMATED COSTS**\n");
            itinerary.append("• Flights: $657.90\n");
            itinerary.append("• Hotel: $922.00\n");
            itinerary.append("• Kids jackets: ~$30-40\n");
            itinerary.append("• **Base Total: ~$1,610 USD**\n");
            itinerary.append("(excludes meals, activities, other shopping)\n\n");
            
            itinerary.append("🌟 **TRIP HIGHLIGHTS**\n");
            itinerary.append("• Perfect downtown location with walking access to 3 museums\n");
            itinerary.append("• Comprehensive winter clothing shopping at Costco\n");
            itinerary.append("• Efficient museum routing saves time and gas\n");
            itinerary.append("• YouTube videos available for all museums for pre-trip planning\n\n");
            
            itinerary.append("Have an amazing trip to Alaska! 🐻❄️🏔️");
            
            // Step 5: Send the itinerary via Microsoft Teams
            teams_microsoft_com.MessageStatus messageStatus = teamsInstance.sendMessage(
                "johndoe@contoso.com", 
                itinerary.toString()
            );
            
            JsonObject messagesFact = new JsonObject();
            messagesFact.addProperty("type", "teams_itinerary_sent");
            messagesFact.addProperty("recipient", "johndoe@contoso.com");
            messagesFact.addProperty("message_status", messageStatus.toString());
            messagesFact.addProperty("message_length", itinerary.length());
            messagesFact.addProperty("content_preview", itinerary.substring(0, Math.min(200, itinerary.length())) + "...");
            factsCollected.add(messagesFact);
            
            finalResult.addProperty("refinement_focus", "Google Maps list creation and Teams itinerary sharing");
            finalResult.addProperty("maps_list_created", createResult);
            finalResult.addProperty("teams_message_sent", messageStatus.toString());
            finalResult.add("facts_collected", factsCollected);
            
            // Append to known_facts.md
            appendToKnownFacts(factsCollected);
            
        } catch (Exception e) {
            JsonObject errorResult = new JsonObject();
            errorResult.addProperty("error", "Failed to complete Maps list and Teams messaging: " + e.getMessage());
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
            content.append("### Google Maps List and Teams Itinerary Sharing\n\n");
            
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
