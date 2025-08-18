import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0004 {
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
        JsonObject result = new JsonObject();
        
        // Step 1: Clear Amazon cart to remove old items
        amazon_com amazon = new amazon_com(context);
        amazon.clearCart();
        
        JsonObject cartInfo = new JsonObject();
        cartInfo.addProperty("status", "Cart cleared successfully");
        result.add("cart_cleanup", cartInfo);
        
        // Step 2: Search for party supplies at Costco to get everything in bulk
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult partySupplies = costco.searchProducts("party supplies");
        
        JsonObject partySuppliesInfo = new JsonObject();
        if (partySupplies.error != null) {
            partySuppliesInfo.addProperty("error", partySupplies.error);
        } else {
            JsonArray productsArray = new JsonArray();
            for (costco_com.ProductInfo product : partySupplies.products) {
                JsonObject productObj = new JsonObject();
                productObj.addProperty("product_name", product.productName);
                if (product.productPrice != null) {
                    JsonObject priceObj = new JsonObject();
                    priceObj.addProperty("amount", product.productPrice.amount);
                    priceObj.addProperty("currency", product.productPrice.currency);
                    productObj.add("price", priceObj);
                }
                if (product.error != null) {
                    productObj.addProperty("product_error", product.error);
                }
                productsArray.add(productObj);
            }
            partySuppliesInfo.add("party_supplies", productsArray);
        }
        result.add("costco_shopping", partySuppliesInfo);
        
        // Step 3: Find good restaurants near the party venue in downtown Portland for catering options
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult restaurants = maps.get_nearestBusinesses("downtown Portland, OR", "restaurant", 15);
        
        JsonObject restaurantsInfo = new JsonObject();
        restaurantsInfo.addProperty("reference_point", restaurants.referencePoint);
        restaurantsInfo.addProperty("business_description", restaurants.businessDescription);
        
        JsonArray restaurantsArray = new JsonArray();
        for (maps_google_com.BusinessInfo restaurant : restaurants.businesses) {
            JsonObject restaurantObj = new JsonObject();
            restaurantObj.addProperty("name", restaurant.name);
            restaurantObj.addProperty("address", restaurant.address);
            restaurantsArray.add(restaurantObj);
        }
        restaurantsInfo.add("restaurants", restaurantsArray);
        result.add("catering_options", restaurantsInfo);
        
        // Step 4: Search for hotels for relatives coming from out of state for August 14-16, 2025
        booking_com hotels = new booking_com(context);
        LocalDate checkinDate = LocalDate.of(2025, 8, 14);
        LocalDate checkoutDate = LocalDate.of(2025, 8, 16);
        booking_com.HotelSearchResult hotelSearch = hotels.search_hotel("Portland, Oregon", checkinDate, checkoutDate);
        
        JsonObject hotelInfo = new JsonObject();
        hotelInfo.addProperty("destination", hotelSearch.destination);
        hotelInfo.addProperty("check_in_date", hotelSearch.checkinDate.toString());
        hotelInfo.addProperty("check_out_date", hotelSearch.checkoutDate.toString());
        
        JsonArray hotelArray = new JsonArray();
        for (booking_com.HotelInfo hotel : hotelSearch.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotel_name", hotel.hotelName);
            if (hotel.price != null) {
                JsonObject priceObj = new JsonObject();
                priceObj.addProperty("amount", hotel.price.amount);
                priceObj.addProperty("currency", hotel.price.currency);
                hotelObj.add("price", priceObj);
            }
            hotelArray.add(hotelObj);
        }
        hotelInfo.add("hotels", hotelArray);
        result.add("guest_accommodation", hotelInfo);
        
        return result;
    }
}
