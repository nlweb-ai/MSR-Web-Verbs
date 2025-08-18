import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0091 {
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
        
        // Step 1: Search for hotels in New Orleans for August 23-24, 2025
        booking_com booking = new booking_com(context);
        LocalDate checkinDate = LocalDate.of(2025, 8, 23);
        LocalDate checkoutDate = LocalDate.of(2025, 8, 24);
        
        booking_com.HotelSearchResult hotelResult = booking.search_hotel("New Orleans, Louisiana", checkinDate, checkoutDate);
        
        JsonObject hotelInfo = new JsonObject();
        hotelInfo.addProperty("destination", hotelResult.destination);
        hotelInfo.addProperty("checkin_date", hotelResult.checkinDate.toString());
        hotelInfo.addProperty("checkout_date", hotelResult.checkoutDate.toString());
        
        JsonArray hotelsArray = new JsonArray();
        for (booking_com.HotelInfo hotel : hotelResult.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotel_name", hotel.hotelName);
            if (hotel.price != null) {
                hotelObj.addProperty("price", hotel.price.amount);
                hotelObj.addProperty("currency", hotel.price.currency);
            }
            hotelsArray.add(hotelObj);
        }
        hotelInfo.add("hotels", hotelsArray);
        result.add("new_orleans_hotels", hotelInfo);
        
        // Step 2: Find restaurants and cafes near French Quarter (max 12 locations)
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "French Quarter, New Orleans, Louisiana";
        String businessDescription = "restaurants cafes dining";
        int maxCount = 12;
        
        maps_google_com.NearestBusinessesResult restaurantResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxCount);
        
        JsonObject diningInfo = new JsonObject();
        diningInfo.addProperty("reference_point", restaurantResult.referencePoint);
        diningInfo.addProperty("business_description", restaurantResult.businessDescription);
        
        JsonArray restaurantsArray = new JsonArray();
        JsonArray seafoodCreoleArray = new JsonArray();
        
        for (maps_google_com.BusinessInfo business : restaurantResult.businesses) {
            JsonObject restaurantObj = new JsonObject();
            restaurantObj.addProperty("name", business.name);
            restaurantObj.addProperty("address", business.address);
            
            // Categorize restaurants (prioritize seafood and Creole)
            String businessName = business.name.toLowerCase();
            boolean isSeafoodCreole = businessName.contains("seafood") || businessName.contains("creole") || 
                                    businessName.contains("cajun") || businessName.contains("oyster") || 
                                    businessName.contains("gumbo") || businessName.contains("jambalaya");
            restaurantObj.addProperty("cuisine_priority", isSeafoodCreole ? "high" : "standard");
            
            restaurantsArray.add(restaurantObj);
            if (isSeafoodCreole) {
                seafoodCreoleArray.add(restaurantObj);
            }
        }
        
        diningInfo.add("all_restaurants", restaurantsArray);
        diningInfo.add("priority_seafood_creole", seafoodCreoleArray);
        diningInfo.addProperty("total_restaurants", restaurantsArray.size());
        diningInfo.addProperty("priority_restaurants", seafoodCreoleArray.size());
        result.add("french_quarter_dining", diningInfo);
        
        // Step 3: Search Amazon for high-quality camera for food photography
        amazon_com amazon = new amazon_com(context);
        String cameraSearch = "high-quality camera food photography";
        
        amazon_com.CartResult cameraItems = amazon.addItemToCart(cameraSearch);
        
        JsonObject cameraInfo = new JsonObject();
        cameraInfo.addProperty("search_term", cameraSearch);
        cameraInfo.addProperty("purpose", "Document culinary experiences for blog");
        JsonArray cameraItemsArray = new JsonArray();
        for (amazon_com.CartItem item : cameraItems.items) {
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("item_name", item.itemName);
            if (item.price != null) {
                itemObj.addProperty("price", item.price.amount);
                itemObj.addProperty("currency", item.price.currency);
            }
            cameraItemsArray.add(itemObj);
        }
        cameraInfo.add("camera_equipment", cameraItemsArray);
        result.add("amazon_camera_search", cameraInfo);
        
        // Step 4: Search OpenLibrary for Louisiana and Creole cuisine cookbooks
        OpenLibrary openLibrary = new OpenLibrary();
        String cookbookQuery = "Louisiana Creole cuisine cookbook New Orleans cooking";
        
        JsonObject cookbookInfo = new JsonObject();
        try {
            java.util.List<OpenLibrary.BookInfo> books = openLibrary.search(cookbookQuery, null, null, null, 15, 1);
            cookbookInfo.addProperty("search_query", cookbookQuery);
            cookbookInfo.addProperty("total_books_found", books.size());
            
            JsonArray booksArray = new JsonArray();
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                booksArray.add(bookObj);
            }
            cookbookInfo.add("culinary_books", booksArray);
        } catch (Exception e) {
            cookbookInfo.addProperty("error", "Failed to search cookbooks: " + e.getMessage());
            cookbookInfo.add("culinary_books", new JsonArray());
            cookbookInfo.addProperty("total_books_found", 0);
        }
        result.add("openlibrary_cookbooks", cookbookInfo);
        
        // Culinary adventure summary
        JsonObject adventureSummary = new JsonObject();
        adventureSummary.addProperty("event_type", "Culinary Adventure Weekend");
        adventureSummary.addProperty("location", "New Orleans, Louisiana");
        adventureSummary.addProperty("dates", "2025-08-23 to 2025-08-24");
        adventureSummary.addProperty("accommodation_options", hotelsArray.size());
        adventureSummary.addProperty("total_dining_venues", restaurantsArray.size());
        adventureSummary.addProperty("priority_creole_seafood_venues", seafoodCreoleArray.size());
        
        int totalBooks = cookbookInfo.has("total_books_found") ? cookbookInfo.get("total_books_found").getAsInt() : 0;
        adventureSummary.addProperty("cultural_learning_resources", totalBooks);
        
        String itineraryRecommendation = createItineraryRecommendation(seafoodCreoleArray.size(), restaurantsArray.size());
        adventureSummary.addProperty("dining_itinerary_recommendation", itineraryRecommendation);
        
        result.add("culinary_adventure_summary", adventureSummary);
        
        return result;
    }
    
    // Helper method to create dining itinerary recommendations
    private static String createItineraryRecommendation(int priorityRestaurants, int totalRestaurants) {
        StringBuilder recommendation = new StringBuilder();
        
        if (priorityRestaurants >= 6) {
            recommendation.append("Excellent authentic options - focus on ").append(priorityRestaurants)
                          .append(" Creole/seafood establishments. ");
            recommendation.append("Recommend: breakfast at café, lunch at seafood spot, dinner at fine Creole restaurant. ");
        } else if (priorityRestaurants >= 3) {
            recommendation.append("Good authentic selection - visit ").append(priorityRestaurants)
                          .append(" specialty Creole/seafood venues. ");
            recommendation.append("Mix with ").append(totalRestaurants - priorityRestaurants)
                          .append(" other local favorites. ");
        } else {
            recommendation.append("Limited specialty venues found. Explore all ")
                          .append(totalRestaurants).append(" dining options. ");
            recommendation.append("Research specific Creole dishes at each location. ");
        }
        
        recommendation.append("Document each meal with camera for blog content creation.");
        
        return recommendation.toString();
    }
}
