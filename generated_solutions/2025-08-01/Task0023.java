import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0023 {
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
        
        // Step 1: Find university venues in Boston using Google Maps
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult venueSearch = maps.get_nearestBusinesses("Boston, MA", "university venues conference", 10);
        
        JsonArray venuesArray = new JsonArray();
        if (venueSearch.businesses != null && !venueSearch.businesses.isEmpty()) {
            for (maps_google_com.BusinessInfo venue : venueSearch.businesses) {
                JsonObject venueObj = new JsonObject();
                venueObj.addProperty("name", venue.name);
                venueObj.addProperty("address", venue.address);
                venuesArray.add(venueObj);
            }
        }
        finalResult.add("university_venues", venuesArray);
        
        // Step 2: Search for short-term rentals for 8 attendees using Redfin
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult rentalSearch = redfin.searchApartments("Boston, MA", 1500, 4000);
        
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
        finalResult.add("short_term_rentals", rentalsArray);
        if (rentalSearch.error != null) {
            finalResult.addProperty("rental_search_error", rentalSearch.error);
        }
        
        // Step 3: Find affordable AV equipment for presentations using Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult avEquipmentSearch = costco.searchProducts("projector presentation equipment");
        
        JsonArray avEquipmentArray = new JsonArray();
        if (avEquipmentSearch.products != null && !avEquipmentSearch.products.isEmpty()) {
            for (costco_com.ProductInfo product : avEquipmentSearch.products) {
                JsonObject avObj = new JsonObject();
                avObj.addProperty("product_name", product.productName);
                if (product.productPrice != null) {
                    avObj.addProperty("price", product.productPrice.amount);
                    avObj.addProperty("currency", product.productPrice.currency);
                }
                if (product.error != null) {
                    avObj.addProperty("error", product.error);
                }
                avEquipmentArray.add(avObj);
            }
        }
        finalResult.add("av_equipment", avEquipmentArray);
        if (avEquipmentSearch.error != null) {
            finalResult.addProperty("av_equipment_search_error", avEquipmentSearch.error);
        }
        
        // Step 4: Check flight prices from Atlanta to Boston using Alaska Airlines
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 23); // August 23, 2025
        LocalDate returnDate = LocalDate.of(2025, 8, 25);   // August 25, 2025
        alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("ATL", "BOS", outboundDate, returnDate);
        
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
        
        // Step 5: Compare and select the best options
        JsonObject summary = new JsonObject();
        
        // Calculate total estimated costs
        double totalRentalCost = 0;
        double totalAVCost = 0;
        
        if (rentalSearch.apartments != null && !rentalSearch.apartments.isEmpty()) {
            // Assume first rental option for calculation (3 nights)
            totalRentalCost = rentalSearch.apartments.get(0).price.amount * 3;
            summary.addProperty("selected_rental", rentalSearch.apartments.get(0).address);
            summary.addProperty("rental_cost", totalRentalCost);
        }
        
        if (avEquipmentSearch.products != null && !avEquipmentSearch.products.isEmpty()) {
            totalAVCost = avEquipmentSearch.products.get(0).productPrice != null ? 
                avEquipmentSearch.products.get(0).productPrice.amount : 0;
            summary.addProperty("selected_av_equipment", avEquipmentSearch.products.get(0).productName);
            summary.addProperty("av_cost", totalAVCost);
        }
        
        if (venueSearch.businesses != null && !venueSearch.businesses.isEmpty()) {
            summary.addProperty("recommended_venue", venueSearch.businesses.get(0).name);
            summary.addProperty("venue_address", venueSearch.businesses.get(0).address);
        }
        
        summary.addProperty("total_estimated_cost", totalRentalCost + totalAVCost);
        summary.addProperty("workshop_dates", "August 23-25, 2025");
        summary.addProperty("location", "Boston, MA");
        summary.addProperty("attendees", 8);
        summary.addProperty("event_type", "Graduate Student Workshop");
        
        finalResult.add("workshop_summary", summary);
        
        return finalResult;
    }
}
