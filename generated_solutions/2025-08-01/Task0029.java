import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0029 {
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
        
        // Step 1: Find hotel conference facilities in San Diego using Google Maps
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult hotelSearch = maps.get_nearestBusinesses("San Diego, CA", "hotel conference facilities", 10);
        
        JsonArray hotelsArray = new JsonArray();
        if (hotelSearch.businesses != null && !hotelSearch.businesses.isEmpty()) {
            for (maps_google_com.BusinessInfo hotel : hotelSearch.businesses) {
                JsonObject hotelObj = new JsonObject();
                hotelObj.addProperty("name", hotel.name);
                hotelObj.addProperty("address", hotel.address);
                hotelsArray.add(hotelObj);
            }
        }
        finalResult.add("hotel_conference_facilities", hotelsArray);
        
        // Step 2: Search for short-term rentals for 8 out-of-town guests using Redfin
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult rentalSearch = redfin.searchApartments("San Diego, CA", 1500, 4000);
        
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
        finalResult.add("guest_rentals", rentalsArray);
        if (rentalSearch.error != null) {
            finalResult.addProperty("rental_search_error", rentalSearch.error);
        }
        
        // Step 3: Find catering packages for 40 attendees using Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult cateringSearch = costco.searchProducts("catering packages professional event");
        
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
        finalResult.add("catering_packages", cateringArray);
        if (cateringSearch.error != null) {
            finalResult.addProperty("catering_search_error", cateringSearch.error);
        }
        
        // Step 4: Check flight prices from Phoenix to San Diego using Alaska Airlines
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 30); // August 30, 2025
        LocalDate returnDate = LocalDate.of(2025, 8, 31);   // August 31, 2025
        alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("PHX", "SAN", outboundDate, returnDate);
        
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
        
        // Step 5: Compare hotel amenities and catering costs, create summary
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
            // Estimate catering for 40 people
            totalCateringCost = cateringSearch.products.get(0).productPrice != null ? 
                cateringSearch.products.get(0).productPrice.amount * 4 : 0; // Assuming 4 packages needed
            summary.addProperty("selected_catering", cateringSearch.products.get(0).productName);
            summary.addProperty("catering_cost", totalCateringCost);
        }
        
        if (hotelSearch.businesses != null && !hotelSearch.businesses.isEmpty()) {
            summary.addProperty("recommended_hotel", hotelSearch.businesses.get(0).name);
            summary.addProperty("hotel_address", hotelSearch.businesses.get(0).address);
        }
        
        summary.addProperty("total_estimated_cost", totalRentalCost + totalCateringCost);
        summary.addProperty("event_date", "August 30, 2025");
        summary.addProperty("location", "San Diego, CA");
        summary.addProperty("attendees", 40);
        summary.addProperty("out_of_town_guests", 8);
        summary.addProperty("event_type", "Professional Networking Event");
        
        finalResult.add("networking_summary", summary);
        
        return finalResult;
    }
}
