import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0040 {
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
        JsonObject output = new JsonObject();
        
        try {
            // Step 1: Search for school supplies and backpacks at Costco
            costco_com costco = new costco_com(context);
            JsonObject costcoResults = new JsonObject();
            
            try {
                // Search for school supplies and backpacks
                costco_com.ProductListResult schoolSupplies = costco.searchProducts("school supplies backpacks");
                
                JsonArray schoolSuppliesArray = new JsonArray();
                
                if (schoolSupplies != null && schoolSupplies.products != null) {
                    for (costco_com.ProductInfo product : schoolSupplies.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("name", product.productName);
                        if (product.productPrice != null) {
                            productObj.addProperty("price", product.productPrice.amount);
                            productObj.addProperty("currency", product.productPrice.currency);
                        }
                        productObj.addProperty("category", "School Supplies");
                        productObj.addProperty("bulk_savings", "Yes - Costco bulk pricing");
                        
                        // Add value assessment
                        if (product.productPrice != null && product.productPrice.amount > 0) {
                            double price = product.productPrice.amount;
                            if (price <= 20) {
                                productObj.addProperty("value_rating", "Excellent - Great budget option");
                            } else if (price <= 50) {
                                productObj.addProperty("value_rating", "Good - Reasonable price for quality");
                            } else {
                                productObj.addProperty("value_rating", "Premium - Higher cost but likely durable");
                            }
                        }
                        
                        if (product.error != null) {
                            productObj.addProperty("error", product.error);
                        }
                        schoolSuppliesArray.add(productObj);
                    }
                }
                
                costcoResults.add("school_supplies", schoolSuppliesArray);
                costcoResults.addProperty("total_products", schoolSuppliesArray.size());
                costcoResults.addProperty("store", "Costco Wholesale");
                costcoResults.addProperty("shopping_date", "August 7, 2025");
                costcoResults.addProperty("bulk_advantage", "Costco offers bulk quantities perfect for families with multiple children");
                
            } catch (Exception e) {
                costcoResults.addProperty("error", "Failed to search Costco products: " + e.getMessage());
            }
            
            output.add("costco_school_supplies", costcoResults);
            
            // Step 2: Add lunchbox to Amazon cart
            amazon_com amazon = new amazon_com(context);
            JsonObject amazonResults = new JsonObject();
            
            try {
                // Add lunchbox to cart
                amazon_com.CartResult cartResult = amazon.addItemToCart("lunchbox");
                
                if (cartResult != null) {
                    JsonObject cartInfo = new JsonObject();
                    cartInfo.addProperty("item_added", "Lunchbox");
                    cartInfo.addProperty("cart_status", cartResult.items != null ? "Successfully added" : "Failed to add");
                    cartInfo.addProperty("total_items", cartResult.items != null ? cartResult.items.size() : 0);
                    
                    // Calculate total price from cart items
                    double totalPrice = 0.0;
                    if (cartResult.items != null) {
                        for (amazon_com.CartItem item : cartResult.items) {
                            if (item.price != null) {
                                totalPrice += item.price.amount;
                            }
                        }
                    }
                    cartInfo.addProperty("estimated_total", totalPrice);
                    
                    amazonResults.add("cart_update", cartInfo);
                    
                    // Lunchbox shopping tips
                    JsonArray lunchboxTips = new JsonArray();
                    lunchboxTips.add("Look for insulated lunchboxes to keep food at proper temperature");
                    lunchboxTips.add("Choose easy-to-clean materials like wipeable fabric or plastic");
                    lunchboxTips.add("Consider size based on your child's appetite and age");
                    lunchboxTips.add("Check for BPA-free materials for food safety");
                    lunchboxTips.add("Look for compartments to separate different foods");
                    lunchboxTips.add("Choose designs your child will be excited to use");
                    
                    amazonResults.add("lunchbox_selection_tips", lunchboxTips);
                }
                
                amazonResults.addProperty("shopping_platform", "Amazon");
                amazonResults.addProperty("convenience_factor", "Prime delivery available for quick back-to-school shopping");
                
            } catch (Exception e) {
                amazonResults.addProperty("error", "Failed to add lunchbox to cart: " + e.getMessage());
            }
            
            output.add("amazon_lunchbox_cart", amazonResults);
            
            // Step 3: Get back-to-school news and tips
            News news = new News();
            JsonObject newsResults = new JsonObject();
            
            try {
                // Search for back-to-school related news from the past week
                News.NewsResponse backToSchoolNews = news.searchEverything("back to school tips 2025");
                News.NewsResponse parentingTips = news.searchEverything("parenting back to school preparation");
                News.NewsResponse schoolSupplyTrends = news.searchEverything("school supplies trends 2025");
                
                JsonArray newsArticles = new JsonArray();
                
                // Process back-to-school news
                if (backToSchoolNews != null && backToSchoolNews.articles != null) {
                    for (News.NewsArticle article : backToSchoolNews.articles) {
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("headline", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("source", article.source);
                        articleObj.addProperty("category", "Back-to-School Tips");
                        articleObj.addProperty("relevance", "High - directly applicable to parent preparation");
                        newsArticles.add(articleObj);
                    }
                }
                
                // Process parenting tips
                if (parentingTips != null && parentingTips.articles != null) {
                    for (News.NewsArticle article : parentingTips.articles) {
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("headline", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("source", article.source);
                        articleObj.addProperty("category", "Parenting & Preparation");
                        articleObj.addProperty("relevance", "Medium - general parenting advice");
                        newsArticles.add(articleObj);
                    }
                }
                
                // Process school supply trends
                if (schoolSupplyTrends != null && schoolSupplyTrends.articles != null) {
                    for (News.NewsArticle article : schoolSupplyTrends.articles) {
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("headline", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("source", article.source);
                        articleObj.addProperty("category", "Shopping Trends");
                        articleObj.addProperty("relevance", "High - shopping guidance and trends");
                        newsArticles.add(articleObj);
                    }
                }
                
                newsResults.add("back_to_school_articles", newsArticles);
                newsResults.addProperty("total_articles", newsArticles.size());
                newsResults.addProperty("news_focus", "Comprehensive back-to-school preparation and shopping guidance");
                
            } catch (Exception e) {
                newsResults.addProperty("error", "Failed to fetch back-to-school news: " + e.getMessage());
            }
            
            output.add("back_to_school_news", newsResults);
            
            // Step 4: Get weather forecast for Dallas on August 7, 2025
            OpenWeather weather = new OpenWeather();
            JsonObject weatherResults = new JsonObject();
            
            try {
                // Dallas coordinates: 32.7767, -96.7970
                double lat = 32.7767;
                double lon = -96.7970;
                
                // Get weather forecast for shopping day
                OpenWeather.CurrentWeatherData dallasForecast = weather.getCurrentWeather(lat, lon);
                
                JsonObject weatherObj = new JsonObject();
                if (dallasForecast != null) {
                    weatherObj.addProperty("temperature", dallasForecast.getTemperature());
                    weatherObj.addProperty("feels_like", dallasForecast.getFeelsLike());
                    weatherObj.addProperty("humidity", dallasForecast.getHumidity());
                    weatherObj.addProperty("weather_condition", dallasForecast.getCondition());
                    weatherObj.addProperty("weather_description", dallasForecast.getDescription());
                    weatherObj.addProperty("wind_speed", dallasForecast.getWindSpeed());
                    weatherObj.addProperty("cloudiness", dallasForecast.getCloudiness());
                    
                    // Weather-based shopping recommendations
                    JsonArray weatherRecommendations = new JsonArray();
                    
                    double temp = dallasForecast.getTemperature();
                    
                    if (temp >= 85) {
                        weatherRecommendations.add("Hot day in Dallas - shop early morning or evening for comfort");
                        weatherRecommendations.add("Stay hydrated while shopping and use air-conditioned stores");
                        weatherRecommendations.add("Consider online shopping with curbside pickup to avoid heat");
                    } else if (temp >= 70 && temp <= 84) {
                        weatherRecommendations.add("Pleasant weather for shopping - perfect day for back-to-school trips");
                        weatherRecommendations.add("Comfortable temperature for walking between stores");
                    } else {
                        weatherRecommendations.add("Cooler weather - great for extended shopping trips");
                        weatherRecommendations.add("Consider light layers for air-conditioned stores");
                    }
                    
                    if (dallasForecast.getHumidity() > 60) {
                        weatherRecommendations.add("High humidity - stay hydrated while shopping");
                    }
                    
                    weatherObj.add("shopping_recommendations", weatherRecommendations);
                }
                
                weatherResults.add("dallas_weather", weatherObj);
                weatherResults.addProperty("location", "Dallas, TX");
                weatherResults.addProperty("shopping_date", "August 7, 2025");
                weatherResults.addProperty("coordinates", "(" + lat + ", " + lon + ")");
                
            } catch (Exception e) {
                weatherResults.addProperty("error", "Failed to get weather forecast: " + e.getMessage());
            }
            
            output.add("weather_planning", weatherResults);
            
            // Step 5: Create comprehensive back-to-school shopping guide
            JsonObject shoppingGuide = new JsonObject();
            shoppingGuide.addProperty("guide_title", "Complete Back-to-School Shopping Guide for Dallas Parents");
            shoppingGuide.addProperty("shopping_date", "Thursday, August 7, 2025");
            shoppingGuide.addProperty("location", "Dallas, Texas");
            
            // Shopping strategy
            JsonObject shoppingStrategy = new JsonObject();
            
            JsonArray costcoRecommendations = new JsonArray();
            costcoRecommendations.add("Visit Costco first for bulk school supplies - best value for families");
            costcoRecommendations.add("Bring membership card and check for back-to-school coupons");
            costcoRecommendations.add("Consider splitting bulk purchases with other families");
            costcoRecommendations.add("Stock up on basics like paper, pencils, and notebooks");
            
            shoppingStrategy.add("costco_shopping_tips", costcoRecommendations);
            
            JsonArray amazonStrategy = new JsonArray();
            amazonStrategy.add("Use Amazon for specialized items like themed lunchboxes");
            amazonStrategy.add("Check Prime delivery options for last-minute needs");
            amazonStrategy.add("Read reviews before purchasing lunch containers");
            amazonStrategy.add("Consider Subscribe & Save for recurring school supplies");
            
            shoppingStrategy.add("amazon_shopping_tips", amazonStrategy);
            
            shoppingGuide.add("shopping_strategy", shoppingStrategy);
            
            // Weather considerations
            JsonObject weatherConsiderations = new JsonObject();
            if (weatherResults.has("dallas_weather")) {
                JsonObject weatherData = weatherResults.get("dallas_weather").getAsJsonObject();
                if (weatherData.has("temperature")) {
                    weatherConsiderations.addProperty("temperature", weatherData.get("temperature").getAsDouble() + "°F");
                    weatherConsiderations.addProperty("conditions", weatherData.get("weather_description").getAsString());
                    
                    // Best shopping times
                    JsonArray shoppingTimes = new JsonArray();
                    double temp = weatherData.get("temperature").getAsDouble();
                    
                    if (temp >= 85) {
                        shoppingTimes.add("8:00 AM - 10:00 AM (cooler morning hours)");
                        shoppingTimes.add("7:00 PM - 9:00 PM (evening when it cools down)");
                        weatherConsiderations.addProperty("parking_tip", "Park in shaded areas and use sunshades");
                    } else {
                        shoppingTimes.add("10:00 AM - 12:00 PM (comfortable mid-morning)");
                        shoppingTimes.add("2:00 PM - 6:00 PM (pleasant afternoon shopping)");
                        weatherConsiderations.addProperty("parking_tip", "Weather is comfortable for regular parking");
                    }
                    
                    weatherConsiderations.add("recommended_shopping_times", shoppingTimes);
                }
            }
            
            shoppingGuide.add("weather_considerations", weatherConsiderations);
            
            // News-based tips compilation
            JsonArray expertTips = new JsonArray();
            expertTips.add("Start shopping early to avoid crowds and ensure stock availability");
            expertTips.add("Make a checklist organized by store to maximize efficiency");
            expertTips.add("Set a budget and stick to it - back-to-school expenses add up quickly");
            expertTips.add("Involve kids in choosing age-appropriate items they'll actually use");
            expertTips.add("Check school supply lists carefully - requirements vary by grade");
            expertTips.add("Consider quality over quantity for items used daily like backpacks");
            expertTips.add("Take advantage of tax-free weekends if available in Texas");
            expertTips.add("Buy basics in bulk but specialized items individually");
            
            shoppingGuide.add("expert_shopping_tips", expertTips);
            
            // Budget planning
            JsonObject budgetPlanning = new JsonObject();
            budgetPlanning.addProperty("costco_budget_range", "$150-$300 for bulk school supplies (family of 2-3 kids)");
            budgetPlanning.addProperty("amazon_budget_range", "$25-$75 for specialized items like lunchboxes");
            budgetPlanning.addProperty("total_estimated_budget", "$175-$375 depending on family size and needs");
            
            JsonArray budgetTips = new JsonArray();
            budgetTips.add("Compare unit prices even at Costco to ensure best value");
            budgetTips.add("Check Amazon price history for items you can wait on");
            budgetTips.add("Use store credit cards for additional discounts if available");
            budgetTips.add("Keep receipts for potential returns of unused items");
            
            budgetPlanning.add("money_saving_tips", budgetTips);
            
            shoppingGuide.add("budget_planning", budgetPlanning);
            
            // Essential items checklist
            JsonObject essentialItems = new JsonObject();
            
            JsonArray costcoEssentials = new JsonArray();
            costcoEssentials.add("Notebooks and composition books (bulk packs)");
            costcoEssentials.add("Pencils, pens, and erasers (variety packs)");
            costcoEssentials.add("Colored pencils and markers (large sets)");
            costcoEssentials.add("Folders and binders (multi-packs)");
            costcoEssentials.add("Paper - copy paper, construction paper");
            costcoEssentials.add("Backpacks (durable, good warranty)");
            costcoEssentials.add("Glue sticks and tape (bulk packages)");
            
            essentialItems.add("costco_essentials", costcoEssentials);
            
            JsonArray amazonEssentials = new JsonArray();
            amazonEssentials.add("Insulated lunchbox with compartments");
            amazonEssentials.add("Water bottle (BPA-free, easy to clean)");
            amazonEssentials.add("Personalized name labels for belongings");
            amazonEssentials.add("Calculator (if required by grade level)");
            amazonEssentials.add("Specialty items specific to your child's needs");
            
            essentialItems.add("amazon_essentials", amazonEssentials);
            
            shoppingGuide.add("essential_items_checklist", essentialItems);
            
            // Parent preparation timeline
            JsonArray timeline = new JsonArray();
            timeline.add("2 weeks before school: Review school supply lists and create shopping list");
            timeline.add("1 week before school (August 7): Main shopping trip to Costco and Amazon orders");
            timeline.add("3 days before school: Check for any missing items and make final purchases");
            timeline.add("1 day before school: Organize supplies and pack backpacks with your child");
            
            shoppingGuide.add("preparation_timeline", timeline);
            
            output.add("complete_shopping_guide", shoppingGuide);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while creating back-to-school shopping guide: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
