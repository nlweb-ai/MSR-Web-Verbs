import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0025 {
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
        JsonObject finalResult = new JsonObject();
        
        // Step 1: Find rental cabin for 5 people in Denver using Redfin
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult cabinSearch = redfin.searchApartments("Denver, CO", 1000, 3000);
        
        JsonArray cabinsArray = new JsonArray();
        if (cabinSearch.apartments != null && !cabinSearch.apartments.isEmpty()) {
            for (redfin_com.ApartmentInfo cabin : cabinSearch.apartments) {
                JsonObject cabinObj = new JsonObject();
                cabinObj.addProperty("address", cabin.address);
                cabinObj.addProperty("price", cabin.price.amount);
                cabinObj.addProperty("currency", cabin.price.currency);
                cabinObj.addProperty("url", cabin.url);
                cabinsArray.add(cabinObj);
            }
        }
        finalResult.add("rental_cabins", cabinsArray);
        if (cabinSearch.error != null) {
            finalResult.addProperty("cabin_search_error", cabinSearch.error);
        }
        
        // Step 2: Search for healthy breakfast options using Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult breakfastSearch = costco.searchProducts("healthy breakfast organic");
        
        JsonArray breakfastArray = new JsonArray();
        if (breakfastSearch.products != null && !breakfastSearch.products.isEmpty()) {
            for (costco_com.ProductInfo product : breakfastSearch.products) {
                JsonObject breakfastObj = new JsonObject();
                breakfastObj.addProperty("product_name", product.productName);
                if (product.productPrice != null) {
                    breakfastObj.addProperty("price", product.productPrice.amount);
                    breakfastObj.addProperty("currency", product.productPrice.currency);
                }
                if (product.error != null) {
                    breakfastObj.addProperty("error", product.error);
                }
                breakfastArray.add(breakfastObj);
            }
        }
        finalResult.add("breakfast_options", breakfastArray);
        if (breakfastSearch.error != null) {
            finalResult.addProperty("breakfast_search_error", breakfastSearch.error);
        }
        
        // Step 3: Check flight prices from Dallas to Denver using Alaska Airlines
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 18); // August 18, 2025
        LocalDate returnDate = LocalDate.of(2025, 8, 20);   // August 20, 2025
        alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("DFW", "DEN", outboundDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        if (flightSearch.flightInfo != null) {
            JsonArray flightsArray = new JsonArray();
            if (flightSearch.flightInfo.flights != null) {
                for (String flight : flightSearch.flightInfo.flights) {
                    flightsArray.add(flight);
                }
            }
            flightInfo.add("flights", flightsArray);
            if (flightSearch.flightInfo.price != null) {
                flightInfo.addProperty("price", flightSearch.flightInfo.price.amount);
                flightInfo.addProperty("currency", flightSearch.flightInfo.price.currency);
            }
        }
        if (flightSearch.message != null) {
            flightInfo.addProperty("message", flightSearch.message);
        }
        finalResult.add("flight_options", flightInfo);
        
        // Step 4: Find hiking trails near Denver using Google Maps
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult trailSearch = maps.get_nearestBusinesses("Denver, CO", "hiking trails nature", 10);
        
        JsonArray trailsArray = new JsonArray();
        if (trailSearch.businesses != null && !trailSearch.businesses.isEmpty()) {
            for (maps_google_com.BusinessInfo trail : trailSearch.businesses) {
                JsonObject trailObj = new JsonObject();
                trailObj.addProperty("name", trail.name);
                trailObj.addProperty("address", trail.address);
                trailsArray.add(trailObj);
            }
        }
        finalResult.add("hiking_trails", trailsArray);
        
        // Step 5: Compare options and create summary
        JsonObject summary = new JsonObject();
        
        // Calculate total estimated costs
        double totalCabinCost = 0;
        double totalBreakfastCost = 0;
        
        if (cabinSearch.apartments != null && !cabinSearch.apartments.isEmpty()) {
            // Assume first cabin option for calculation (3 nights)
            totalCabinCost = cabinSearch.apartments.get(0).price.amount * 3;
            summary.addProperty("selected_cabin", cabinSearch.apartments.get(0).address);
            summary.addProperty("cabin_cost", totalCabinCost);
        }
        
        if (breakfastSearch.products != null && !breakfastSearch.products.isEmpty()) {
            // Estimate breakfast for 5 people for 3 days
            totalBreakfastCost = breakfastSearch.products.get(0).productPrice != null ? 
                breakfastSearch.products.get(0).productPrice.amount * 2 : 0; // Assuming 2 packages needed
            summary.addProperty("selected_breakfast", breakfastSearch.products.get(0).productName);
            summary.addProperty("breakfast_cost", totalBreakfastCost);
        }
        
        if (trailSearch.businesses != null && !trailSearch.businesses.isEmpty()) {
            summary.addProperty("recommended_trail", trailSearch.businesses.get(0).name);
            summary.addProperty("trail_location", trailSearch.businesses.get(0).address);
        }
        
        summary.addProperty("total_estimated_cost", totalCabinCost + totalBreakfastCost);
        summary.addProperty("retreat_dates", "August 18-20, 2025");
        summary.addProperty("location", "Denver, CO");
        summary.addProperty("participants", 5);
        summary.addProperty("event_type", "Research Retreat");
        
        finalResult.add("retreat_summary", summary);
        
        return finalResult;
    }
}
