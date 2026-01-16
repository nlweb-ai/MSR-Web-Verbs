import java.nio.file.Paths;
import java.time.LocalDate;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;
public class Code_2026_01_12_0004 {
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
            context.close();
        }
    }
    /* Do not modify anything above this line.
       The following "automate(...)" function is the one you should modify.
       The current function body is just an example specifically about youtube.
    */
    static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        // REFINEMENT STRATEGY:
        // The task requires creating a Google Maps list and sending an itinerary via Teams.
        // All research (flights, hotel, museums, Costco) has been completed in previous rounds.
        // This round focuses on:
        // 1. Finalizing the Google Maps list with ALL required locations (airport, hotel, museums)
        // 2. Compiling a comprehensive, nicely-formatted itinerary from all known facts
        // 3. Sending the itinerary to johndoe@contoso.com via Microsoft Teams
        // Step 1: Delete any existing "Anchorage 2025" list to start fresh
        // Reasoning: Task specifies "if there is an existing list with the same name, please delete it first"
        maps_google_com mapsInstance = new maps_google_com(context);
        boolean deleteSuccess = mapsInstance.deleteList("Anchorage 2025");
        result.addProperty("existing_list_deleted", deleteSuccess);
        // Step 2: Create the Google Maps list with ALL required locations
        // Reasoning: Task requires adding "the anchorage airport, the selected hotel and the museums"
        // Based on known facts, The Voyager Inn is the selected hotel (smallest distance to museums)
        java.util.List<String> placesToAdd = java.util.Arrays.asList(
            "Ted Stevens Anchorage International Airport",  // Airport
            "The Voyager Inn, Anchorage",                  // Selected hotel
            "Anchorage Museum at Rasmuson Center",         // Museum 1
            "Alaska Native Heritage Center",                // Museum 2
            "Alaska Aviation Museum",                       // Museum 3
            "Oscar Anderson House Museum"                   // Museum 4
        );
        boolean listCreated = mapsInstance.createList("Anchorage 2025", placesToAdd);
        result.addProperty("google_maps_list_created", listCreated);
        JsonArray placesArray = new JsonArray();
        for (String place : placesToAdd) {
            placesArray.add(place);
        }
        result.add("places_in_list", placesArray);
        // Step 3: Compile the itinerary
        // Reasoning: Create a comprehensive, well-formatted itinerary from all confirmed facts
        StringBuilder itinerary = new StringBuilder();
        itinerary.append("🌟 ANCHORAGE TRIP ITINERARY 🌟\n");
        itinerary.append("4-Day Adventure | January 21-24, 2026\n");
        itinerary.append("2 Travelers | Seattle → Anchorage → Seattle\n\n");
        itinerary.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n");
        itinerary.append("✈️ FLIGHTS\n");
        itinerary.append("─────────────────────────────────────────\n");
        itinerary.append("📅 OUTBOUND - Tuesday, January 21, 2026\n");
        itinerary.append("   Alaska Airlines AS 59\n");
        itinerary.append("   SEA 7:40 AM → ANC 10:38 AM (3h 58m)\n\n");
        itinerary.append("📅 RETURN - Friday, January 24, 2026\n");
        itinerary.append("   Alaska Airlines AS 110\n");
        itinerary.append("   ANC 12:38 AM → SEA 5:12 AM (3h 34m)\n\n");
        itinerary.append("💰 Total Flight Cost: $628.70 USD\n\n");
        itinerary.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n");
        itinerary.append("🏨 ACCOMMODATION\n");
        itinerary.append("─────────────────────────────────────────\n");
        itinerary.append("Hotel: The Voyager Inn\n");
        itinerary.append("Check-in: January 21, 2026\n");
        itinerary.append("Check-out: January 24, 2026\n");
        itinerary.append("Duration: 3 nights\n");
        itinerary.append("💰 Total: $438.00 USD\n");
        itinerary.append("📍 Prime location - Minimum distance to all museums (13.7 miles total)\n\n");
        itinerary.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n");
        itinerary.append("🗓️ DAILY ITINERARY\n");
        itinerary.append("─────────────────────────────────────────\n\n");
        itinerary.append("📅 DAY 1 - Tuesday, January 21, 2026\n");
        itinerary.append("   • Arrive ANC 10:38 AM\n");
        itinerary.append("   • Check in to The Voyager Inn\n");
        itinerary.append("   • Settle in and explore downtown Anchorage\n\n");
        itinerary.append("📅 DAY 2 - Wednesday, January 22, 2026\n");
        itinerary.append("   Morning:\n");
        itinerary.append("   🏛️ Anchorage Museum at Rasmuson Center (0.6 mi from hotel)\n");
        itinerary.append("      Alaska's premier art, history & science museum\n\n");
        itinerary.append("   Afternoon:\n");
        itinerary.append("   🏛️ Alaska Native Heritage Center (7.2 mi from hotel)\n");
        itinerary.append("      Explore indigenous cultures & traditional dwellings\n\n");
        itinerary.append("📅 DAY 3 - Thursday, January 23, 2026\n");
        itinerary.append("   Morning:\n");
        itinerary.append("   ✈️ Alaska Aviation Museum (5.7 mi from hotel)\n");
        itinerary.append("      Historic aircraft & Alaska aviation history\n\n");
        itinerary.append("   Afternoon:\n");
        itinerary.append("   🏠 Oscar Anderson House Museum (0.2 mi from hotel)\n");
        itinerary.append("      Historic home tour (shortest distance!)\n\n");
        itinerary.append("   Evening:\n");
        itinerary.append("   🛒 Costco Anchorage - Kids Winter Jackets Shopping\n");
        itinerary.append("      Available options:\n");
        itinerary.append("      • Snozu Kids' Jacket - $14.97\n");
        itinerary.append("      • Mondetta Youth Quilted Jacket - $21.99\n");
        itinerary.append("      • Carter's Kids' Jacket - $15.99\n");
        itinerary.append("      • Character Kids' Plush Hoodie - $16.99\n\n");
        itinerary.append("📅 DAY 4 - Friday, January 24, 2026\n");
        itinerary.append("   • Depart hotel early for 12:38 AM flight\n");
        itinerary.append("   • Arrive SEA 5:12 AM\n\n");
        itinerary.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n");
        itinerary.append("💵 COST SUMMARY\n");
        itinerary.append("─────────────────────────────────────────\n");
        itinerary.append("Flights:        $628.70\n");
        itinerary.append("Hotel:          $438.00\n");
        itinerary.append("────────────────────────\n");
        itinerary.append("TOTAL:         $1,066.70 USD\n");
        itinerary.append("(Plus museums, meals, shopping)\n\n");
        itinerary.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n");
        itinerary.append("📍 GOOGLE MAPS LIST\n");
        itinerary.append("─────────────────────────────────────────\n");
        itinerary.append("List Name: \"Anchorage 2025\"\n");
        itinerary.append("Includes: Airport, Hotel & All 4 Museums\n");
        itinerary.append("Ready for easy navigation! 🗺️\n\n");
        itinerary.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n");
        itinerary.append("❄️ WEATHER TIPS\n");
        itinerary.append("Expected conditions: Winter/Snow likely\n");
        itinerary.append("Pack warm clothing and winter gear!\n\n");
        itinerary.append("Safe travels! 🎉");
        String itineraryText = itinerary.toString();
        // Step 4: Send itinerary via Microsoft Teams
        // Reasoning: Task specifies "send it to johndoe@contoso.com using Microsoft Teams"
        teams_microsoft_com teamsInstance = new teams_microsoft_com(context);
        teams_microsoft_com.MessageStatus messageStatus = teamsInstance.sendMessage(
            "johndoe@contoso.com",
            itineraryText
        );
        result.addProperty("itinerary_sent_to", messageStatus.recipientEmail);
        result.addProperty("teams_send_status", messageStatus.status);
        result.addProperty("itinerary_preview", itineraryText.substring(0, Math.min(200, itineraryText.length())) + "...");
        // Step 5: Document the refinement strategy and outcomes
        result.addProperty("refinement_round", 4);
        result.addProperty("refinement_focus", "Finalized Google Maps list creation and sent comprehensive itinerary via Teams");
        result.addProperty("google_maps_list_name", "Anchorage 2025");
        result.addProperty("places_added_count", placesToAdd.size());
        result.addProperty("reasoning", "This round completes the task by: (1) ensuring Google Maps list includes ALL required locations per task spec (airport + hotel + museums), (2) compiling all confirmed facts from previous rounds into a well-formatted itinerary, and (3) delivering it to the specified recipient via Microsoft Teams");
        return result;
    }
}