import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0030 {
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
        
        // Step 1: Find rental property with large studio space for 6 artists in Santa Fe using Redfin
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult rentalSearch = redfin.searchApartments("Santa Fe, NM", 1200, 3500);
        
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
        finalResult.add("studio_rentals", rentalsArray);
        if (rentalSearch.error != null) {
            finalResult.addProperty("rental_search_error", rentalSearch.error);
        }
        
        // Step 2: Search for art supplies and snacks using Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult artSuppliesSearch = costco.searchProducts("art supplies craft materials");
        
        JsonArray artSuppliesArray = new JsonArray();
        if (artSuppliesSearch.products != null && !artSuppliesSearch.products.isEmpty()) {
            for (costco_com.ProductInfo product : artSuppliesSearch.products) {
                JsonObject artObj = new JsonObject();
                artObj.addProperty("product_name", product.productName);
                if (product.productPrice != null) {
                    artObj.addProperty("price", product.productPrice.amount);
                    artObj.addProperty("currency", product.productPrice.currency);
                }
                if (product.error != null) {
                    artObj.addProperty("error", product.error);
                }
                artSuppliesArray.add(artObj);
            }
        }
        finalResult.add("art_supplies", artSuppliesArray);
        if (artSuppliesSearch.error != null) {
            finalResult.addProperty("art_supplies_search_error", artSuppliesSearch.error);
        }
        
        // Step 3: Check flight options from Denver to Santa Fe using Alaska Airlines
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 16); // August 16, 2025
        LocalDate returnDate = LocalDate.of(2025, 8, 18);   // August 18, 2025
        alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("DEN", "SAF", outboundDate, returnDate);
        
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
        
        // Step 4: Find local art galleries and museums near Santa Fe using Google Maps
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult gallerySearch = maps.get_nearestBusinesses("Santa Fe, NM", "art galleries museums", 10);
        
        JsonArray galleriesArray = new JsonArray();
        if (gallerySearch.businesses != null && !gallerySearch.businesses.isEmpty()) {
            for (maps_google_com.BusinessInfo gallery : gallerySearch.businesses) {
                JsonObject galleryObj = new JsonObject();
                galleryObj.addProperty("name", gallery.name);
                galleryObj.addProperty("address", gallery.address);
                galleriesArray.add(galleryObj);
            }
        }
        finalResult.add("art_galleries_museums", galleriesArray);
        
        // Step 5: Compare rental amenities and art supply costs, create summary
        JsonObject summary = new JsonObject();
        
        // Calculate total estimated costs
        double totalRentalCost = 0;
        double totalArtSupplyCost = 0;
        
        if (rentalSearch.apartments != null && !rentalSearch.apartments.isEmpty()) {
            // Assume first rental option for calculation (3 nights)
            totalRentalCost = rentalSearch.apartments.get(0).price.amount * 3;
            summary.addProperty("selected_studio_rental", rentalSearch.apartments.get(0).address);
            summary.addProperty("rental_cost", totalRentalCost);
        }
        
        if (artSuppliesSearch.products != null && !artSuppliesSearch.products.isEmpty()) {
            // Estimate art supplies for 6 artists
            totalArtSupplyCost = artSuppliesSearch.products.get(0).productPrice != null ? 
                artSuppliesSearch.products.get(0).productPrice.amount * 3 : 0; // Assuming 3 packages needed
            summary.addProperty("selected_art_supplies", artSuppliesSearch.products.get(0).productName);
            summary.addProperty("art_supply_cost", totalArtSupplyCost);
        }
        
        if (gallerySearch.businesses != null && !gallerySearch.businesses.isEmpty()) {
            summary.addProperty("recommended_gallery", gallerySearch.businesses.get(0).name);
            summary.addProperty("gallery_address", gallerySearch.businesses.get(0).address);
        }
        
        summary.addProperty("total_estimated_cost", totalRentalCost + totalArtSupplyCost);
        summary.addProperty("retreat_dates", "August 16-18, 2025");
        summary.addProperty("location", "Santa Fe, NM");
        summary.addProperty("artists", 6);
        summary.addProperty("event_type", "Weekend Art Retreat");
        
        finalResult.add("art_retreat_summary", summary);
        
        return finalResult;
    }
}
