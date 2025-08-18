import java.io.IOException;
import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0081 {
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
        
        // Step 1: Search for flights from LAX to PDX for August 15-17, 2025
        alaskaair_com alaska = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 15);
        LocalDate returnDate = LocalDate.of(2025, 8, 17);
        
        alaskaair_com.SearchFlightsResult flightResult = alaska.searchFlights("LAX", "PDX", outboundDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        if (flightResult.message != null) {
            flightInfo.addProperty("message", flightResult.message);
            flightInfo.addProperty("flight_price", 0.0);
        } else if (flightResult.flightInfo != null) {
            JsonArray flightsArray = new JsonArray();
            for (String flight : flightResult.flightInfo.flights) {
                flightsArray.add(flight);
            }
            flightInfo.add("flights", flightsArray);
            if (flightResult.flightInfo.price != null) {
                flightInfo.addProperty("flight_price", flightResult.flightInfo.price.amount);
                flightInfo.addProperty("currency", flightResult.flightInfo.price.currency);
            } else {
                flightInfo.addProperty("flight_price", 0.0);
            }
        }
        result.add("flight_search", flightInfo);
        
        // Step 2: Calculate remaining budget (starting with $2000)
        double initialBudget = 2000.0;
        double flightCost = 0.0;
        if (flightResult.flightInfo != null && flightResult.flightInfo.price != null) {
            flightCost = flightResult.flightInfo.price.amount;
        }
        double remainingBudget = initialBudget - flightCost;
        
        JsonObject budgetInfo = new JsonObject();
        budgetInfo.addProperty("initial_budget", initialBudget);
        budgetInfo.addProperty("flight_cost", flightCost);
        budgetInfo.addProperty("remaining_budget", remainingBudget);
        result.add("budget_calculation", budgetInfo);
        
        // Step 3: Search for hotels in Portland using Booking.com
        booking_com booking = new booking_com(context);
        LocalDate checkinDate = LocalDate.of(2025, 8, 15);
        LocalDate checkoutDate = LocalDate.of(2025, 8, 17);
        
        booking_com.HotelSearchResult hotelResult = booking.search_hotel("Portland, Oregon", checkinDate, checkoutDate);
        
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
        result.add("hotel_search", hotelInfo);
        
        // Step 4: Find nearby coffee shops using Google Maps (max 5)
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "Portland, Oregon";
        String businessDescription = "coffee shop";
        int maxCount = 5;
        
        maps_google_com.NearestBusinessesResult coffeeResult = maps.get_nearestBusinesses(referencePoint, businessDescription, maxCount);
        
        JsonObject coffeeInfo = new JsonObject();
        coffeeInfo.addProperty("reference_point", coffeeResult.referencePoint);
        coffeeInfo.addProperty("business_description", coffeeResult.businessDescription);
        
        JsonArray coffeeShopsArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : coffeeResult.businesses) {
            JsonObject businessObj = new JsonObject();
            businessObj.addProperty("name", business.name);
            businessObj.addProperty("address", business.address);
            coffeeShopsArray.add(businessObj);
        }
        coffeeInfo.add("coffee_shops", coffeeShopsArray);
        result.add("coffee_shops", coffeeInfo);
        
        // Step 5: Get current news about Portland tourism
        News news = new News();
        String query = "Portland tourism";
        
        JsonObject newsInfo = new JsonObject();
        try {
            News.NewsResponse newsResult = news.searchEverything(query);
            newsInfo.addProperty("status", newsResult.status);
            newsInfo.addProperty("total_results", newsResult.totalResults);
            
            JsonArray articlesArray = new JsonArray();
            for (News.NewsArticle article : newsResult.articles) {
                JsonObject articleObj = new JsonObject();
                articleObj.addProperty("title", article.title);
                articleObj.addProperty("description", article.description);
                articleObj.addProperty("url", article.url);
                articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : null);
                articleObj.addProperty("source", article.source);
                articlesArray.add(articleObj);
            }
            newsInfo.add("articles", articlesArray);
        } catch (IOException | InterruptedException e) {
            newsInfo.addProperty("error", "Failed to fetch news: " + e.getMessage());
            newsInfo.add("articles", new JsonArray());
        }
        result.add("portland_tourism_news", newsInfo);
        
        return result;
    }
}
