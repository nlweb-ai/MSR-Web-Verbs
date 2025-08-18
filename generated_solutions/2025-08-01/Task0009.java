import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0009 {
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
        
        // Step 1: Search for senior-friendly apartments in Tampa, FL with budget $1200-$1800
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult apartmentSearch = redfin.searchApartments("Tampa, FL", 1200, 1800);
        
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
        result.add("senior_housing", apartmentInfo);
        
        // Step 2: Find nearby medical centers and pharmacies for healthcare needs
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult medicalCenters = maps.get_nearestBusinesses("Tampa, FL", "medical center", 10);
        maps_google_com.NearestBusinessesResult pharmacies = maps.get_nearestBusinesses("Tampa, FL", "pharmacy", 10);
        
        JsonObject healthcareInfo = new JsonObject();
        
        JsonArray medicalCentersArray = new JsonArray();
        for (maps_google_com.BusinessInfo center : medicalCenters.businesses) {
            JsonObject centerObj = new JsonObject();
            centerObj.addProperty("name", center.name);
            centerObj.addProperty("address", center.address);
            medicalCentersArray.add(centerObj);
        }
        healthcareInfo.add("medical_centers", medicalCentersArray);
        
        JsonArray pharmaciesArray = new JsonArray();
        for (maps_google_com.BusinessInfo pharmacy : pharmacies.businesses) {
            JsonObject pharmacyObj = new JsonObject();
            pharmacyObj.addProperty("name", pharmacy.name);
            pharmacyObj.addProperty("address", pharmacy.address);
            pharmaciesArray.add(pharmacyObj);
        }
        healthcareInfo.add("pharmacies", pharmaciesArray);
        result.add("healthcare_facilities", healthcareInfo);
        
        // Step 3: Search for emergency supplies at Costco to help prepare for any situations
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult emergencySupplies = costco.searchProducts("emergency supplies");
        
        JsonObject emergencySuppliesInfo = new JsonObject();
        if (emergencySupplies.error != null) {
            emergencySuppliesInfo.addProperty("error", emergencySupplies.error);
        } else {
            JsonArray productsArray = new JsonArray();
            for (costco_com.ProductInfo product : emergencySupplies.products) {
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
            emergencySuppliesInfo.add("emergency_products", productsArray);
        }
        result.add("emergency_preparedness", emergencySuppliesInfo);
        
        // Step 4: Check local Tampa Florida news to keep them informed about community
        News news = new News();
        JsonObject newsInfo = new JsonObject();
        
        try {
            News.NewsResponse tampaNews = news.searchEverything("Tampa Florida local news", "en", 10);
            
            newsInfo.addProperty("status", tampaNews.status);
            newsInfo.addProperty("total_results", tampaNews.totalResults);
            
            JsonArray articlesArray = new JsonArray();
            for (News.NewsArticle article : tampaNews.articles) {
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
            newsInfo.addProperty("error", "Failed to get Tampa local news: " + e.getMessage());
        }
        result.add("local_news", newsInfo);
        
        return result;
    }
}
