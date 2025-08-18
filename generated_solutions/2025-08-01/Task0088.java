import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0088 {
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
        
        // Step 1: Get NASA's Astronomy Picture of the Day for party inspiration
        Nasa nasa = new Nasa();
        String targetDate = "2025-08-16"; // August 16, 2025
        
        JsonObject apodInfo = new JsonObject();
        try {
            Nasa.ApodResult apodResult = nasa.getApod(targetDate, true);
            apodInfo.addProperty("title", apodResult.title);
            apodInfo.addProperty("url", apodResult.url);
            apodInfo.addProperty("explanation", apodResult.explanation);
            apodInfo.addProperty("date", apodResult.date.toString());
            
            // Determine party theme based on APOD content
            String partyTheme = determinePartyTheme(apodResult.title, apodResult.explanation);
            apodInfo.addProperty("party_theme", partyTheme);
            apodInfo.addProperty("decoration_inspiration", getDecorationIdeas(partyTheme));
        } catch (IOException | InterruptedException e) {
            apodInfo.addProperty("error", "Failed to fetch APOD: " + e.getMessage());
            apodInfo.addProperty("party_theme", "general space"); // default theme
            apodInfo.addProperty("decoration_inspiration", "Use general space decorations with stars and rockets");
        }
        result.add("nasa_apod_inspiration", apodInfo);
        
        // Step 2: Search Costco for party supplies within $300 budget
        costco_com costco = new costco_com(context);
        String partyTheme = apodInfo.has("party_theme") ? apodInfo.get("party_theme").getAsString() : "space";
        String[] partyItems = getPartyItemSearchTerms(partyTheme);
        
        JsonObject costcoInfo = new JsonObject();
        JsonArray partySuppliesArray = new JsonArray();
        double totalCostcoSpending = 0.0;
        double budget = 300.0;
        
        for (String item : partyItems) {
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
                    totalCostcoSpending += productResult.productPrice.amount;
                } else {
                    itemObj.addProperty("price", 0.0);
                }
            }
            partySuppliesArray.add(itemObj);
        }
        
        costcoInfo.add("party_supplies", partySuppliesArray);
        costcoInfo.addProperty("total_costco_spending", totalCostcoSpending);
        costcoInfo.addProperty("budget", budget);
        costcoInfo.addProperty("remaining_budget", budget - totalCostcoSpending);
        result.add("costco_party_supplies", costcoInfo);
        
        // Step 3: Add space-themed birthday cake decorations to Amazon cart
        amazon_com amazon = new amazon_com(context);
        String cakeDecorations = "space birthday cake decorations " + partyTheme;
        
        amazon_com.CartResult cakeItems = amazon.addItemToCart(cakeDecorations);
        
        JsonObject cakeInfo = new JsonObject();
        cakeInfo.addProperty("search_term", cakeDecorations);
        JsonArray cakeDecorationsArray = new JsonArray();
        for (amazon_com.CartItem item : cakeItems.items) {
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("item_name", item.itemName);
            if (item.price != null) {
                itemObj.addProperty("price", item.price.amount);
                itemObj.addProperty("currency", item.price.currency);
            }
            cakeDecorationsArray.add(itemObj);
        }
        cakeInfo.add("cake_decorations", cakeDecorationsArray);
        result.add("amazon_cake_decorations", cakeInfo);
        
        // Step 4: Search for children's space and astronomy books in OpenLibrary
        OpenLibrary openLibrary = new OpenLibrary();
        String booksQuery = "children space astronomy books kids";
        
        JsonObject booksInfo = new JsonObject();
        try {
            java.util.List<OpenLibrary.BookInfo> books = openLibrary.search(booksQuery, null, null, null, 15, 1);
            booksInfo.addProperty("search_query", booksQuery);
            booksInfo.addProperty("total_books_found", books.size());
            
            JsonArray booksArray = new JsonArray();
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                booksArray.add(bookObj);
            }
            booksInfo.add("space_books", booksArray);
        } catch (Exception e) {
            booksInfo.addProperty("error", "Failed to search space books: " + e.getMessage());
            booksInfo.add("space_books", new JsonArray());
            booksInfo.addProperty("total_books_found", 0);
        }
        result.add("openlibrary_space_books", booksInfo);
        
        // Birthday party planning summary
        JsonObject partySummary = new JsonObject();
        partySummary.addProperty("event_type", "Astronomy-Themed Birthday Party");
        partySummary.addProperty("location", "Phoenix, Arizona");
        partySummary.addProperty("date", "2025-08-16");
        partySummary.addProperty("theme", apodInfo.has("party_theme") ? apodInfo.get("party_theme").getAsString() : "space");
        partySummary.addProperty("budget", budget);
        partySummary.addProperty("costco_spending", totalCostcoSpending);
        partySummary.addProperty("remaining_budget", budget - totalCostcoSpending);
        
        int totalBooks = booksInfo.has("total_books_found") ? booksInfo.get("total_books_found").getAsInt() : 0;
        partySummary.addProperty("educational_books_available", totalBooks);
        partySummary.addProperty("party_favors_suggestion", "Create space-themed gift bags with " + totalBooks + " book options");
        
        result.add("party_planning_summary", partySummary);
        
        return result;
    }
    
    // Helper method to determine party theme based on APOD content
    private static String determinePartyTheme(String title, String explanation) {
        String content = (title + " " + explanation).toLowerCase();
        if (content.contains("planet") || content.contains("mars") || content.contains("venus") || 
            content.contains("jupiter") || content.contains("saturn")) {
            return "planets";
        } else if (content.contains("galaxy") || content.contains("galaxies") || content.contains("milky way") ||
                   content.contains("spiral") || content.contains("nebula")) {
            return "galaxies";
        } else if (content.contains("star") || content.contains("constellation") || content.contains("sun")) {
            return "stars";
        } else if (content.contains("moon") || content.contains("lunar") || content.contains("crater")) {
            return "moon";
        } else {
            return "general space";
        }
    }
    
    // Helper method to get decoration ideas based on theme
    private static String getDecorationIdeas(String theme) {
        switch (theme) {
            case "planets":
                return "Use planet-shaped balloons, solar system banners, and planetary orbit decorations";
            case "galaxies":
                return "Create swirling galaxy patterns, use purple/blue color scheme, spiral decorations";
            case "stars":
                return "Hang star garlands, use constellation maps, golden star decorations";
            case "moon":
                return "Use moon phase decorations, crater-like textures, silver/white color scheme";
            default:
                return "General space theme with rockets, astronauts, and mixed celestial objects";
        }
    }
    
    // Helper method to get search terms for party supplies based on theme
    private static String[] getPartyItemSearchTerms(String theme) {
        switch (theme) {
            case "planets":
                return new String[]{"telescope", "planet party supplies", "solar system decorations"};
            case "galaxies":
                return new String[]{"telescope", "galaxy party supplies", "space toys"};
            case "stars":
                return new String[]{"telescope", "star party supplies", "constellation decorations"};
            case "moon":
                return new String[]{"telescope", "moon party supplies", "space toys"};
            default:
                return new String[]{"telescope", "space party supplies", "astronomy toys"};
        }
    }
}
