import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0090 {
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
        
        // Step 1: Search Costco for office supplies and presentation materials
        costco_com costco = new costco_com(context);
        String[] workshopSupplies = {"office supplies", "presentation materials", "conference supplies"};
        
        JsonObject costcoInfo = new JsonObject();
        JsonArray suppliesArray = new JsonArray();
        double totalSupplyCost = 0.0;
        int expectedAttendees = 25;
        
        for (String supply : workshopSupplies) {
            costco_com.ProductInfo productResult = costco.searchProduct(supply);
            JsonObject supplyObj = new JsonObject();
            supplyObj.addProperty("search_term", supply);
            
            if (productResult.error != null) {
                supplyObj.addProperty("error", productResult.error);
                supplyObj.addProperty("price", 0.0);
            } else {
                supplyObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    supplyObj.addProperty("price", productResult.productPrice.amount);
                    supplyObj.addProperty("currency", productResult.productPrice.currency);
                    totalSupplyCost += productResult.productPrice.amount;
                } else {
                    supplyObj.addProperty("price", 0.0);
                }
            }
            suppliesArray.add(supplyObj);
        }
        
        double costPerParticipant = expectedAttendees > 0 ? totalSupplyCost / expectedAttendees : 0.0;
        
        costcoInfo.add("workshop_supplies", suppliesArray);
        costcoInfo.addProperty("total_supply_cost", totalSupplyCost);
        costcoInfo.addProperty("expected_attendees", expectedAttendees);
        costcoInfo.addProperty("cost_per_participant", costPerParticipant);
        result.add("costco_workshop_supplies", costcoInfo);
        
        // Step 2: Find meeting rooms and conference centers near Atlanta airport
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "Atlanta airport, Georgia";
        String businessDescription = "meeting rooms conference centers";
        int maxCount = 10;
        
        maps_google_com.NearestBusinessesResult venueResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxCount);
        
        JsonObject venueInfo = new JsonObject();
        venueInfo.addProperty("reference_point", venueResult.referencePoint);
        venueInfo.addProperty("business_description", venueResult.businessDescription);
        venueInfo.addProperty("location_rationale", "Near airport for easy access for out-of-town attendees");
        
        JsonArray venuesArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : venueResult.businesses) {
            JsonObject venueObj = new JsonObject();
            venueObj.addProperty("name", business.name);
            venueObj.addProperty("address", business.address);
            venuesArray.add(venueObj);
        }
        venueInfo.add("conference_venues", venuesArray);
        venueInfo.addProperty("total_venues_found", venuesArray.size());
        result.add("atlanta_conference_venues", venueInfo);
        
        // Step 3: Search for business and professional development books in OpenLibrary
        OpenLibrary openLibrary = new OpenLibrary();
        String booksQuery = "business professional development leadership management";
        
        JsonObject booksInfo = new JsonObject();
        try {
            java.util.List<OpenLibrary.BookInfo> books = openLibrary.search(booksQuery, null, null, null, 25, 1);
            booksInfo.addProperty("search_query", booksQuery);
            booksInfo.addProperty("total_books_found", books.size());
            
            JsonArray booksArray = new JsonArray();
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                booksArray.add(bookObj);
            }
            booksInfo.add("professional_development_books", booksArray);
            booksInfo.addProperty("reading_list_status", "Ready for participant distribution");
        } catch (Exception e) {
            booksInfo.addProperty("error", "Failed to search professional development books: " + e.getMessage());
            booksInfo.add("professional_development_books", new JsonArray());
            booksInfo.addProperty("total_books_found", 0);
        }
        result.add("openlibrary_business_books", booksInfo);
        
        // Step 4: Get recent news about professional development trends
        News news = new News();
        String newsQuery = "professional development trends best practices workplace training";
        
        JsonObject newsInfo = new JsonObject();
        try {
            News.NewsResponse newsResult = news.searchEverything(newsQuery);
            newsInfo.addProperty("status", newsResult.status);
            newsInfo.addProperty("total_results", newsResult.totalResults);
            newsInfo.addProperty("search_query", newsQuery);
            
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
            newsInfo.addProperty("error", "Failed to fetch professional development news: " + e.getMessage());
            newsInfo.add("articles", new JsonArray());
        }
        result.add("professional_development_news", newsInfo);
        
        // Workshop planning summary
        JsonObject workshopSummary = new JsonObject();
        int totalBooks = booksInfo.has("total_books_found") ? booksInfo.get("total_books_found").getAsInt() : 0;
        int totalVenues = venuesArray.size();
        
        workshopSummary.addProperty("event_type", "Professional Development Workshop");
        workshopSummary.addProperty("location", "Atlanta, Georgia (near airport)");
        workshopSummary.addProperty("workshop_date", "2025-08-19");
        workshopSummary.addProperty("expected_attendees", expectedAttendees);
        workshopSummary.addProperty("supply_cost_per_participant", costPerParticipant);
        workshopSummary.addProperty("total_supply_budget", totalSupplyCost);
        workshopSummary.addProperty("venue_options_available", totalVenues);
        workshopSummary.addProperty("recommended_reading_books", totalBooks);
        
        String workshopRecommendation = getWorkshopRecommendation(costPerParticipant, totalVenues, totalBooks);
        workshopSummary.addProperty("planning_recommendation", workshopRecommendation);
        
        // Create curriculum suggestions based on news trends
        JsonArray curriculumSuggestions = new JsonArray();
        curriculumSuggestions.add("Leadership and team management skills");
        curriculumSuggestions.add("Digital transformation and remote work best practices");
        curriculumSuggestions.add("Communication and presentation techniques");
        curriculumSuggestions.add("Professional networking and career development");
        curriculumSuggestions.add("Industry trends and future skills requirements");
        workshopSummary.add("suggested_curriculum_topics", curriculumSuggestions);
        
        result.add("workshop_planning_summary", workshopSummary);
        
        return result;
    }
    
    // Helper method to provide workshop planning recommendations
    private static String getWorkshopRecommendation(double costPerParticipant, int venueCount, int bookCount) {
        StringBuilder recommendation = new StringBuilder();
        
        if (costPerParticipant <= 50.0) {
            recommendation.append("Excellent cost efficiency - $").append(String.format("%.2f", costPerParticipant))
                          .append(" per participant for supplies. ");
        } else if (costPerParticipant <= 100.0) {
            recommendation.append("Moderate supply costs - $").append(String.format("%.2f", costPerParticipant))
                          .append(" per participant. Consider bulk purchasing. ");
        } else {
            recommendation.append("High supply costs - $").append(String.format("%.2f", costPerParticipant))
                          .append(" per participant. Review budget or reduce supply requirements. ");
        }
        
        if (venueCount >= 8) {
            recommendation.append("Excellent venue availability - ").append(venueCount)
                          .append(" options near airport for attendee convenience. ");
        } else if (venueCount >= 5) {
            recommendation.append("Good venue selection - ").append(venueCount)
                          .append(" conference centers available. ");
        } else {
            recommendation.append("Limited venue options - consider expanding search area or alternative locations. ");
        }
        
        if (bookCount >= 20) {
            recommendation.append("Comprehensive reading list available - ").append(bookCount)
                          .append(" professional development books for participant resources.");
        } else if (bookCount >= 10) {
            recommendation.append("Good selection of reading materials - ").append(bookCount)
                          .append(" books for recommended reading list.");
        } else {
            recommendation.append("Limited book resources - supplement with online materials or industry publications.");
        }
        
        return recommendation.toString();
    }
}
