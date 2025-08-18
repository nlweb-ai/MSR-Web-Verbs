import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0028 {
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
        
        // Step 1: Find event spaces in Austin using Google Maps
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult venueSearch = maps.get_nearestBusinesses("Austin, TX", "event spaces hackathon venues", 10);
        
        JsonArray venuesArray = new JsonArray();
        if (venueSearch.businesses != null && !venueSearch.businesses.isEmpty()) {
            for (maps_google_com.BusinessInfo venue : venueSearch.businesses) {
                JsonObject venueObj = new JsonObject();
                venueObj.addProperty("name", venue.name);
                venueObj.addProperty("address", venue.address);
                venuesArray.add(venueObj);
            }
        }
        finalResult.add("event_spaces", venuesArray);
        
        // Step 2: Search for short-term rentals for 12 participants using Redfin
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult rentalSearch = redfin.searchApartments("Austin, TX", 1800, 5000);
        
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
        finalResult.add("participant_rentals", rentalsArray);
        if (rentalSearch.error != null) {
            finalResult.addProperty("rental_search_error", rentalSearch.error);
        }
        
        // Step 3: Find energy drinks and snacks for the hackathon using Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult snackSearch = costco.searchProducts("energy drinks snacks bulk");
        
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
        finalResult.add("snacks_energy_drinks", snacksArray);
        if (snackSearch.error != null) {
            finalResult.addProperty("snack_search_error", snackSearch.error);
        }
        
        // Step 4: Check flight options from Chicago to Austin using Alaska Airlines
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 22); // August 22, 2025
        LocalDate returnDate = LocalDate.of(2025, 8, 24);   // August 24, 2025
        alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("ORD", "AUS", outboundDate, returnDate);
        
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
        
        // Step 5: Compare amenities and prices, create summary
        JsonObject summary = new JsonObject();
        
        // Calculate total estimated costs
        double totalRentalCost = 0;
        double totalSnackCost = 0;
        
        if (rentalSearch.apartments != null && !rentalSearch.apartments.isEmpty()) {
            // Assume first rental option for calculation (3 nights)
            totalRentalCost = rentalSearch.apartments.get(0).price.amount * 3;
            summary.addProperty("selected_rental", rentalSearch.apartments.get(0).address);
            summary.addProperty("rental_cost", totalRentalCost);
        }
        
        if (snackSearch.products != null && !snackSearch.products.isEmpty()) {
            // Estimate snacks and energy drinks for 12 people for 3 days
            totalSnackCost = snackSearch.products.get(0).productPrice != null ? 
                snackSearch.products.get(0).productPrice.amount * 4 : 0; // Assuming 4 packages needed
            summary.addProperty("selected_snacks", snackSearch.products.get(0).productName);
            summary.addProperty("snack_cost", totalSnackCost);
        }
        
        if (venueSearch.businesses != null && !venueSearch.businesses.isEmpty()) {
            summary.addProperty("recommended_event_space", venueSearch.businesses.get(0).name);
            summary.addProperty("venue_address", venueSearch.businesses.get(0).address);
        }
        
        summary.addProperty("total_estimated_cost", totalRentalCost + totalSnackCost);
        summary.addProperty("hackathon_dates", "August 22-24, 2025");
        summary.addProperty("location", "Austin, TX");
        summary.addProperty("participants", 12);
        summary.addProperty("event_type", "Weekend Hackathon");
        
        finalResult.add("hackathon_summary", summary);
        
        return finalResult;
    }
}
