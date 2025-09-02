import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class AnchorageTask0003 {
    static BrowserContext context = null;
    static java.util.Scanner scanner= new java.util.Scanner(System.in);
    public static void main(String[] args) {
        
        try (Playwright playwright = Playwright.create()) {
            String userDataDir = System.getProperty("user.home") +"\\AppData\\Local\\Google\\Chrome\\User Data\\Default";

            BrowserType.LaunchPersistentContextOptions options = new BrowserType.LaunchPersistentContextOptions()
                .setChannel("chrome")
                .setHeadless(false)
                .setArgs(java.util.Arrays.asList(
                    "--disable-blink-features=AutomationControlled",
                    //"--no-sandbox",
                    //"--disable-web-security",
                    "--disable-infobars",
                    "--disable-extensions",
                    "--start-maximized"
                ));

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
       The current function body addresses the new requirement for kids winter jackets at Costco.
    */
    static JsonObject automate(BrowserContext context) {
        
        // Strategy: The task has a new requirement - "we want to see kids winter jackets in the Anchorage costco. Please get a list of the jackets."
        // This is a concrete shopping request that requires:
        // 1. Setting the Costco warehouse location to Anchorage
        // 2. Searching for kids winter jackets 
        // 3. Getting product details including names and prices
        // This will help the users know what winter clothing options are available for children during their September trip to Alaska.
        
        costco_com costcoInstance = new costco_com(context);
        NLWeb nlwebInstance = new NLWeb();
        
        JsonObject finalResult = new JsonObject();
        JsonArray factsCollected = new JsonArray();
        
        try {
            // Step 1: Set preferred warehouse to Anchorage, Alaska
            costco_com.WarehouseStatusResult warehouseResult = costcoInstance.setPreferredWarehouse("Anchorage, Alaska");
            
            JsonObject warehouseFact = new JsonObject();
            warehouseFact.addProperty("type", "costco_warehouse_setup");
            warehouseFact.addProperty("location", "Anchorage, Alaska");
            warehouseFact.addProperty("status", warehouseResult.status);
            if (warehouseResult.error != null) {
                warehouseFact.addProperty("error", warehouseResult.error);
            }
            factsCollected.add(warehouseFact);
            
            // Step 2: Search for kids winter jackets
            costco_com.ProductListResult jacketResults = costcoInstance.searchProducts("kids winter jackets");
            
            JsonObject jacketSearchFact = new JsonObject();
            jacketSearchFact.addProperty("type", "costco_kids_winter_jackets");
            jacketSearchFact.addProperty("search_term", "kids winter jackets");
            jacketSearchFact.addProperty("location", "Anchorage Costco");
            
            if (jacketResults.error != null) {
                jacketSearchFact.addProperty("error", jacketResults.error);
            } else {
                JsonArray jacketArray = new JsonArray();
                for (costco_com.ProductInfo jacket : jacketResults.products) {
                    JsonObject jacketInfo = new JsonObject();
                    jacketInfo.addProperty("name", jacket.productName);
                    if (jacket.productPrice != null) {
                        jacketInfo.addProperty("price", jacket.productPrice.toString());
                    }
                    if (jacket.error != null) {
                        jacketInfo.addProperty("error", jacket.error);
                    }
                    jacketArray.add(jacketInfo);
                }
                jacketSearchFact.add("jackets", jacketArray);
                jacketSearchFact.addProperty("jackets_found", jacketResults.products.size());
            }
            factsCollected.add(jacketSearchFact);
            
            // Step 3: Also search for more specific terms to get comprehensive results
            String[] searchTerms = {
                "children winter coats",
                "toddler winter jackets", 
                "youth winter outerwear",
                "kids snow jackets"
            };
            
            for (String searchTerm : searchTerms) {
                costco_com.ProductListResult additionalResults = costcoInstance.searchProducts(searchTerm);
                
                JsonObject additionalSearchFact = new JsonObject();
                additionalSearchFact.addProperty("type", "costco_additional_winter_clothing");
                additionalSearchFact.addProperty("search_term", searchTerm);
                additionalSearchFact.addProperty("location", "Anchorage Costco");
                
                if (additionalResults.error != null) {
                    additionalSearchFact.addProperty("error", additionalResults.error);
                } else {
                    JsonArray additionalArray = new JsonArray();
                    for (costco_com.ProductInfo item : additionalResults.products) {
                        JsonObject itemInfo = new JsonObject();
                        itemInfo.addProperty("name", item.productName);
                        if (item.productPrice != null) {
                            itemInfo.addProperty("price", item.productPrice.toString());
                        }
                        if (item.error != null) {
                            itemInfo.addProperty("error", item.error);
                        }
                        additionalArray.add(itemInfo);
                    }
                    additionalSearchFact.add("products", additionalArray);
                    additionalSearchFact.addProperty("products_found", additionalResults.products.size());
                }
                factsCollected.add(additionalSearchFact);
            }
            
            // Step 4: Get weather context for jacket recommendations using NLWeb
            String weatherQuery = "What should kids wear in Anchorage Alaska in September? What type of winter clothing is recommended for children visiting Anchorage in early September?";
            String weatherResponse = nlwebInstance.AskNLWeb(weatherQuery);
            
            JsonObject weatherFact = new JsonObject();
            weatherFact.addProperty("type", "kids_clothing_weather_advice");
            weatherFact.addProperty("query", weatherQuery);
            weatherFact.addProperty("advice", weatherResponse);
            factsCollected.add(weatherFact);
            
            // Step 5: Get Costco store information for Anchorage
            String storeQuery = "What is the address and operating hours of Costco in Anchorage Alaska? When can we visit the store during our trip September 2-5, 2025?";
            String storeResponse = nlwebInstance.AskNLWeb(storeQuery);
            
            JsonObject storeFact = new JsonObject();
            storeFact.addProperty("type", "anchorage_costco_store_info");
            storeFact.addProperty("query", storeQuery);
            storeFact.addProperty("store_info", storeResponse);
            factsCollected.add(storeFact);
            
            finalResult.addProperty("refinement_focus", "Kids winter jackets at Anchorage Costco");
            finalResult.addProperty("search_terms_used", searchTerms.length + 1);
            finalResult.add("facts_collected", factsCollected);
            
            // Append to known_facts.md
            appendToKnownFacts(factsCollected);
            
        } catch (Exception e) {
            JsonObject errorResult = new JsonObject();
            errorResult.addProperty("error", "Failed to complete Costco jacket search: " + e.getMessage());
            finalResult.add("error_details", errorResult);
        }
        
        return finalResult;
    }
    
    private static void appendToKnownFacts(JsonArray facts) {
        try {
            String factsPath = "tasks\\2025-08-27\\known_facts.md";
            String timestamp = java.time.LocalDateTime.now().toString();
            
            StringBuilder content = new StringBuilder();
            content.append("\n\n## Facts collected on ").append(timestamp).append("\n");
            content.append("### Kids Winter Jackets at Anchorage Costco\n\n");
            
            Gson gson = new GsonBuilder()
                .disableHtmlEscaping()
                .setPrettyPrinting()
                .create();
            
            for (int i = 0; i < facts.size(); i++) {
                content.append("```json\n");
                content.append(gson.toJson(facts.get(i)));
                content.append("\n```\n\n");
            }
            
            Files.write(Paths.get(factsPath), content.toString().getBytes(StandardCharsets.UTF_8), 
                       StandardOpenOption.CREATE, StandardOpenOption.APPEND);
                       
        } catch (IOException e) {
            System.err.println("Failed to append to known_facts.md: " + e.getMessage());
        }
    }
}
