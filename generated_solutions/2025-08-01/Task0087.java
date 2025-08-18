import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0087 {
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
        
        // Step 1: Search for rental properties in Seattle ($2500-$4000)
        redfin_com redfin = new redfin_com(context);
        String location = "Seattle, Washington";
        int minRent = 2500;
        int maxRent = 4000;
        
        redfin_com.ApartmentSearchResult propertyResult = redfin.searchApartments(location, minRent, maxRent);
        
        JsonObject propertyInfo = new JsonObject();
        propertyInfo.addProperty("location", location);
        propertyInfo.addProperty("min_rent", minRent);
        propertyInfo.addProperty("max_rent", maxRent);
        
        if (propertyResult.error != null) {
            propertyInfo.addProperty("error", propertyResult.error);
            propertyInfo.add("properties", new JsonArray());
            propertyInfo.addProperty("total_properties", 0);
            propertyInfo.addProperty("average_price", 0.0);
        } else {
            JsonArray propertiesArray = new JsonArray();
            double totalPrice = 0.0;
            int priceCount = 0;
            
            for (redfin_com.ApartmentInfo apartment : propertyResult.apartments) {
                JsonObject propertyObj = new JsonObject();
                propertyObj.addProperty("address", apartment.address);
                if (apartment.price != null) {
                    propertyObj.addProperty("price", apartment.price.amount);
                    propertyObj.addProperty("currency", apartment.price.currency);
                    totalPrice += apartment.price.amount;
                    priceCount++;
                }
                propertyObj.addProperty("url", apartment.url);
                propertiesArray.add(propertyObj);
            }
            
            double averagePrice = priceCount > 0 ? totalPrice / priceCount : 0.0;
            propertyInfo.add("properties", propertiesArray);
            propertyInfo.addProperty("total_properties", propertyResult.apartments.size());
            propertyInfo.addProperty("average_price", averagePrice);
        }
        result.add("seattle_rental_properties", propertyInfo);
        
        // Step 2: Find real estate and investment companies near downtown Seattle
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "downtown Seattle, Washington";
        String businessDescription = "real estate investment companies";
        int maxCount = 10;
        
        maps_google_com.NearestBusinessesResult businessResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxCount);
        
        JsonObject businessInfo = new JsonObject();
        businessInfo.addProperty("reference_point", businessResult.referencePoint);
        businessInfo.addProperty("business_description", businessResult.businessDescription);
        
        JsonArray businessesArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : businessResult.businesses) {
            JsonObject businessObj = new JsonObject();
            businessObj.addProperty("name", business.name);
            businessObj.addProperty("address", business.address);
            businessesArray.add(businessObj);
        }
        businessInfo.add("investment_companies", businessesArray);
        result.add("seattle_investment_companies", businessInfo);
        
        // Step 3: Get recent news about Seattle real estate market trends
        News news = new News();
        String newsQuery = "Seattle real estate market trends investment";
        
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
            newsInfo.addProperty("error", "Failed to fetch real estate news: " + e.getMessage());
            newsInfo.add("articles", new JsonArray());
        }
        result.add("seattle_real_estate_news", newsInfo);
        
        // Step 4: Search for real estate investing books in OpenLibrary
        OpenLibrary openLibrary = new OpenLibrary();
        String bookQuery = "real estate investing property investment";
        
        JsonObject booksInfo = new JsonObject();
        try {
            java.util.List<OpenLibrary.BookInfo> books = openLibrary.search(bookQuery, null, null, null, 20, 1);
            booksInfo.addProperty("search_query", bookQuery);
            booksInfo.addProperty("total_books_found", books.size());
            
            JsonArray booksArray = new JsonArray();
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                booksArray.add(bookObj);
            }
            booksInfo.add("investment_books", booksArray);
        } catch (Exception e) {
            booksInfo.addProperty("error", "Failed to search investment books: " + e.getMessage());
            booksInfo.add("investment_books", new JsonArray());
            booksInfo.addProperty("total_books_found", 0);
        }
        result.add("real_estate_investment_books", booksInfo);
        
        // Investment opportunity analysis
        JsonObject analysisInfo = new JsonObject();
        int totalProperties = propertyInfo.has("total_properties") ? propertyInfo.get("total_properties").getAsInt() : 0;
        double avgPrice = propertyInfo.has("average_price") ? propertyInfo.get("average_price").getAsDouble() : 0.0;
        int totalCompanies = businessesArray.size();
        int totalBooks = booksInfo.has("total_books_found") ? booksInfo.get("total_books_found").getAsInt() : 0;
        
        analysisInfo.addProperty("market_research_date", "2025-08-22");
        analysisInfo.addProperty("market_location", "Seattle, Washington");
        analysisInfo.addProperty("available_properties_in_range", totalProperties);
        analysisInfo.addProperty("average_rental_price", avgPrice);
        analysisInfo.addProperty("investment_companies_found", totalCompanies);
        analysisInfo.addProperty("educational_resources_available", totalBooks);
        
        String marketAssessment = getMarketAssessment(totalProperties, avgPrice, totalCompanies);
        analysisInfo.addProperty("market_assessment", marketAssessment);
        
        result.add("investment_analysis", analysisInfo);
        
        return result;
    }
    
    // Helper method to assess market conditions
    private static String getMarketAssessment(int propertyCount, double avgPrice, int companyCount) {
        if (propertyCount > 20 && avgPrice > 0) {
            return "Active market with good availability - " + propertyCount + " properties available, avg price $" + 
                   String.format("%.0f", avgPrice) + ". " + companyCount + " investment companies for consultation.";
        } else if (propertyCount > 10) {
            return "Moderate market activity - " + propertyCount + " properties available. Consider timing and professional consultation.";
        } else if (propertyCount > 0) {
            return "Limited property availability - " + propertyCount + " properties in range. Market may be competitive.";
        } else {
            return "No properties found in specified range. Consider adjusting budget or location parameters.";
        }
    }
}
