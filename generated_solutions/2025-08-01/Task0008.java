import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0008 {
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
        
        // Step 1: Search for flights from Phoenix to Chicago for August 12-15, 2025
        alaskaair_com flights = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 12);
        LocalDate returnDate = LocalDate.of(2025, 8, 15);
        
        alaskaair_com.SearchFlightsResult flightSearch = flights.searchFlights("PHX", "ORD", outboundDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        if (flightSearch.message != null) {
            flightInfo.addProperty("message", flightSearch.message);
        } else if (flightSearch.flightInfo != null) {
            JsonArray flightArray = new JsonArray();
            for (String flight : flightSearch.flightInfo.flights) {
                flightArray.add(flight);
            }
            flightInfo.add("flights", flightArray);
            if (flightSearch.flightInfo.price != null) {
                JsonObject priceObj = new JsonObject();
                priceObj.addProperty("amount", flightSearch.flightInfo.price.amount);
                priceObj.addProperty("currency", flightSearch.flightInfo.price.currency);
                flightInfo.add("price", priceObj);
            }
        }
        result.add("flight_search", flightInfo);
        
        // Step 2: Book a hotel near the business district for August 12-15, 2025
        booking_com hotels = new booking_com(context);
        booking_com.HotelSearchResult hotelSearch = hotels.search_hotel("Chicago business district", outboundDate, returnDate);
        
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
        result.add("hotel_booking", hotelInfo);
        
        // Step 3: Add a professional leather briefcase to Amazon cart for presentations
        amazon_com amazon = new amazon_com(context);
        amazon_com.CartResult cartResult = amazon.addItemToCart("professional leather briefcase");
        
        JsonObject amazonInfo = new JsonObject();
        JsonArray cartItemsArray = new JsonArray();
        for (amazon_com.CartItem item : cartResult.items) {
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("item_name", item.itemName);
            if (item.price != null) {
                JsonObject priceObj = new JsonObject();
                priceObj.addProperty("amount", item.price.amount);
                priceObj.addProperty("currency", item.price.currency);
                itemObj.add("price", priceObj);
            }
            cartItemsArray.add(itemObj);
        }
        amazonInfo.add("cart_items", cartItemsArray);
        result.add("amazon_shopping", amazonInfo);
        
        // Step 4: Check the latest business news to stay informed about market trends
        News news = new News();
        JsonObject newsInfo = new JsonObject();
        
        try {
            News.NewsResponse businessNews = news.getTopHeadlines("us", "business");
            
            newsInfo.addProperty("status", businessNews.status);
            newsInfo.addProperty("total_results", businessNews.totalResults);
            
            JsonArray articlesArray = new JsonArray();
            for (News.NewsArticle article : businessNews.articles) {
                JsonObject articleObj = new JsonObject();
                articleObj.addProperty("title", article.title);
                articleObj.addProperty("description", article.description);
                articleObj.addProperty("url", article.url);
                articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : null);
                articleObj.addProperty("source", article.source);
                articlesArray.add(articleObj);
            }
            newsInfo.add("articles", articlesArray);
        } catch (Exception e) {
            newsInfo.addProperty("error", "Failed to get business news: " + e.getMessage());
        }
        result.add("business_news", newsInfo);
        
        return result;
    }
}
