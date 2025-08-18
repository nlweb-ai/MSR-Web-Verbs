import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0002 {
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
        
        // Step 1: Search for apartments in Bellevue, WA within budget range $2500-$3500
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult apartmentSearch = redfin.searchApartments("Bellevue, WA", 2500, 3500);
        
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
        result.add("apartment_search", apartmentInfo);
        
        // Step 2: Set preferred Costco warehouse location to be close to Bellevue
        costco_com costco = new costco_com(context);
        costco_com.WarehouseStatusResult warehouseResult = costco.setPreferredWarehouse("Bellevue, WA");
        
        JsonObject warehouseInfo = new JsonObject();
        if (warehouseResult.error != null) {
            warehouseInfo.addProperty("error", warehouseResult.error);
        } else {
            warehouseInfo.addProperty("status", warehouseResult.status);
        }
        result.add("warehouse_setup", warehouseInfo);
        
        // Step 3: Search for organic food options at Costco for healthy eating
        costco_com.ProductListResult organicProducts = costco.searchProducts("organic food");
        
        JsonObject organicFoodInfo = new JsonObject();
        if (organicProducts.error != null) {
            organicFoodInfo.addProperty("error", organicProducts.error);
        } else {
            JsonArray productsArray = new JsonArray();
            for (costco_com.ProductInfo product : organicProducts.products) {
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
            organicFoodInfo.add("organic_products", productsArray);
        }
        result.add("costco_shopping", organicFoodInfo);
        
        // Step 4: Add a coffee maker to Amazon cart for the new place
        amazon_com amazon = new amazon_com(context);
        amazon_com.CartResult cartResult = amazon.addItemToCart("coffee maker");
        
        JsonObject amazonInfo = new JsonObject();
        JsonArray cartItemsArray = new JsonArray();
        for (amazon_com.CartItem item : cartResult.items) {
            JsonObject itemObj = new JsonObject();
            itemObj.addProperty("item_name", item.itemName);
            if (item.price != null) {
                JsonObject priceObj = new JsonObject();
                priceObj.addProperty("amount", item.price.amount);
                priceObj.addProperty("currency", item.price.currency);
                itemObj.add("price", priceObj);
            }
            cartItemsArray.add(itemObj);
        }
        amazonInfo.add("cart_items", cartItemsArray);
        result.add("amazon_cart", amazonInfo);
        
        return result;
    }
}
