import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0084 {
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
        
        // Step 1: Search for gym equipment and protein supplements at Costco
        costco_com costco = new costco_com(context);
        String[] fitnessItems = {"gym equipment", "protein supplements"};
        
        JsonObject costcoInfo = new JsonObject();
        JsonArray fitnessItemsArray = new JsonArray();
        double totalFitnessCost = 0.0;
        
        for (String item : fitnessItems) {
            costco_com.ProductInfo productResult = costco.searchProduct(item);
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("search_term", item);
            
            if (productResult.error != null) {
                itemObj.addProperty("error", productResult.error);
                itemObj.addProperty("price", 0.0);
            } else {
                itemObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    itemObj.addProperty("price", productResult.productPrice.amount);
                    itemObj.addProperty("currency", productResult.productPrice.currency);
                    totalFitnessCost += productResult.productPrice.amount;
                } else {
                    itemObj.addProperty("price", 0.0);
                }
            }
            fitnessItemsArray.add(itemObj);
        }
        costcoInfo.add("fitness_items", fitnessItemsArray);
        costcoInfo.addProperty("total_fitness_cost", totalFitnessCost);
        result.add("costco_fitness_search", costcoInfo);
        
        // Step 2: Calculate budget for other wellness activities
        double totalBudget = 1000.0; // Assumed fitness budget
        double remainingBudget = totalBudget - totalFitnessCost;
        
        JsonObject budgetInfo = new JsonObject();
        budgetInfo.addProperty("total_fitness_budget", totalBudget);
        budgetInfo.addProperty("fitness_equipment_cost", totalFitnessCost);
        budgetInfo.addProperty("remaining_for_wellness_activities", remainingBudget);
        result.add("fitness_budget", budgetInfo);
        
        // Step 3: Find yoga studios and fitness centers near downtown Austin (max 6)
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "downtown Austin, Texas";
        String businessDescription = "yoga studios fitness centers";
        int maxCount = 6;
        
        maps_google_com.NearestBusinessesResult fitnessResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxCount);
        
        JsonObject fitnessLocationsInfo = new JsonObject();
        fitnessLocationsInfo.addProperty("reference_point", fitnessResult.referencePoint);
        fitnessLocationsInfo.addProperty("business_description", fitnessResult.businessDescription);
        
        JsonArray fitnessLocationsArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : fitnessResult.businesses) {
            JsonObject locationObj = new JsonObject();
            locationObj.addProperty("name", business.name);
            locationObj.addProperty("address", business.address);
            fitnessLocationsArray.add(locationObj);
        }
        fitnessLocationsInfo.add("fitness_locations", fitnessLocationsArray);
        result.add("austin_fitness_centers", fitnessLocationsInfo);
        
        // Step 4: Search for apartments for rent in Austin ($1200-$2000)
        redfin_com redfin = new redfin_com(context);
        String location = "Austin, Texas";
        int minRent = 1200;
        int maxRent = 2000;
        
        redfin_com.ApartmentSearchResult apartmentResult = redfin.searchApartments(location, minRent, maxRent);
        
        JsonObject apartmentInfo = new JsonObject();
        apartmentInfo.addProperty("location", location);
        apartmentInfo.addProperty("min_rent", minRent);
        apartmentInfo.addProperty("max_rent", maxRent);
        
        if (apartmentResult.error != null) {
            apartmentInfo.addProperty("error", apartmentResult.error);
            apartmentInfo.add("apartments", new JsonArray());
        } else {
            JsonArray apartmentsArray = new JsonArray();
            for (redfin_com.ApartmentInfo apartment : apartmentResult.apartments) {
                JsonObject apartmentObj = new JsonObject();
                apartmentObj.addProperty("address", apartment.address);
                if (apartment.price != null) {
                    apartmentObj.addProperty("price", apartment.price.amount);
                    apartmentObj.addProperty("currency", apartment.price.currency);
                }
                apartmentObj.addProperty("url", apartment.url);
                apartmentsArray.add(apartmentObj);
            }
            apartmentInfo.add("apartments", apartmentsArray);
        }
        result.add("austin_apartments", apartmentInfo);
        
        // Step 5: Get recent news about fitness trends and wellness tips
        News news = new News();
        String newsQuery = "fitness trends wellness tips";
        
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
            newsInfo.addProperty("error", "Failed to fetch fitness news: " + e.getMessage());
            newsInfo.add("articles", new JsonArray());
        }
        result.add("fitness_wellness_news", newsInfo);
        
        return result;
    }
}
