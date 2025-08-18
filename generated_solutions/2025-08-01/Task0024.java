import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0024 {
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
        
        // Step 1: Find conference centers in San Jose using Google Maps
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult venueSearch = maps.get_nearestBusinesses("San Jose, CA", "conference centers event spaces", 10);
        
        JsonArray venuesArray = new JsonArray();
        if (venueSearch.businesses != null && !venueSearch.businesses.isEmpty()) {
            for (maps_google_com.BusinessInfo venue : venueSearch.businesses) {
                JsonObject venueObj = new JsonObject();
                venueObj.addProperty("name", venue.name);
                venueObj.addProperty("address", venue.address);
                venuesArray.add(venueObj);
            }
        }
        finalResult.add("conference_centers", venuesArray);
        
        // Step 2: Search for short-term rentals for 6 speakers using Redfin
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult rentalSearch = redfin.searchApartments("San Jose, CA", 1200, 3500);
        
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
        finalResult.add("speaker_rentals", rentalsArray);
        if (rentalSearch.error != null) {
            finalResult.addProperty("rental_search_error", rentalSearch.error);
        }
        
        // Step 3: Find snack and beverage packages for 50 attendees using Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult snackSearch = costco.searchProducts("snack beverage packages party");
        
        JsonArray snacksArray = new JsonArray();
        if (snackSearch.products != null && !snackSearch.products.isEmpty()) {
            for (costco_com.ProductInfo product : snackSearch.products) {
                JsonObject snackObj = new JsonObject();
                snackObj.addProperty("product_name", product.productName);
                if (product.productPrice != null) {
                    snackObj.addProperty("price", product.productPrice.amount);
                    snackObj.addProperty("currency", product.productPrice.currency);
                }
                if (product.error != null) {
                    snackObj.addProperty("error", product.error);
                }
                snacksArray.add(snackObj);
            }
        }
        finalResult.add("snack_packages", snacksArray);
        if (snackSearch.error != null) {
            finalResult.addProperty("snack_search_error", snackSearch.error);
        }
        
        // Step 4: Check flight options from Los Angeles to San Jose using Alaska Airlines
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 15); // August 15, 2025
        LocalDate returnDate = LocalDate.of(2025, 8, 16);   // August 16, 2025
        alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("LAX", "SJC", outboundDate, returnDate);
        
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
        
        // Step 5: Calculate total costs and select best options
        JsonObject summary = new JsonObject();
        
        // Calculate total estimated costs
        double totalVenueCost = 0; // Venue cost would need to be estimated
        double totalRentalCost = 0;
        double totalSnackCost = 0;
        
        if (rentalSearch.apartments != null && !rentalSearch.apartments.isEmpty()) {
            // Assume first rental option for calculation (1 night)
            totalRentalCost = rentalSearch.apartments.get(0).price.amount;
            summary.addProperty("selected_rental", rentalSearch.apartments.get(0).address);
            summary.addProperty("rental_cost", totalRentalCost);
        }
        
        if (snackSearch.products != null && !snackSearch.products.isEmpty()) {
            // Estimate snacks for 50 people (multiple packages)
            totalSnackCost = snackSearch.products.get(0).productPrice != null ? 
                snackSearch.products.get(0).productPrice.amount * 3 : 0; // Assuming 3 packages needed
            summary.addProperty("selected_snacks", snackSearch.products.get(0).productName);
            summary.addProperty("snack_cost", totalSnackCost);
        }
        
        if (venueSearch.businesses != null && !venueSearch.businesses.isEmpty()) {
            summary.addProperty("recommended_venue", venueSearch.businesses.get(0).name);
            summary.addProperty("venue_address", venueSearch.businesses.get(0).address);
        }
        
        summary.addProperty("total_estimated_cost", totalVenueCost + totalRentalCost + totalSnackCost);
        summary.addProperty("meetup_date", "August 15, 2025");
        summary.addProperty("location", "San Jose, CA");
        summary.addProperty("attendees", 50);
        summary.addProperty("speakers", 6);
        summary.addProperty("event_type", "Tech Meetup");
        
        finalResult.add("meetup_summary", summary);
        
        return finalResult;
    }
}
