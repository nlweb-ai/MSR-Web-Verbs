import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0092 {
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
        
        // Step 1: Search Costco for presentation equipment and tech gadgets
        costco_com costco = new costco_com(context);
        String[] techEquipment = {"presentation equipment", "tech gadgets", "projectors"};
        
        JsonObject costcoInfo = new JsonObject();
        JsonArray equipmentArray = new JsonArray();
        double totalTechCost = 0.0;
        double techBudget = 1500.0;
        
        for (String equipment : techEquipment) {
            costco_com.ProductInfo productResult = costco.searchProduct(equipment);
            JsonObject equipmentObj = new JsonObject();
            equipmentObj.addProperty("search_term", equipment);
            
            if (productResult.error != null) {
                equipmentObj.addProperty("error", productResult.error);
                equipmentObj.addProperty("price", 0.0);
            } else {
                equipmentObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    equipmentObj.addProperty("price", productResult.productPrice.amount);
                    equipmentObj.addProperty("currency", productResult.productPrice.currency);
                    totalTechCost += productResult.productPrice.amount;
                } else {
                    equipmentObj.addProperty("price", 0.0);
                }
            }
            equipmentArray.add(equipmentObj);
        }
        
        // Budget allocation analysis
        JsonObject budgetAllocation = new JsonObject();
        budgetAllocation.addProperty("total_budget", techBudget);
        budgetAllocation.addProperty("equipment_cost", totalTechCost);
        budgetAllocation.addProperty("remaining_budget", techBudget - totalTechCost);
        budgetAllocation.addProperty("budget_utilization_percent", (totalTechCost / techBudget) * 100);
        
        costcoInfo.add("tech_equipment", equipmentArray);
        costcoInfo.add("budget_analysis", budgetAllocation);
        result.add("costco_tech_equipment", costcoInfo);
        
        // Step 2: Find co-working spaces and startup incubators near Silicon Valley
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "Silicon Valley, San Jose, California";
        String businessDescription = "co-working spaces startup incubators";
        int maxCount = 15;
        
        maps_google_com.NearestBusinessesResult workspaceResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxCount);
        
        JsonObject workspaceInfo = new JsonObject();
        workspaceInfo.addProperty("reference_point", workspaceResult.referencePoint);
        workspaceInfo.addProperty("business_description", workspaceResult.businessDescription);
        workspaceInfo.addProperty("purpose", "Networking and potential startup relocation");
        
        JsonArray workspacesArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : workspaceResult.businesses) {
            JsonObject workspaceObj = new JsonObject();
            workspaceObj.addProperty("name", business.name);
            workspaceObj.addProperty("address", business.address);
            workspacesArray.add(workspaceObj);
        }
        workspaceInfo.add("startup_workspaces", workspacesArray);
        workspaceInfo.addProperty("total_options", workspacesArray.size());
        result.add("silicon_valley_workspaces", workspaceInfo);
        
        // Step 3: Get recent news about technology startups and venture capital
        News news = new News();
        String newsQuery = "technology startups venture capital market trends investor interests";
        
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
            newsInfo.addProperty("error", "Failed to fetch startup news: " + e.getMessage());
            newsInfo.add("articles", new JsonArray());
        }
        result.add("startup_market_news", newsInfo);
        
        // Step 4: Search for entrepreneurship and startup books in OpenLibrary
        OpenLibrary openLibrary = new OpenLibrary();
        String booksQuery = "entrepreneurship startup business strategy pitch techniques";
        
        JsonObject booksInfo = new JsonObject();
        try {
            java.util.List<OpenLibrary.BookInfo> books = openLibrary.search(booksQuery, null, null, null, 20, 1);
            booksInfo.addProperty("search_query", booksQuery);
            booksInfo.addProperty("total_books_found", books.size());
            
            JsonArray booksArray = new JsonArray();
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                booksArray.add(bookObj);
            }
            booksInfo.add("entrepreneurship_books", booksArray);
        } catch (Exception e) {
            booksInfo.addProperty("error", "Failed to search entrepreneurship books: " + e.getMessage());
            booksInfo.add("entrepreneurship_books", new JsonArray());
            booksInfo.addProperty("total_books_found", 0);
        }
        result.add("openlibrary_business_books", booksInfo);
        
        // Startup pitch event summary
        JsonObject pitchSummary = new JsonObject();
        pitchSummary.addProperty("event_type", "Technology Startup Pitch Event");
        pitchSummary.addProperty("location", "San Jose, California");
        pitchSummary.addProperty("event_date", "2025-08-27");
        pitchSummary.addProperty("tech_budget", techBudget);
        pitchSummary.addProperty("equipment_investment", totalTechCost);
        pitchSummary.addProperty("budget_remaining", techBudget - totalTechCost);
        pitchSummary.addProperty("networking_opportunities", workspacesArray.size());
        
        int totalBooks = booksInfo.has("total_books_found") ? booksInfo.get("total_books_found").getAsInt() : 0;
        pitchSummary.addProperty("strategy_resources", totalBooks);
        
        String pitchRecommendation = createPitchRecommendation(totalTechCost, techBudget, workspacesArray.size(), totalBooks);
        pitchSummary.addProperty("pitch_preparation_recommendation", pitchRecommendation);
        
        // Market analysis based on news
        JsonObject marketAnalysis = new JsonObject();
        marketAnalysis.addProperty("analysis_date", "2025-08-27");
        marketAnalysis.addProperty("focus_areas", "Technology trends, investor preferences, market opportunities");
        marketAnalysis.addProperty("preparation_status", "Ready for pitch refinement based on current market data");
        pitchSummary.add("market_intelligence", marketAnalysis);
        
        result.add("startup_pitch_summary", pitchSummary);
        
        return result;
    }
    
    // Helper method to create pitch preparation recommendations
    private static String createPitchRecommendation(double equipmentCost, double budget, int workspaces, int books) {
        StringBuilder recommendation = new StringBuilder();
        
        double budgetUtilization = (equipmentCost / budget) * 100;
        
        if (budgetUtilization <= 60.0) {
            recommendation.append("Excellent budget management - ").append(String.format("%.1f", budgetUtilization))
                          .append("% budget used. Consider additional demo equipment or marketing materials. ");
        } else if (budgetUtilization <= 80.0) {
            recommendation.append("Good budget allocation - ").append(String.format("%.1f", budgetUtilization))
                          .append("% budget used. Focus on pitch content refinement. ");
        } else {
            recommendation.append("High equipment investment - ").append(String.format("%.1f", budgetUtilization))
                          .append("% budget used. Ensure ROI on premium equipment. ");
        }
        
        if (workspaces >= 10) {
            recommendation.append("Outstanding networking potential - ").append(workspaces)
                          .append(" startup spaces available for connections and relocation research. ");
        } else if (workspaces >= 5) {
            recommendation.append("Good networking options - ").append(workspaces)
                          .append(" workspaces to explore for partnerships. ");
        } else {
            recommendation.append("Limited workspace options - expand networking to online communities and events. ");
        }
        
        if (books >= 15) {
            recommendation.append("Comprehensive learning resources - ").append(books)
                          .append(" books available for strategy refinement and pitch improvement.");
        } else {
            recommendation.append("Supplement with online resources and mentorship programs for additional guidance.");
        }
        
        return recommendation.toString();
    }
}
