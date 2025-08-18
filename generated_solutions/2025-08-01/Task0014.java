import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0014 {
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
        
        // 1. Set preferred Costco warehouse to San Francisco, CA
        costco_com costco = new costco_com(context);
        costco_com.WarehouseStatusResult warehouseStatus = costco.setPreferredWarehouse("San Francisco, CA");
        
        JsonObject warehouseInfo = new JsonObject();
        warehouseInfo.addProperty("location", "San Francisco, CA");
        warehouseInfo.addProperty("status", warehouseStatus.status);
        if (warehouseStatus.error != null) {
            warehouseInfo.addProperty("error", warehouseStatus.error);
        }
        result.add("warehouseSetup", warehouseInfo);
        
        // 2. Search for office supplies at Costco
        costco_com.ProductListResult officeSuppliesResults = costco.searchProducts("office supplies");
        
        JsonObject officeSuppliesInfo = new JsonObject();
        officeSuppliesInfo.addProperty("searchTerm", "office supplies");
        if (officeSuppliesResults.error != null) {
            officeSuppliesInfo.addProperty("error", officeSuppliesResults.error);
        }
        
        JsonArray officeProductsArray = new JsonArray();
        double totalOfficeSuppliesCost = 0.0;
        for (costco_com.ProductInfo product : officeSuppliesResults.products) {
            JsonObject productObj = new JsonObject();
            productObj.addProperty("productName", product.productName);
            if (product.productPrice != null) {
                productObj.addProperty("priceAmount", product.productPrice.amount);
                productObj.addProperty("priceCurrency", product.productPrice.currency);
                totalOfficeSuppliesCost += product.productPrice.amount;
            }
            if (product.error != null) {
                productObj.addProperty("error", product.error);
            }
            officeProductsArray.add(productObj);
        }
        officeSuppliesInfo.add("products", officeProductsArray);
        officeSuppliesInfo.addProperty("totalEstimatedCost", Math.round(totalOfficeSuppliesCost * 100.0) / 100.0);
        
        // 3. Search for snacks at Costco
        costco_com.ProductListResult snacksResults = costco.searchProducts("snacks");
        
        JsonObject snacksInfo = new JsonObject();
        snacksInfo.addProperty("searchTerm", "snacks");
        if (snacksResults.error != null) {
            snacksInfo.addProperty("error", snacksResults.error);
        }
        
        JsonArray snackProductsArray = new JsonArray();
        double totalSnacksCost = 0.0;
        for (costco_com.ProductInfo product : snacksResults.products) {
            JsonObject productObj = new JsonObject();
            productObj.addProperty("productName", product.productName);
            if (product.productPrice != null) {
                productObj.addProperty("priceAmount", product.productPrice.amount);
                productObj.addProperty("priceCurrency", product.productPrice.currency);
                totalSnacksCost += product.productPrice.amount;
            }
            if (product.error != null) {
                productObj.addProperty("error", product.error);
            }
            snackProductsArray.add(productObj);
        }
        snacksInfo.add("products", snackProductsArray);
        snacksInfo.addProperty("totalEstimatedCost", Math.round(totalSnacksCost * 100.0) / 100.0);
        
        // Calculate total procurement costs for 50 attendees
        JsonObject procurementSummary = new JsonObject();
        procurementSummary.addProperty("targetAttendees", 50);
        procurementSummary.addProperty("officeSuppliesTotal", Math.round(totalOfficeSuppliesCost * 100.0) / 100.0);
        procurementSummary.addProperty("snacksTotal", Math.round(totalSnacksCost * 100.0) / 100.0);
        double grandTotal = totalOfficeSuppliesCost + totalSnacksCost;
        procurementSummary.addProperty("grandTotal", Math.round(grandTotal * 100.0) / 100.0);
        procurementSummary.addProperty("costPerAttendee", Math.round((grandTotal / 50) * 100.0) / 100.0);
        
        JsonObject costcoResults = new JsonObject();
        costcoResults.add("officeSupplies", officeSuppliesInfo);
        costcoResults.add("snacks", snacksInfo);
        costcoResults.add("procurementSummary", procurementSummary);
        result.add("costcoProcurement", costcoResults);
        
        // 4. Search for hotels in San Francisco for August 25-27
        booking_com booking = new booking_com(context);
        LocalDate checkinDate = LocalDate.of(2025, 8, 25);
        LocalDate checkoutDate = LocalDate.of(2025, 8, 27);
        
        booking_com.HotelSearchResult hotelResults = booking.search_hotel("San Francisco", checkinDate, checkoutDate);
        
        JsonObject hotelInfo = new JsonObject();
        hotelInfo.addProperty("destination", hotelResults.destination);
        hotelInfo.addProperty("checkinDate", hotelResults.checkinDate.toString());
        hotelInfo.addProperty("checkoutDate", hotelResults.checkoutDate.toString());
        hotelInfo.addProperty("purpose", "Accommodation for out-of-town speakers");
        
        JsonArray hotelsArray = new JsonArray();
        double totalHotelCost = 0.0;
        double minHotelPrice = Double.MAX_VALUE;
        double maxHotelPrice = 0.0;
        int validHotelPrices = 0;
        
        for (booking_com.HotelInfo hotel : hotelResults.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotelName", hotel.hotelName);
            if (hotel.price != null) {
                hotelObj.addProperty("priceAmount", hotel.price.amount);
                hotelObj.addProperty("priceCurrency", hotel.price.currency);
                hotelObj.addProperty("priceType", "Per night");
                
                totalHotelCost += hotel.price.amount;
                validHotelPrices++;
                minHotelPrice = Math.min(minHotelPrice, hotel.price.amount);
                maxHotelPrice = Math.max(maxHotelPrice, hotel.price.amount);
            } else {
                hotelObj.addProperty("priceAmount", (String) null);
                hotelObj.addProperty("priceCurrency", (String) null);
            }
            hotelsArray.add(hotelObj);
        }
        
        hotelInfo.add("hotels", hotelsArray);
        
        // Hotel pricing analysis
        JsonObject hotelAnalysis = new JsonObject();
        hotelAnalysis.addProperty("totalHotelsFound", hotelResults.hotels.size());
        if (validHotelPrices > 0) {
            double avgPrice = totalHotelCost / validHotelPrices;
            hotelAnalysis.addProperty("averagePricePerNight", Math.round(avgPrice * 100.0) / 100.0);
            hotelAnalysis.addProperty("minPricePerNight", Math.round(minHotelPrice * 100.0) / 100.0);
            hotelAnalysis.addProperty("maxPricePerNight", Math.round(maxHotelPrice * 100.0) / 100.0);
            hotelAnalysis.addProperty("totalCostForTwoNights", Math.round(avgPrice * 2 * 100.0) / 100.0);
            hotelAnalysis.addProperty("recommendedBudgetPerSpeaker", Math.round(avgPrice * 2 * 1.1 * 100.0) / 100.0); // 10% buffer
        }
        
        hotelInfo.add("pricingAnalysis", hotelAnalysis);
        result.add("hotelAccommodation", hotelInfo);
        
        // 5. Search for latest technology news
        try {
            News news = new News();
            News.NewsResponse techNews = news.getTopHeadlines("us", "technology");
            
            JsonObject newsInfo = new JsonObject();
            newsInfo.addProperty("category", "Technology");
            newsInfo.addProperty("country", "US");
            newsInfo.addProperty("purpose", "Identify trending topics for startup event discussions");
            newsInfo.addProperty("status", techNews.status);
            newsInfo.addProperty("totalResults", techNews.totalResults);
            
            JsonArray articlesArray = new JsonArray();
            JsonArray trendingTopics = new JsonArray();
            
            for (News.NewsArticle article : techNews.articles) {
                JsonObject articleObj = new JsonObject();
                articleObj.addProperty("title", article.title);
                articleObj.addProperty("description", article.description);
                articleObj.addProperty("url", article.url);
                articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                articleObj.addProperty("source", article.source);
                
                // Extract trending topics from titles
                String title = article.title.toLowerCase();
                if (title.contains("ai") || title.contains("artificial intelligence")) {
                    trendingTopics.add("Artificial Intelligence and Machine Learning");
                }
                if (title.contains("startup") || title.contains("funding")) {
                    trendingTopics.add("Startup Funding and Investment Trends");
                }
                if (title.contains("crypto") || title.contains("blockchain")) {
                    trendingTopics.add("Cryptocurrency and Blockchain Technology");
                }
                if (title.contains("cloud") || title.contains("saas")) {
                    trendingTopics.add("Cloud Computing and SaaS Solutions");
                }
                if (title.contains("data") || title.contains("analytics")) {
                    trendingTopics.add("Big Data and Analytics");
                }
                if (title.contains("mobile") || title.contains("app")) {
                    trendingTopics.add("Mobile Technology and App Development");
                }
                if (title.contains("cybersecurity") || title.contains("security")) {
                    trendingTopics.add("Cybersecurity and Data Protection");
                }
                
                articlesArray.add(articleObj);
            }
            
            // Add some default trending topics for tech startups
            trendingTopics.add("Digital Transformation in Enterprise");
            trendingTopics.add("Remote Work Technologies");
            trendingTopics.add("Sustainable Tech Solutions");
            
            newsInfo.add("articles", articlesArray);
            newsInfo.add("suggestedDiscussionTopics", trendingTopics);
            
            result.add("technologyNews", newsInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject newsError = new JsonObject();
            newsError.addProperty("error", "Failed to get technology news: " + e.getMessage());
            newsError.addProperty("category", "Technology");
            result.add("technologyNews", newsError);
        }
        
        // 6. Get directions from San Francisco International Airport to downtown San Francisco
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.DirectionResult directions = maps.get_direction("San Francisco International Airport", "downtown San Francisco");
        
        JsonObject directionsInfo = new JsonObject();
        directionsInfo.addProperty("origin", "San Francisco International Airport (SFO)");
        directionsInfo.addProperty("destination", "Downtown San Francisco");
        directionsInfo.addProperty("purpose", "Travel guidance for attendees");
        directionsInfo.addProperty("travelTime", directions.travelTime);
        directionsInfo.addProperty("distance", directions.distance);
        directionsInfo.addProperty("route", directions.route);
        
        // Add travel recommendations
        JsonObject travelRecommendations = new JsonObject();
        travelRecommendations.addProperty("publicTransport", "BART (Bay Area Rapid Transit) is the most efficient option from SFO to downtown");
        travelRecommendations.addProperty("rideshare", "Uber/Lyft available but expect higher costs during peak hours");
        travelRecommendations.addProperty("parking", "Limited and expensive downtown - recommend public transport");
        travelRecommendations.addProperty("timing", "Allow extra time during rush hours (7-9 AM, 5-7 PM)");
        directionsInfo.add("travelRecommendations", travelRecommendations);
        
        result.add("travelDirections", directionsInfo);
        
        // Add overall event planning summary
        JsonObject eventSummary = new JsonObject();
        eventSummary.addProperty("eventType", "Tech Startup Event - San Francisco");
        eventSummary.addProperty("targetAttendees", 50);
        eventSummary.addProperty("accommodationDates", "August 25-27, 2025");
        
        JsonArray planningChecklist = new JsonArray();
        planningChecklist.add("Finalize Costco bulk purchases for office supplies and catering");
        planningChecklist.add("Book hotel accommodations for out-of-town speakers");
        planningChecklist.add("Prepare discussion topics based on current tech trends");
        planningChecklist.add("Share airport-to-downtown travel guide with attendees");
        planningChecklist.add("Confirm venue capacity and AV equipment requirements");
        planningChecklist.add("Set up registration and check-in process");
        
        eventSummary.add("nextSteps", planningChecklist);
        
        double estimatedTotalBudget = grandTotal + (validHotelPrices > 0 ? (totalHotelCost / validHotelPrices * 2 * 5) : 0); // Assume 5 speakers
        eventSummary.addProperty("estimatedBudget", Math.round(estimatedTotalBudget * 100.0) / 100.0);
        eventSummary.addProperty("budgetBreakdown", "Includes procurement and estimated speaker accommodations");
        
        result.add("eventPlanning", eventSummary);
        
        return result;
    }
}
