import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0016 {
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
        
        // 1. Search for flights from Los Angeles, CA to Chicago, IL for August 12-15
        alaskaair_com alaskaAir = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 12);
        LocalDate returnDate = LocalDate.of(2025, 8, 15);
        
        alaskaair_com.SearchFlightsResult flightResults = alaskaAir.searchFlights("LAX", "ORD", outboundDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        flightInfo.addProperty("origin", "Los Angeles, CA (LAX)");
        flightInfo.addProperty("destination", "Chicago, IL (ORD)");
        flightInfo.addProperty("outboundDate", outboundDate.toString());
        flightInfo.addProperty("returnDate", returnDate.toString());
        flightInfo.addProperty("purpose", "Business trip logistics");
        
        if (flightResults.message != null) {
            flightInfo.addProperty("message", flightResults.message);
        }
        
        JsonObject budgetAnalysis = new JsonObject();
        if (flightResults.flightInfo != null) {
            JsonArray flightsArray = new JsonArray();
            for (String flight : flightResults.flightInfo.flights) {
                flightsArray.add(flight);
            }
            flightInfo.add("availableFlights", flightsArray);
            
            if (flightResults.flightInfo.price != null) {
                flightInfo.addProperty("totalFlightCost", flightResults.flightInfo.price.amount);
                flightInfo.addProperty("currency", flightResults.flightInfo.price.currency);
                
                // Budget analysis
                double flightCost = flightResults.flightInfo.price.amount;
                budgetAnalysis.addProperty("flightCost", Math.round(flightCost * 100.0) / 100.0);
                budgetAnalysis.addProperty("costCategory", flightCost < 400 ? "Budget-friendly" : 
                                         flightCost < 800 ? "Moderate" : "Premium");
                budgetAnalysis.addProperty("businessTravelAssessment", 
                    "Flight cost represents " + Math.round((flightCost / 2000) * 100) + "% of typical $2000 business trip budget");
            }
        }
        
        result.add("flightSearch", flightInfo);
        result.add("travelBudget", budgetAnalysis);
        
        // 2. Search for hotels in Chicago for August 12-15
        booking_com booking = new booking_com(context);
        LocalDate checkinDate = LocalDate.of(2025, 8, 12);
        LocalDate checkoutDate = LocalDate.of(2025, 8, 15);
        
        booking_com.HotelSearchResult hotelResults = booking.search_hotel("Chicago, Illinois", checkinDate, checkoutDate);
        
        JsonObject hotelInfo = new JsonObject();
        hotelInfo.addProperty("destination", hotelResults.destination);
        hotelInfo.addProperty("checkinDate", hotelResults.checkinDate.toString());
        hotelInfo.addProperty("checkoutDate", hotelResults.checkoutDate.toString());
        hotelInfo.addProperty("purpose", "Business accommodations near downtown area");
        
        JsonArray hotelsArray = new JsonArray();
        double totalHotelCost = 0.0;
        double minHotelPrice = Double.MAX_VALUE;
        double maxHotelPrice = 0.0;
        int validHotelPrices = 0;
        
        for (booking_com.HotelInfo hotel : hotelResults.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotelName", hotel.hotelName);
            
            if (hotel.price != null) {
                hotelObj.addProperty("pricePerNight", hotel.price.amount);
                hotelObj.addProperty("currency", hotel.price.currency);
                
                // Categorize hotels for business travel
                String businessSuitability;
                if (hotel.price.amount <= 120) {
                    businessSuitability = "Budget business option - suitable for cost-conscious travel";
                } else if (hotel.price.amount <= 250) {
                    businessSuitability = "Standard business hotel - good amenities and location";
                } else {
                    businessSuitability = "Premium business accommodation - luxury amenities and prime location";
                }
                hotelObj.addProperty("businessSuitability", businessSuitability);
                
                totalHotelCost += hotel.price.amount;
                validHotelPrices++;
                minHotelPrice = Math.min(minHotelPrice, hotel.price.amount);
                maxHotelPrice = Math.max(maxHotelPrice, hotel.price.amount);
            } else {
                hotelObj.addProperty("pricePerNight", (String) null);
                hotelObj.addProperty("currency", (String) null);
                hotelObj.addProperty("businessSuitability", "Pricing not available");
            }
            
            hotelsArray.add(hotelObj);
        }
        
        hotelInfo.add("hotels", hotelsArray);
        
        // Hotel accommodation analysis
        JsonObject accommodationAnalysis = new JsonObject();
        accommodationAnalysis.addProperty("totalHotelsFound", hotelResults.hotels.size());
        if (validHotelPrices > 0) {
            double avgPrice = totalHotelCost / validHotelPrices;
            int tripDuration = 3; // 3 nights
            accommodationAnalysis.addProperty("averagePricePerNight", Math.round(avgPrice * 100.0) / 100.0);
            accommodationAnalysis.addProperty("minPricePerNight", Math.round(minHotelPrice * 100.0) / 100.0);
            accommodationAnalysis.addProperty("maxPricePerNight", Math.round(maxHotelPrice * 100.0) / 100.0);
            accommodationAnalysis.addProperty("totalAccommodationCost", Math.round(avgPrice * tripDuration * 100.0) / 100.0);
        }
        
        hotelInfo.add("accommodationAnalysis", accommodationAnalysis);
        result.add("hotelAccommodation", hotelInfo);
        
        // 3. Add business laptop bag to Amazon cart
        amazon_com amazon = new amazon_com(context);
        amazon_com.CartResult cartResult = amazon.addItemToCart("business laptop bag");
        
        JsonObject shoppingInfo = new JsonObject();
        shoppingInfo.addProperty("item", "business laptop bag");
        shoppingInfo.addProperty("purpose", "Reliable travel gear for business documents and electronics");
        
        JsonArray cartItemsArray = new JsonArray();
        double totalCartValue = 0.0;
        
        for (amazon_com.CartItem item : cartResult.items) {
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("itemName", item.itemName);
            if (item.price != null) {
                itemObj.addProperty("price", item.price.amount);
                itemObj.addProperty("currency", item.price.currency);
                totalCartValue += item.price.amount;
                
                // Assess value for business travel
                String businessValue;
                if (item.price.amount <= 50) {
                    businessValue = "Budget-friendly option for basic business needs";
                } else if (item.price.amount <= 150) {
                    businessValue = "Good value for professional business travel";
                } else {
                    businessValue = "Premium business accessory with advanced features";
                }
                itemObj.addProperty("businessValue", businessValue);
            }
            cartItemsArray.add(itemObj);
        }
        
        shoppingInfo.add("cartItems", cartItemsArray);
        shoppingInfo.addProperty("totalCartValue", Math.round(totalCartValue * 100.0) / 100.0);
        shoppingInfo.addProperty("travelGearAssessment", "Essential for protecting business equipment during travel");
        
        result.add("businessShopping", shoppingInfo);
        
        // 4. Search for current business news
        try {
            News news = new News();
            News.NewsResponse businessNews = news.getTopHeadlines("us", "business");
            
            JsonObject newsInfo = new JsonObject();
            newsInfo.addProperty("category", "Business");
            newsInfo.addProperty("country", "US");
            newsInfo.addProperty("purpose", "Stay updated on market trends for business meetings");
            newsInfo.addProperty("status", businessNews.status);
            newsInfo.addProperty("totalResults", businessNews.totalResults);
            
            JsonArray articlesArray = new JsonArray();
            JsonArray discussionTopics = new JsonArray();
            
            for (News.NewsArticle article : businessNews.articles) {
                JsonObject articleObj = new JsonObject();
                articleObj.addProperty("title", article.title);
                articleObj.addProperty("description", article.description);
                articleObj.addProperty("url", article.url);
                articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                articleObj.addProperty("source", article.source);
                
                // Extract business discussion topics
                String title = article.title.toLowerCase();
                if (title.contains("market") || title.contains("stock") || title.contains("trading")) {
                    discussionTopics.add("Market trends and investment opportunities");
                }
                if (title.contains("tech") || title.contains("innovation") || title.contains("startup")) {
                    discussionTopics.add("Technology sector developments and startup ecosystem");
                }
                if (title.contains("economy") || title.contains("gdp") || title.contains("growth")) {
                    discussionTopics.add("Economic indicators and growth forecasts");
                }
                if (title.contains("merger") || title.contains("acquisition") || title.contains("deal")) {
                    discussionTopics.add("Mergers, acquisitions, and corporate strategy");
                }
                if (title.contains("regulation") || title.contains("policy") || title.contains("government")) {
                    discussionTopics.add("Regulatory changes and government policy impacts");
                }
                
                articlesArray.add(articleObj);
            }
            
            // Add general business discussion topics
            discussionTopics.add("Industry best practices and operational efficiency");
            discussionTopics.add("Supply chain management and logistics");
            discussionTopics.add("Digital transformation and business automation");
            
            newsInfo.add("articles", articlesArray);
            newsInfo.add("meetingDiscussionTopics", discussionTopics);
            
            result.add("businessNews", newsInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject newsError = new JsonObject();
            newsError.addProperty("error", "Failed to get business news: " + e.getMessage());
            result.add("businessNews", newsError);
        }
        
        // 5. Business trip summary and total budget calculation
        JsonObject tripSummary = new JsonObject();
        tripSummary.addProperty("trip", "Business Trip - Los Angeles to Chicago");
        tripSummary.addProperty("duration", "August 12-15, 2025 (3 nights)");
        tripSummary.addProperty("purpose", "Business meetings and professional networking");
        
        // Calculate total trip cost
        double totalTripCost = 0.0;
        if (flightResults.flightInfo != null && flightResults.flightInfo.price != null) {
            totalTripCost += flightResults.flightInfo.price.amount;
        }
        if (validHotelPrices > 0) {
            totalTripCost += (totalHotelCost / validHotelPrices) * 3; // 3 nights
        }
        totalTripCost += totalCartValue; // Travel gear
        
        JsonObject costBreakdown = new JsonObject();
        if (flightResults.flightInfo != null && flightResults.flightInfo.price != null) {
            costBreakdown.addProperty("flights", flightResults.flightInfo.price.amount);
        }
        if (validHotelPrices > 0) {
            costBreakdown.addProperty("accommodation", Math.round((totalHotelCost / validHotelPrices) * 3 * 100.0) / 100.0);
        }
        costBreakdown.addProperty("travelGear", totalCartValue);
        costBreakdown.addProperty("estimatedMeals", 200.0); // Estimated meal costs
        costBreakdown.addProperty("localTransport", 100.0); // Estimated local transport
        
        totalTripCost += 300.0; // Add estimated meals and transport
        
        tripSummary.add("costBreakdown", costBreakdown);
        tripSummary.addProperty("totalEstimatedCost", Math.round(totalTripCost * 100.0) / 100.0);
        
        JsonArray preparationChecklist = new JsonArray();
        preparationChecklist.add("Confirm flight bookings and check-in online");
        preparationChecklist.add("Reserve business-appropriate hotel near downtown area");
        preparationChecklist.add("Purchase reliable laptop bag for travel equipment");
        preparationChecklist.add("Prepare discussion topics based on current business news");
        preparationChecklist.add("Schedule ground transportation from ORD to hotel");
        preparationChecklist.add("Pack business attire and meeting materials");
        
        tripSummary.add("preparationSteps", preparationChecklist);
        result.add("businessTripSummary", tripSummary);
        
        return result;
    }
}
