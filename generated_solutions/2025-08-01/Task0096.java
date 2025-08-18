import java.io.IOException;
import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0096 {
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
        
        // Film festival details
        LocalDate festivalDate = LocalDate.of(2025, 8, 31);
        String festivalLocation = "Portland, Oregon";
        double totalBudget = 2000.0;
        
        // Step 1: Search for audio-visual equipment and projectors at Costco
        costco_com costco = new costco_com(context);
        String[] avEquipment = {"projector", "audio equipment", "speakers", "screen"};
        
        JsonObject equipmentInfo = new JsonObject();
        JsonArray equipmentArray = new JsonArray();
        double totalEquipmentCost = 0.0;
        
        for (String equipment : avEquipment) {
            costco_com.ProductInfo productResult = costco.searchProduct(equipment);
            JsonObject equipmentObj = new JsonObject();
            equipmentObj.addProperty("equipment_type", equipment);
            
            if (productResult.error != null) {
                equipmentObj.addProperty("error", productResult.error);
                double estimatedCost = getEstimatedEquipmentCost(equipment);
                equipmentObj.addProperty("estimated_cost", estimatedCost);
                totalEquipmentCost += estimatedCost;
            } else {
                equipmentObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    equipmentObj.addProperty("cost", productResult.productPrice.amount);
                    equipmentObj.addProperty("currency", productResult.productPrice.currency);
                    totalEquipmentCost += productResult.productPrice.amount;
                } else {
                    double estimatedCost = getEstimatedEquipmentCost(equipment);
                    equipmentObj.addProperty("estimated_cost", estimatedCost);
                    totalEquipmentCost += estimatedCost;
                }
            }
            equipmentArray.add(equipmentObj);
        }
        
        // Calculate how many screening rooms can be afforded
        double costPerScreeningRoom = totalEquipmentCost;
        int maxScreeningRooms = (int) Math.floor(totalBudget / costPerScreeningRoom);
        double remainingBudget = totalBudget - (maxScreeningRooms * costPerScreeningRoom);
        
        equipmentInfo.add("av_equipment", equipmentArray);
        equipmentInfo.addProperty("total_equipment_cost_per_room", totalEquipmentCost);
        equipmentInfo.addProperty("total_budget", totalBudget);
        equipmentInfo.addProperty("max_screening_rooms_affordable", maxScreeningRooms);
        equipmentInfo.addProperty("remaining_budget", remainingBudget);
        equipmentInfo.addProperty("budget_utilization_percentage", ((totalBudget - remainingBudget) / totalBudget) * 100);
        result.add("equipment_analysis", equipmentInfo);
        
        // Step 2: Find movie theaters and event venues near downtown Portland
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "downtown Portland, Oregon";
        String businessDescription = "movie theaters event venues";
        int maxVenues = 8;
        
        maps_google_com.NearestBusinessesResult venuesResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxVenues);
        
        JsonObject venueInfo = new JsonObject();
        venueInfo.addProperty("reference_point", venuesResult.referencePoint);
        venueInfo.addProperty("search_type", venuesResult.businessDescription);
        venueInfo.addProperty("purpose", "Film festival venue location scouting");
        
        JsonArray venuesArray = new JsonArray();
        for (maps_google_com.BusinessInfo venue : venuesResult.businesses) {
            JsonObject venueObj = new JsonObject();
            venueObj.addProperty("name", venue.name);
            venueObj.addProperty("address", venue.address);
            
            // Categorize venue type based on name
            String venueName = venue.name.toLowerCase();
            String venueType = "other";
            if (venueName.contains("theater") || venueName.contains("cinema") || venueName.contains("movie")) {
                venueType = "movie_theater";
            } else if (venueName.contains("center") || venueName.contains("hall") || venueName.contains("venue")) {
                venueType = "event_venue";
            } else if (venueName.contains("studio") || venueName.contains("screening")) {
                venueType = "screening_room";
            }
            
            venueObj.addProperty("venue_type", venueType);
            venuesArray.add(venueObj);
        }
        venueInfo.add("potential_venues", venuesArray);
        venueInfo.addProperty("total_venues_found", venuesArray.size());
        result.add("venue_information", venueInfo);
        
        // Step 3: Search Amazon for film festival promotional materials
        amazon_com amazon = new amazon_com(context);
        String[] promotionalItems = {"movie posters", "promotional banners", "film festival merchandise"};
        
        JsonObject promotionalInfo = new JsonObject();
        JsonArray promotionalArray = new JsonArray();
        
        for (String item : promotionalItems) {
            amazon_com.CartResult cartResult = amazon.addItemToCart(item);
            JsonObject promoObj = new JsonObject();
            promoObj.addProperty("promotional_item", item);
            
            if (cartResult.items != null && !cartResult.items.isEmpty()) {
                amazon_com.CartItem firstItem = cartResult.items.get(0);
                promoObj.addProperty("product_name", firstItem.itemName);
                if (firstItem.price != null) {
                    promoObj.addProperty("price", firstItem.price.amount);
                    promoObj.addProperty("currency", firstItem.price.currency);
                } else {
                    promoObj.addProperty("price", "Price not available");
                }
                promoObj.addProperty("status", "Found on Amazon");
            } else {
                promoObj.addProperty("status", "Not found - consider custom printing");
                promoObj.addProperty("estimated_cost", getEstimatedPromotionalCost(item));
            }
            promotionalArray.add(promoObj);
        }
        
        promotionalInfo.add("promotional_materials", promotionalArray);
        promotionalInfo.addProperty("purpose", "Festival marketing and branding materials");
        result.add("promotional_materials", promotionalInfo);
        
        // Step 4: Get recent news about independent film festivals
        News news = new News();
        JsonObject newsInfo = new JsonObject();
        
        try {
            News.NewsResponse newsResponse = news.searchEverything("independent film festival", "en", 5);
            
            newsInfo.addProperty("search_query", "independent film festival");
            newsInfo.addProperty("purpose", "Current trends and best practices for promoting emerging filmmakers");
            newsInfo.addProperty("total_results", newsResponse.totalResults);
            newsInfo.addProperty("status", newsResponse.status);
            
            JsonArray articlesArray = new JsonArray();
            if (newsResponse.articles != null) {
                for (News.NewsArticle article : newsResponse.articles) {
                    JsonObject articleObj = new JsonObject();
                    articleObj.addProperty("title", article.title);
                    articleObj.addProperty("description", article.description);
                    articleObj.addProperty("url", article.url);
                    articleObj.addProperty("source", article.source);
                    articleObj.addProperty("published_date", article.publishedAt != null ? article.publishedAt.toString() : "Unknown");
                    articlesArray.add(articleObj);
                }
            }
            newsInfo.add("recent_articles", articlesArray);
            newsInfo.addProperty("articles_found", articlesArray.size());
            
        } catch (IOException | InterruptedException e) {
            newsInfo.addProperty("error", "Failed to fetch news: " + e.getMessage());
            newsInfo.addProperty("recommendation", "Research film festival trends manually through industry publications");
        }
        
        result.add("industry_news", newsInfo);
        
        // Film festival planning summary and recommendations
        JsonObject festivalSummary = new JsonObject();
        festivalSummary.addProperty("festival_type", "Independent Film Festival Screening");
        festivalSummary.addProperty("location", festivalLocation);
        festivalSummary.addProperty("date", festivalDate.toString());
        festivalSummary.addProperty("budget", totalBudget);
        festivalSummary.addProperty("max_screening_rooms", maxScreeningRooms);
        festivalSummary.addProperty("venues_identified", venuesArray.size());
        
        // Festival recommendations
        StringBuilder recommendations = new StringBuilder();
        recommendations.append("Portland's vibrant arts scene makes it ideal for independent film festivals. ");
        
        if (maxScreeningRooms >= 2) {
            recommendations.append("Budget allows for ").append(maxScreeningRooms).append(" screening rooms - can host multiple films simultaneously. ");
        } else if (maxScreeningRooms == 1) {
            recommendations.append("Budget allows for 1 screening room - consider sequential screenings throughout the day. ");
        } else {
            recommendations.append("Budget insufficient for professional equipment - consider partnerships with existing venues. ");
        }
        
        if (venuesArray.size() >= 5) {
            recommendations.append("Good variety of venue options available - negotiate group rates. ");
        } else {
            recommendations.append("Limited venue options - expand search area or consider outdoor screenings. ");
        }
        
        recommendations.append("Focus on emerging filmmakers and create networking opportunities. ");
        recommendations.append("Use promotional materials to build buzz and attract film industry professionals.");
        
        festivalSummary.addProperty("planning_recommendations", recommendations.toString());
        
        // Festival logistics and planning
        JsonObject festivalLogistics = new JsonObject();
        festivalLogistics.addProperty("equipment_setup", "Professional AV equipment for quality screenings");
        festivalLogistics.addProperty("venue_requirements", "Seating for 50-200 guests depending on venue size");
        festivalLogistics.addProperty("promotional_strategy", "Posters, programs, and digital marketing for filmmaker exposure");
        festivalLogistics.addProperty("target_audience", "Independent filmmakers, industry professionals, film enthusiasts");
        
        JsonArray screeningSchedule = new JsonArray();
        if (maxScreeningRooms >= 2) {
            screeningSchedule.add("Room 1: Short films and documentaries");
            screeningSchedule.add("Room 2: Feature films and premieres");
            if (maxScreeningRooms >= 3) {
                screeningSchedule.add("Room 3: Q&A sessions and filmmaker panels");
            }
        } else {
            screeningSchedule.add("Single room: Rotating schedule of all film categories");
        }
        festivalLogistics.add("screening_schedule", screeningSchedule);
        
        festivalSummary.add("festival_logistics", festivalLogistics);
        
        // Success metrics and goals
        JsonObject successMetrics = new JsonObject();
        successMetrics.addProperty("primary_goal", "Showcase emerging filmmakers and independent cinema");
        successMetrics.addProperty("expected_attendance", maxScreeningRooms * 100); // Estimate 100 people per room capacity
        successMetrics.addProperty("filmmaker_networking", "Connect filmmakers with industry professionals and audiences");
        successMetrics.addProperty("community_impact", "Strengthen Portland's independent film scene");
        
        if (remainingBudget > 200) {
            successMetrics.addProperty("additional_opportunities", "Use remaining budget for filmmaker awards or refreshments");
        } else {
            successMetrics.addProperty("budget_optimization", "Budget fully utilized for core screening infrastructure");
        }
        
        festivalSummary.add("success_metrics", successMetrics);
        
        result.add("film_festival_summary", festivalSummary);
        
        return result;
    }
    
    // Helper method to estimate equipment costs when Costco search fails
    private static double getEstimatedEquipmentCost(String equipment) {
        switch (equipment.toLowerCase()) {
            case "projector":
                return 800.0;
            case "audio equipment":
                return 400.0;
            case "speakers":
                return 300.0;
            case "screen":
                return 200.0;
            default:
                return 300.0;
        }
    }
    
    // Helper method to estimate promotional material costs
    private static double getEstimatedPromotionalCost(String item) {
        switch (item.toLowerCase()) {
            case "movie posters":
                return 50.0;
            case "festival programs":
                return 75.0;
            case "promotional banners":
                return 100.0;
            case "film festival merchandise":
                return 150.0;
            default:
                return 75.0;
        }
    }
}
