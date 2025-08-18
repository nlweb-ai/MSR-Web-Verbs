import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0021 {
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
        JsonObject mainResult = new JsonObject();
        
        // 1. Search for presentation equipment at Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult equipmentResults = costco.searchProducts("presentation equipment");
        
        JsonArray equipmentArray = new JsonArray();
        if (equipmentResults.error == null && equipmentResults.products != null) {
            for (costco_com.ProductInfo product : equipmentResults.products) {
                JsonObject productObj = new JsonObject();
                productObj.addProperty("productName", product.productName);
                if (product.productPrice != null) {
                    productObj.addProperty("price", product.productPrice.amount);
                    productObj.addProperty("currency", product.productPrice.currency);
                }
                if (product.error != null) {
                    productObj.addProperty("error", product.error);
                }
                equipmentArray.add(productObj);
            }
        } else if (equipmentResults.error != null) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", equipmentResults.error);
            equipmentArray.add(errorObj);
        }
        mainResult.add("costco_equipment", equipmentArray);
        
        // 2. Search YouTube for "scientific presentation skills"
        youtube_com youtube = new youtube_com(context);
        List<youtube_com.YouTubeVideoInfo> videoResults = youtube.searchVideos("scientific presentation skills");
        
        JsonArray videoArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : videoResults) {
            JsonObject videoObj = new JsonObject();
            videoObj.addProperty("title", video.title);
            videoObj.addProperty("url", video.url);
            // Format Duration as hh:mm:ss or mm:ss
            long s = video.length.getSeconds();
            long h = s / 3600;
            long m = (s % 3600) / 60;
            long sec = s % 60;
            String lenStr = h > 0 ? String.format("%d:%02d:%02d", h, m, sec) : String.format("%d:%02d", m, sec);
            videoObj.addProperty("length", lenStr);
            videoArray.add(videoObj);
        }
        mainResult.add("youtube_videos", videoArray);
        
        // 3. Get NASA's Astronomy Picture of the Day for August 5th, 2025
        Nasa nasa = new Nasa();
        JsonObject apodObj = new JsonObject();
        
        try {
            Nasa.ApodResult apod = nasa.getApod("2025-08-05", true);
            if (apod != null) {
                apodObj.addProperty("title", apod.title);
                apodObj.addProperty("url", apod.url);
                apodObj.addProperty("explanation", apod.explanation);
                if (apod.date != null) {
                    apodObj.addProperty("date", apod.date.toString());
                }
            }
        } catch (IOException | InterruptedException e) {
            apodObj.addProperty("error", "Failed to retrieve NASA APOD: " + e.getMessage());
        }
        mainResult.add("nasa_apod", apodObj);
        
        // 4. Find conference centers and meeting facilities near downtown Boston
        // Using Google Maps to find nearby businesses
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult businessResults = maps.get_nearestBusinesses(
            "downtown Boston, MA", 
            "conference center", 
            10
        );
        
        JsonArray businessArray = new JsonArray();
        if (businessResults != null && businessResults.businesses != null) {
            for (maps_google_com.BusinessInfo business : businessResults.businesses) {
                JsonObject businessObj = new JsonObject();
                businessObj.addProperty("name", business.name);
                businessObj.addProperty("address", business.address);
                businessArray.add(businessObj);
            }
        }
        mainResult.add("boston_conference_centers", businessArray);
        
        return mainResult;
    }
}
