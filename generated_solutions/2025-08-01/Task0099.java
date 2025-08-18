import java.io.IOException;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0099 {
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
        
        // Art therapy workshop details
        LocalDate workshopDate = LocalDate.of(2025, 8, 14);
        String workshopLocation = "Tampa, Florida";
        int seniorParticipants = 20;
        
        // Step 1: Search for art supplies and craft materials at Costco
        costco_com costco = new costco_com(context);
        String[] artSupplies = {"paint brushes", "acrylic paints", "canvases", "art supplies"};
        
        JsonObject artSuppliesInfo = new JsonObject();
        JsonArray suppliesArray = new JsonArray();
        double totalSupplyCost = 0.0;
        
        for (String supply : artSupplies) {
            costco_com.ProductInfo productResult = costco.searchProduct(supply);
            JsonObject supplyObj = new JsonObject();
            supplyObj.addProperty("supply_type", supply);
            
            if (productResult.error != null) {
                supplyObj.addProperty("error", productResult.error);
                double estimatedCost = getEstimatedArtSupplyCost(supply);
                supplyObj.addProperty("estimated_cost", estimatedCost);
                totalSupplyCost += estimatedCost;
            } else {
                supplyObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    supplyObj.addProperty("cost", productResult.productPrice.amount);
                    supplyObj.addProperty("currency", productResult.productPrice.currency);
                    totalSupplyCost += productResult.productPrice.amount;
                } else {
                    double estimatedCost = getEstimatedArtSupplyCost(supply);
                    supplyObj.addProperty("estimated_cost", estimatedCost);
                    totalSupplyCost += estimatedCost;
                }
            }
            suppliesArray.add(supplyObj);
        }
        
        // Calculate materials budget for 20 senior participants
        double costPerParticipant = totalSupplyCost / seniorParticipants;
        double totalMaterialsBudget = totalSupplyCost * 1.2; // Add 20% buffer for additional materials
        
        artSuppliesInfo.add("basic_art_supplies", suppliesArray);
        artSuppliesInfo.addProperty("total_basic_supply_cost", totalSupplyCost);
        artSuppliesInfo.addProperty("participants", seniorParticipants);
        artSuppliesInfo.addProperty("cost_per_participant", costPerParticipant);
        artSuppliesInfo.addProperty("total_materials_budget", totalMaterialsBudget);
        artSuppliesInfo.addProperty("budget_includes", "Basic supplies plus 20% buffer for additional materials");
        result.add("costco_art_supplies", artSuppliesInfo);
        
        // Step 2: Add therapeutic art supplies to Amazon cart
        amazon_com amazon = new amazon_com(context);
        String[] therapeuticSupplies = {"colored pencils", "sketchbooks", "art therapy materials", "senior-friendly art supplies"};
        
        JsonObject therapeuticSuppliesInfo = new JsonObject();
        JsonArray amazonSuppliesArray = new JsonArray();
        double totalAmazonCost = 0.0;
        
        for (String supply : therapeuticSupplies) {
            amazon_com.CartResult cartResult = amazon.addItemToCart(supply);
            JsonObject supplyObj = new JsonObject();
            supplyObj.addProperty("therapeutic_supply", supply);
            
            if (cartResult.items != null && !cartResult.items.isEmpty()) {
                amazon_com.CartItem firstItem = cartResult.items.get(0);
                supplyObj.addProperty("product_name", firstItem.itemName);
                if (firstItem.price != null) {
                    supplyObj.addProperty("price", firstItem.price.amount);
                    supplyObj.addProperty("currency", firstItem.price.currency);
                    totalAmazonCost += firstItem.price.amount;
                } else {
                    supplyObj.addProperty("price", "Price not available");
                    double estimatedCost = getEstimatedTherapeuticSupplyCost(supply);
                    totalAmazonCost += estimatedCost;
                }
                supplyObj.addProperty("status", "Added to Amazon cart");
            } else {
                supplyObj.addProperty("status", "Not found on Amazon");
                double estimatedCost = getEstimatedTherapeuticSupplyCost(supply);
                supplyObj.addProperty("estimated_cost", estimatedCost);
                totalAmazonCost += estimatedCost;
            }
            amazonSuppliesArray.add(supplyObj);
        }
        
        double totalAllSupplies = totalMaterialsBudget + totalAmazonCost;
        double finalCostPerParticipant = totalAllSupplies / seniorParticipants;
        
        therapeuticSuppliesInfo.add("therapeutic_art_supplies", amazonSuppliesArray);
        therapeuticSuppliesInfo.addProperty("amazon_supplies_cost", totalAmazonCost);
        therapeuticSuppliesInfo.addProperty("total_all_supplies_cost", totalAllSupplies);
        therapeuticSuppliesInfo.addProperty("final_cost_per_participant", finalCostPerParticipant);
        therapeuticSuppliesInfo.addProperty("purpose", "Specialized supplies for therapeutic art activities");
        result.add("amazon_therapeutic_supplies", therapeuticSuppliesInfo);
        
        // Step 3: Find senior centers and community arts facilities near downtown Tampa
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "downtown Tampa, Florida";
        String businessDescription = "senior centers community arts facilities";
        int maxLocations = 10;
        
        maps_google_com.NearestBusinessesResult venuesResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxLocations);
        
        JsonObject venueInfo = new JsonObject();
        venueInfo.addProperty("reference_point", venuesResult.referencePoint);
        venueInfo.addProperty("search_type", venuesResult.businessDescription);
        venueInfo.addProperty("purpose", "Secure accessible venue for art therapy workshop");
        
        JsonArray venuesArray = new JsonArray();
        for (maps_google_com.BusinessInfo venue : venuesResult.businesses) {
            JsonObject venueObj = new JsonObject();
            venueObj.addProperty("name", venue.name);
            venueObj.addProperty("address", venue.address);
            
            // Categorize venue type based on name
            String venueName = venue.name.toLowerCase();
            String venueType = "other";
            if (venueName.contains("senior") || venueName.contains("elderly") || venueName.contains("aging")) {
                venueType = "senior_center";
            } else if (venueName.contains("arts") || venueName.contains("art") || venueName.contains("creative")) {
                venueType = "arts_facility";
            } else if (venueName.contains("community") || venueName.contains("center")) {
                venueType = "community_center";
            } else if (venueName.contains("health") || venueName.contains("wellness")) {
                venueType = "wellness_center";
            }
            
            venueObj.addProperty("venue_type", venueType);
            venueObj.addProperty("accessibility_focus", venueType.equals("senior_center") ? "high" : "medium");
            venueObj.addProperty("suitability_for_seniors", assessSeniorSuitability(venueName, venueType));
            venuesArray.add(venueObj);
        }
        venueInfo.add("potential_venues", venuesArray);
        venueInfo.addProperty("total_venues_found", venuesArray.size());
        result.add("venue_options", venueInfo);
        
        // Step 4: Search for art therapy and creative aging books in OpenLibrary
        OpenLibrary openLibrary = new OpenLibrary();
        JsonObject educationalResourcesInfo = new JsonObject();
        
        try {
            String[] therapyTopics = {"art therapy", "creative aging", "art for seniors", "therapeutic activities"};
            JsonArray booksArray = new JsonArray();
            
            for (String topic : therapyTopics) {
                List<OpenLibrary.BookInfo> books = openLibrary.search(topic, null, null, null, 4, 1);
                
                JsonObject topicObj = new JsonObject();
                topicObj.addProperty("topic", topic);
                
                JsonArray topicBooksArray = new JsonArray();
                for (OpenLibrary.BookInfo book : books) {
                    JsonObject bookObj = new JsonObject();
                    bookObj.addProperty("title", book.title);
                    topicBooksArray.add(bookObj);
                }
                topicObj.add("recommended_books", topicBooksArray);
                topicObj.addProperty("books_found", topicBooksArray.size());
                booksArray.add(topicObj);
            }
            
            educationalResourcesInfo.addProperty("purpose", "Design evidence-based activities promoting mental wellness and artistic expression");
            educationalResourcesInfo.add("educational_categories", booksArray);
            
            // Get additional art therapy subjects
            List<OpenLibrary.SubjectInfo> artTherapySubjects = openLibrary.getSubject("art therapy", false, 6, 0);
            JsonArray subjectsArray = new JsonArray();
            for (OpenLibrary.SubjectInfo subject : artTherapySubjects) {
                subjectsArray.add(subject.info);
            }
            educationalResourcesInfo.add("related_art_therapy_subjects", subjectsArray);
            
        } catch (IOException | InterruptedException e) {
            educationalResourcesInfo.addProperty("error", "Failed to fetch educational resources: " + e.getMessage());
            educationalResourcesInfo.addProperty("recommendation", "Use professional art therapy guidelines and creative aging research");
        }
        
        result.add("educational_resources", educationalResourcesInfo);
        
        // Art therapy workshop summary and recommendations
        JsonObject workshopSummary = new JsonObject();
        workshopSummary.addProperty("workshop_type", "Art Therapy Workshop for Seniors");
        workshopSummary.addProperty("location", workshopLocation);
        workshopSummary.addProperty("date", workshopDate.toString());
        workshopSummary.addProperty("participants", seniorParticipants);
        workshopSummary.addProperty("total_supply_cost", totalAllSupplies);
        workshopSummary.addProperty("cost_per_participant", finalCostPerParticipant);
        workshopSummary.addProperty("venues_identified", venuesArray.size());
        
        // Workshop recommendations
        StringBuilder recommendations = new StringBuilder();
        recommendations.append("Tampa's active senior community provides excellent opportunity for therapeutic art programming. ");
        
        if (finalCostPerParticipant < 50) {
            recommendations.append("Excellent cost efficiency - comprehensive art supplies within reasonable budget. ");
        } else {
            recommendations.append("Higher supply costs - consider group purchasing or seeking donations to reduce participant fees. ");
        }
        
        if (venuesArray.size() >= 7) {
            recommendations.append("Good variety of accessible venues available - prioritize senior centers for familiar environment. ");
        } else {
            recommendations.append("Limited venue options - expand search or partner with existing senior programs. ");
        }
        
        recommendations.append("Focus on sensory-friendly activities and adaptive techniques for varying mobility levels. ");
        recommendations.append("Incorporate social interaction and storytelling through art for enhanced therapeutic benefits. ");
        recommendations.append("Ensure all materials are non-toxic and easy to grip for senior participants.");
        
        workshopSummary.addProperty("planning_recommendations", recommendations.toString());
        
        // Workshop program structure and therapeutic goals
        JsonObject programStructure = new JsonObject();
        programStructure.addProperty("workshop_duration", "3 hours with breaks");
        programStructure.addProperty("group_size", "20 participants maximum for personalized attention");
        programStructure.addProperty("accessibility_features", "Seated activities, large-grip tools, good lighting");
        
        JsonArray therapeuticGoals = new JsonArray();
        therapeuticGoals.add("Enhance cognitive function through creative expression");
        therapeuticGoals.add("Improve fine motor skills and hand-eye coordination");
        therapeuticGoals.add("Reduce anxiety and depression through artistic engagement");
        therapeuticGoals.add("Foster social connections and community building");
        therapeuticGoals.add("Boost self-esteem and sense of accomplishment");
        programStructure.add("therapeutic_goals", therapeuticGoals);
        
        JsonArray activityStructure = new JsonArray();
        activityStructure.add("Welcome and introductions (15 minutes)");
        activityStructure.add("Warm-up drawing exercises (30 minutes)");
        activityStructure.add("Main art project - guided painting (90 minutes)");
        activityStructure.add("Break and social time (30 minutes)");
        activityStructure.add("Art sharing and reflection (30 minutes)");
        activityStructure.add("Cleanup and closing circle (15 minutes)");
        programStructure.add("activity_schedule", activityStructure);
        
        workshopSummary.add("program_structure", programStructure);
        
        // Therapeutic considerations and adaptations
        JsonObject therapeuticConsiderations = new JsonObject();
        therapeuticConsiderations.addProperty("cognitive_benefits", "Stimulates memory, problem-solving, and creative thinking");
        therapeuticConsiderations.addProperty("physical_benefits", "Improves dexterity, hand strength, and coordination");
        therapeuticConsiderations.addProperty("emotional_benefits", "Provides outlet for expression and emotional processing");
        therapeuticConsiderations.addProperty("social_benefits", "Encourages interaction and reduces isolation");
        
        JsonArray adaptations = new JsonArray();
        adaptations.add("Provide chairs with back support and adjustable height tables");
        adaptations.add("Use larger brushes and ergonomic handles for arthritis-friendly grip");
        adaptations.add("Offer washable, non-toxic materials for safety");
        adaptations.add("Include magnifying glasses for detail work");
        adaptations.add("Provide aprons and protective clothing");
        adaptations.add("Have wet wipes and hand sanitizer readily available");
        therapeuticConsiderations.add("senior_specific_adaptations", adaptations);
        
        JsonArray staffingRequirements = new JsonArray();
        staffingRequirements.add("Certified art therapist or trained facilitator");
        staffingRequirements.add("Assistant for mobility support and material distribution");
        staffingRequirements.add("Healthcare professional on standby if needed");
        therapeuticConsiderations.add("staffing_requirements", staffingRequirements);
        
        workshopSummary.add("therapeutic_considerations", therapeuticConsiderations);
        
        // Evaluation and follow-up
        JsonObject evaluationPlan = new JsonObject();
        evaluationPlan.addProperty("immediate_feedback", "Post-workshop survey on enjoyment and perceived benefits");
        evaluationPlan.addProperty("follow_up_assessment", "One-week check-in on mood and motivation to continue art");
        evaluationPlan.addProperty("program_expansion", "Potential for weekly ongoing art therapy sessions");
        evaluationPlan.addProperty("community_partnerships", "Collaborate with local senior centers for regular programming");
        
        JsonArray successIndicators = new JsonArray();
        successIndicators.add("High participant engagement and enjoyment");
        successIndicators.add("Completion of art projects by majority of participants");
        successIndicators.add("Positive social interactions and peer support");
        successIndicators.add("Expressed interest in future art activities");
        successIndicators.add("Observable improvements in mood and confidence");
        evaluationPlan.add("success_indicators", successIndicators);
        
        workshopSummary.add("evaluation_plan", evaluationPlan);
        
        result.add("art_therapy_workshop_summary", workshopSummary);
        
        return result;
    }
    
    // Helper method to estimate art supply costs when Costco search fails
    private static double getEstimatedArtSupplyCost(String supply) {
        switch (supply.toLowerCase()) {
            case "paint brushes":
                return 25.0;
            case "acrylic paints":
                return 35.0;
            case "canvases":
                return 30.0;
            case "art supplies":
                return 40.0;
            default:
                return 30.0;
        }
    }
    
    // Helper method to estimate therapeutic supply costs
    private static double getEstimatedTherapeuticSupplyCost(String supply) {
        switch (supply.toLowerCase()) {
            case "colored pencils":
                return 20.0;
            case "sketchbooks":
                return 25.0;
            case "art therapy materials":
                return 45.0;
            case "senior-friendly art supplies":
                return 35.0;
            default:
                return 30.0;
        }
    }
    
    // Helper method to assess venue suitability for seniors
    private static String assessSeniorSuitability(String venueName, String venueType) {
        if (venueType.equals("senior_center")) {
            return "excellent";
        } else if (venueType.equals("wellness_center") || venueType.equals("community_center")) {
            return "good";
        } else if (venueName.contains("accessible") || venueName.contains("ground floor")) {
            return "good";
        } else {
            return "fair";
        }
    }
}
