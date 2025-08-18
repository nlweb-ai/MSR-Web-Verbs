import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0022 {
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
        
        // Step 1: Find large house rental in Chicago with 4+ bedrooms using Redfin
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult houseSearch = redfin.searchApartments("Chicago, IL", 2000, 8000);
        
        JsonArray housesArray = new JsonArray();
        if (houseSearch.apartments != null && !houseSearch.apartments.isEmpty()) {
            for (redfin_com.ApartmentInfo apartment : houseSearch.apartments) {
                JsonObject houseObj = new JsonObject();
                houseObj.addProperty("address", apartment.address);
                houseObj.addProperty("price", apartment.price.amount);
                houseObj.addProperty("currency", apartment.price.currency);
                houseObj.addProperty("url", apartment.url);
                housesArray.add(houseObj);
            }
        }
        finalResult.add("house_rentals", housesArray);
        if (houseSearch.error != null) {
            finalResult.addProperty("house_search_error", houseSearch.error);
        }
        
        // Step 2: Search for catering options for 20 people using Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult cateringSearch = costco.searchProducts("catering party platters");
        
        JsonArray cateringArray = new JsonArray();
        if (cateringSearch.products != null && !cateringSearch.products.isEmpty()) {
            for (costco_com.ProductInfo product : cateringSearch.products) {
                JsonObject cateringObj = new JsonObject();
                cateringObj.addProperty("product_name", product.productName);
                if (product.productPrice != null) {
                    cateringObj.addProperty("price", product.productPrice.amount);
                    cateringObj.addProperty("currency", product.productPrice.currency);
                }
                if (product.error != null) {
                    cateringObj.addProperty("error", product.error);
                }
                cateringArray.add(cateringObj);
            }
        }
        finalResult.add("catering_options", cateringArray);
        if (cateringSearch.error != null) {
            finalResult.addProperty("catering_search_error", cateringSearch.error);
        }
        
        // Step 3: Find nearby parks in Chicago using Google Maps
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult parksSearch = maps.get_nearestBusinesses("Chicago, IL", "parks recreation", 10);
        
        JsonArray parksArray = new JsonArray();
        if (parksSearch.businesses != null && !parksSearch.businesses.isEmpty()) {
            for (maps_google_com.BusinessInfo park : parksSearch.businesses) {
                JsonObject parkObj = new JsonObject();
                parkObj.addProperty("name", park.name);
                parkObj.addProperty("address", park.address);
                parksArray.add(parkObj);
            }
        }
        finalResult.add("nearby_parks", parksArray);
        
        // Step 4: Check flight options from New York to Chicago using Alaska Airlines
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 17); // August 17, 2025
        LocalDate returnDate = LocalDate.of(2025, 8, 19);   // Return 2 days later
        alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("JFK", "ORD", outboundDate, returnDate);
        
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
        
        // Step 5: Calculate best combination and summarize
        JsonObject summary = new JsonObject();
        
        // Calculate total estimated costs
        double totalHouseCost = 0;
        double totalCateringCost = 0;
        
        if (houseSearch.apartments != null && !houseSearch.apartments.isEmpty()) {
            // Assume first house option for calculation
            totalHouseCost = houseSearch.apartments.get(0).price.amount;
            summary.addProperty("selected_house", houseSearch.apartments.get(0).address);
            summary.addProperty("house_cost", totalHouseCost);
        }
        
        if (cateringSearch.products != null && !cateringSearch.products.isEmpty()) {
            // Estimate catering for 20 people (multiply by quantity needed)
            totalCateringCost = cateringSearch.products.get(0).productPrice != null ? 
                cateringSearch.products.get(0).productPrice.amount * 2 : 0; // Assuming 2 platters needed
            summary.addProperty("selected_catering", cateringSearch.products.get(0).productName);
            summary.addProperty("catering_cost", totalCateringCost);
        }
        
        if (parksSearch.businesses != null && !parksSearch.businesses.isEmpty()) {
            // Choose first park as "closest"
            summary.addProperty("recommended_park", parksSearch.businesses.get(0).name);
            summary.addProperty("park_address", parksSearch.businesses.get(0).address);
        }
        
        summary.addProperty("total_estimated_cost", totalHouseCost + totalCateringCost);
        summary.addProperty("reunion_date", "August 17, 2025");
        summary.addProperty("location", "Chicago, IL");
        summary.addProperty("attendees", 20);
        
        finalResult.add("reunion_summary", summary);
        
        return finalResult;
    }
}
