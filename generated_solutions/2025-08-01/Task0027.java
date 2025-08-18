import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0027 {
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
        
        // Step 1: Find rental property for 10 attendees in Houston using Redfin
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult rentalSearch = redfin.searchApartments("Houston, TX", 1500, 4000);
        
        JsonArray rentalsArray = new JsonArray();
        if (rentalSearch.apartments != null && !rentalSearch.apartments.isEmpty()) {
            for (redfin_com.ApartmentInfo rental : rentalSearch.apartments) {
                JsonObject rentalObj = new JsonObject();
                rentalObj.addProperty("address", rental.address);
                rentalObj.addProperty("price", rental.price.amount);
                rentalObj.addProperty("currency", rental.price.currency);
                rentalObj.addProperty("url", rental.url);
                rentalsArray.add(rentalObj);
            }
        }
        finalResult.add("rental_properties", rentalsArray);
        if (rentalSearch.error != null) {
            finalResult.addProperty("rental_search_error", rentalSearch.error);
        }
        
        // Step 2: Search for lunch catering options using Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult cateringSearch = costco.searchProducts("lunch catering corporate");
        
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
        
        // Step 3: Check flight prices from Miami to Houston using Alaska Airlines
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 12); // August 12, 2025
        LocalDate returnDate = LocalDate.of(2025, 8, 13);   // August 13, 2025
        alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("MIA", "IAH", outboundDate, returnDate);
        
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
        
        // Step 4: Find training centers near the rental property using Google Maps
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult trainingCenterSearch = maps.get_nearestBusinesses("Houston, TX", "training centers conference facilities", 10);
        
        JsonArray trainingCentersArray = new JsonArray();
        if (trainingCenterSearch.businesses != null && !trainingCenterSearch.businesses.isEmpty()) {
            for (maps_google_com.BusinessInfo center : trainingCenterSearch.businesses) {
                JsonObject centerObj = new JsonObject();
                centerObj.addProperty("name", center.name);
                centerObj.addProperty("address", center.address);
                trainingCentersArray.add(centerObj);
            }
        }
        finalResult.add("training_centers", trainingCentersArray);
        
        // Step 5: Compare costs and create summary
        JsonObject summary = new JsonObject();
        
        // Calculate total estimated costs
        double totalRentalCost = 0;
        double totalCateringCost = 0;
        
        if (rentalSearch.apartments != null && !rentalSearch.apartments.isEmpty()) {
            // Assume first rental option for calculation (1 night)
            totalRentalCost = rentalSearch.apartments.get(0).price.amount;
            summary.addProperty("selected_rental", rentalSearch.apartments.get(0).address);
            summary.addProperty("rental_cost", totalRentalCost);
        }
        
        if (cateringSearch.products != null && !cateringSearch.products.isEmpty()) {
            // Estimate catering for 10 people
            totalCateringCost = cateringSearch.products.get(0).productPrice != null ? 
                cateringSearch.products.get(0).productPrice.amount * 2 : 0; // Assuming 2 packages needed
            summary.addProperty("selected_catering", cateringSearch.products.get(0).productName);
            summary.addProperty("catering_cost", totalCateringCost);
        }
        
        if (trainingCenterSearch.businesses != null && !trainingCenterSearch.businesses.isEmpty()) {
            summary.addProperty("recommended_training_center", trainingCenterSearch.businesses.get(0).name);
            summary.addProperty("center_address", trainingCenterSearch.businesses.get(0).address);
        }
        
        summary.addProperty("total_estimated_cost", totalRentalCost + totalCateringCost);
        summary.addProperty("training_date", "August 12, 2025");
        summary.addProperty("location", "Houston, TX");
        summary.addProperty("attendees", 10);
        summary.addProperty("event_type", "Corporate Training Session");
        
        finalResult.add("training_summary", summary);
        
        return finalResult;
    }
}
