import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0010 {
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
        
        // Step 1: Clear Amazon cart to start fresh with health-focused purchases
        amazon_com amazon = new amazon_com(context);
        amazon.clearCart();
        
        JsonObject cartInfo = new JsonObject();
        cartInfo.addProperty("status", "Cart cleared successfully for health-focused shopping");
        result.add("cart_cleanup", cartInfo);
        
        // Step 2: Search for fitness equipment at Costco to set up a home gym
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult fitnessEquipment = costco.searchProducts("fitness equipment");
        
        JsonObject fitnessEquipmentInfo = new JsonObject();
        if (fitnessEquipment.error != null) {
            fitnessEquipmentInfo.addProperty("error", fitnessEquipment.error);
        } else {
            JsonArray productsArray = new JsonArray();
            for (costco_com.ProductInfo product : fitnessEquipment.products) {
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
            fitnessEquipmentInfo.add("home_gym_equipment", productsArray);
        }
        result.add("costco_fitness_shopping", fitnessEquipmentInfo);
        
        // Step 3: Find gyms and fitness centers near Austin, TX for professional workouts
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult gyms = maps.get_nearestBusinesses("Austin, TX", "gym", 15);
        maps_google_com.NearestBusinessesResult fitnessCenter = maps.get_nearestBusinesses("Austin, TX", "fitness center", 10);
        
        JsonObject fitnessVenuesInfo = new JsonObject();
        
        JsonArray gymsArray = new JsonArray();
        for (maps_google_com.BusinessInfo gym : gyms.businesses) {
            JsonObject gymObj = new JsonObject();
            gymObj.addProperty("name", gym.name);
            gymObj.addProperty("address", gym.address);
            gymsArray.add(gymObj);
        }
        fitnessVenuesInfo.add("gyms", gymsArray);
        
        JsonArray fitnessCentersArray = new JsonArray();
        for (maps_google_com.BusinessInfo center : fitnessCenter.businesses) {
            JsonObject centerObj = new JsonObject();
            centerObj.addProperty("name", center.name);
            centerObj.addProperty("address", center.address);
            fitnessCentersArray.add(centerObj);
        }
        fitnessVenuesInfo.add("fitness_centers", fitnessCentersArray);
        result.add("professional_workout_venues", fitnessVenuesInfo);
        
        // Step 4: Search for fitness and nutrition videos to learn proper techniques and healthy eating
        youtube_com youtube = new youtube_com(context);
        List<youtube_com.YouTubeVideoInfo> fitnessVideos = youtube.searchVideos("fitness workout techniques");
        List<youtube_com.YouTubeVideoInfo> nutritionVideos = youtube.searchVideos("healthy nutrition eating habits");
        
        JsonObject educationalContent = new JsonObject();
        
        JsonArray fitnessVideosArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : fitnessVideos) {
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
            fitnessVideosArray.add(videoObj);
        }
        educationalContent.add("fitness_technique_videos", fitnessVideosArray);
        
        JsonArray nutritionVideosArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : nutritionVideos) {
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
            nutritionVideosArray.add(videoObj);
        }
        educationalContent.add("nutrition_videos", nutritionVideosArray);
        result.add("educational_content", educationalContent);
        
        return result;
    }
}
