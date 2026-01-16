import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Test {
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
        JsonObject result = new JsonObject();
        
        // Test maps_google_com functions
        maps_google_com mapsInstance = new maps_google_com(context);
        
        // Test 1: Get directions
        // maps_google_com.DirectionResult directions = mapsInstance.get_direction(
        //     "Seattle, WA",
        //     "Anchorage, AK"
        // );
        
        // JsonObject directionsObj = new JsonObject();
        // directionsObj.addProperty("travelTime", directions.travelTime);
        // directionsObj.addProperty("distance", directions.distance);
        // directionsObj.addProperty("route", directions.route);
        // result.add("directions", directionsObj);
        
        // Test 2: Get nearest businesses (museums in Anchorage)
        maps_google_com.NearestBusinessesResult businesses = mapsInstance.get_nearestBusinesses(
            "Anchorage, AK",
            "museum",
            5
        );
        
        JsonObject businessesObj = new JsonObject();
        businessesObj.addProperty("referencePoint", businesses.referencePoint);
        businessesObj.addProperty("businessDescription", businesses.businessDescription);
        businessesObj.addProperty("count", businesses.businesses.size());
        
        com.google.gson.JsonArray businessArray = new com.google.gson.JsonArray();
        for (maps_google_com.BusinessInfo business : businesses.businesses) {
            JsonObject bizObj = new JsonObject();
            bizObj.addProperty("name", business.name);
            bizObj.addProperty("address", business.address);
            businessArray.add(bizObj);
        }
        businessesObj.add("businesses", businessArray);
        result.add("nearestBusinesses", businessesObj);
        
        return result;
    }
}