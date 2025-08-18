import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0006 {
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
        
        // Step 1: Search for apartments in Denver within price range $2000-$3000
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult apartmentSearch = redfin.searchApartments("Denver, CO", 2000, 3000);
        
        JsonObject apartmentInfo = new JsonObject();
        if (apartmentSearch.error != null) {
            apartmentInfo.addProperty("error", apartmentSearch.error);
        } else {
            JsonArray apartmentsArray = new JsonArray();
            for (redfin_com.ApartmentInfo apartment : apartmentSearch.apartments) {
                JsonObject apartmentObj = new JsonObject();
                apartmentObj.addProperty("address", apartment.address);
                apartmentObj.addProperty("url", apartment.url);
                if (apartment.price != null) {
                    JsonObject priceObj = new JsonObject();
                    priceObj.addProperty("amount", apartment.price.amount);
                    priceObj.addProperty("currency", apartment.price.currency);
                    apartmentObj.add("price", priceObj);
                }
                apartmentsArray.add(apartmentObj);
            }
            apartmentInfo.add("apartments", apartmentsArray);
        }
        result.add("housing_search", apartmentInfo);
        
        // Step 2: Get directions from Denver International Airport to downtown Denver
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.DirectionResult directions = maps.get_direction("Denver International Airport, CO", "downtown Denver, CO");
        
        JsonObject directionsInfo = new JsonObject();
        directionsInfo.addProperty("travel_time", directions.travelTime);
        directionsInfo.addProperty("distance", directions.distance);
        directionsInfo.addProperty("route", directions.route);
        result.add("airport_directions", directionsInfo);
        
        // Step 3: Buy moving boxes and supplies from Costco for the relocation
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult movingSupplies = costco.searchProducts("moving boxes");
        
        JsonObject movingSuppliesInfo = new JsonObject();
        if (movingSupplies.error != null) {
            movingSuppliesInfo.addProperty("error", movingSupplies.error);
        } else {
            JsonArray productsArray = new JsonArray();
            for (costco_com.ProductInfo product : movingSupplies.products) {
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
            movingSuppliesInfo.add("moving_supplies", productsArray);
        }
        result.add("costco_shopping", movingSuppliesInfo);
        
        // Step 4: Check business news about Denver to understand local economy and job market
        News news = new News();
        JsonObject newsInfo = new JsonObject();
        
        try {
            News.NewsResponse denverNews = news.searchEverything("Denver business economy", "en", 10);
            
            newsInfo.addProperty("status", denverNews.status);
            newsInfo.addProperty("total_results", denverNews.totalResults);
            
            JsonArray articlesArray = new JsonArray();
            for (News.NewsArticle article : denverNews.articles) {
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
            newsInfo.addProperty("error", "Failed to get Denver business news: " + e.getMessage());
        }
        result.add("local_business_news", newsInfo);
        
        return result;
    }
}
