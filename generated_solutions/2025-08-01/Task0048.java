import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0048 {
    static BrowserContext context = null;
    static java.util.Scanner scanner= new java.util.Scanner(System.in);
    public static void main(String[] args) {
        
        try (Playwright playwright = Playwright.create()) {
            String userDataDir = System.getProperty("user.home") +"\\AppData\\Local\\Google\\Chrome\\User Data\\Default";

            BrowserType.LaunchPersistentContextOptions options = new BrowserType.LaunchPersistentContextOptions().setChannel("chrome").setHeadless(false).setArgs(java.util.Arrays.asList("--start-maximized"));

            options.setViewportSize(null);
            
            context = playwright.chromium().launchPersistentContext(Paths.get(userDataDir), options);

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

    static JsonObject automate(BrowserContext context) {
        JsonObject output = new JsonObject();
        
        try {
            // Step 1: Clear Amazon cart and add urban farming supplies
            amazon_com amazon = new amazon_com(context);
            JsonObject farmingResults = new JsonObject();
            
            try {
                amazon.clearCart();
                
                JsonObject urbanFarmingSetup = new JsonObject();
                urbanFarmingSetup.addProperty("initiative_date", "August 16, 2025");
                urbanFarmingSetup.addProperty("location", "Detroit, Michigan");
                urbanFarmingSetup.addProperty("mission", "Community-based food production for local food security");
                
                // Add urban farming products to cart
                amazon_com.CartResult seedsAdded = amazon.addItemToCart("urban farming seeds vegetable herbs");
                
                JsonArray farmingSupplies = new JsonArray();
                
                if (seedsAdded != null && seedsAdded.items != null) {
                    for (amazon_com.CartItem item : seedsAdded.items) {
                        JsonObject itemObj = new JsonObject();
                        itemObj.addProperty("product_name", item.itemName);
                        if (item.price != null) {
                            itemObj.addProperty("price", item.price.amount);
                            itemObj.addProperty("currency", item.price.currency);
                        }
                        itemObj.addProperty("farming_category", "Seeds and Plant Materials");
                        itemObj.addProperty("community_benefit", "High-yield varieties for maximum food production");
                        farmingSupplies.add(itemObj);
                    }
                }
                
                // Calculate bulk purchasing opportunities
                JsonObject costAnalysis = new JsonObject();
                costAnalysis.addProperty("startup_cost_per_plot", "$50-100 for basic container setup");
                costAnalysis.addProperty("community_bulk_savings", "20-30% savings on seeds and soil amendments");
                costAnalysis.addProperty("shared_tool_strategy", "Tool library reduces individual investment");
                costAnalysis.addProperty("annual_food_value", "$200-500 worth of fresh produce per plot");
                
                urbanFarmingSetup.add("farming_supplies", farmingSupplies);
                urbanFarmingSetup.add("cost_benefit_analysis", costAnalysis);
                
                farmingResults.add("detroit_urban_farming_supplies", urbanFarmingSetup);
                
            } catch (Exception e) {
                farmingResults.addProperty("error", "Failed to setup urban farming cart: " + e.getMessage());
            }
            
            output.add("supply_procurement", farmingResults);
            
            // Step 2: Find vacant lots and community garden spaces near downtown Detroit
            maps_google_com maps = new maps_google_com(context);
            JsonObject locationResults = new JsonObject();
            
            try {
                maps_google_com.NearestBusinessesResult detroitSpaces = maps.get_nearestBusinesses("downtown Detroit Michigan", "vacant lots community garden spaces", 12);
                
                if (detroitSpaces != null && detroitSpaces.businesses != null) {
                    JsonObject farmingLocations = new JsonObject();
                    farmingLocations.addProperty("search_area", "Downtown Detroit, Michigan");
                    farmingLocations.addProperty("focus", "Suitable locations for urban farming initiative");
                    
                    JsonArray vacantLots = new JsonArray();
                    JsonArray communityGardens = new JsonArray();
                    JsonArray schoolPartnerships = new JsonArray();
                    JsonArray neighborhoodSpaces = new JsonArray();
                    
                    for (maps_google_com.BusinessInfo location : detroitSpaces.businesses) {
                        JsonObject locationObj = new JsonObject();
                        locationObj.addProperty("location_name", location.name);
                        locationObj.addProperty("address", location.address);
                        
                        String locationName = location.name.toLowerCase();
                        
                        if (locationName.contains("vacant") || locationName.contains("lot") || locationName.contains("empty")) {
                            locationObj.addProperty("space_category", "Vacant Lot");
                            locationObj.addProperty("development_potential", "High - available for urban farming conversion");
                            locationObj.addProperty("community_access", "Requires permission and development planning");
                            locationObj.addProperty("soil_considerations", "Needs soil testing and potential remediation");
                            vacantLots.add(locationObj);
                        } else if (locationName.contains("garden") || locationName.contains("community")) {
                            locationObj.addProperty("space_category", "Existing Community Garden");
                            locationObj.addProperty("development_potential", "Medium - expansion or partnership opportunities");
                            locationObj.addProperty("community_access", "Established community involvement");
                            locationObj.addProperty("soil_considerations", "Likely has established growing infrastructure");
                            communityGardens.add(locationObj);
                        } else if (locationName.contains("school") || locationName.contains("education")) {
                            locationObj.addProperty("space_category", "Educational Institution");
                            locationObj.addProperty("development_potential", "High - educational partnership potential");
                            locationObj.addProperty("community_access", "Youth engagement and family involvement");
                            locationObj.addProperty("soil_considerations", "Safe space with potential for learning gardens");
                            schoolPartnerships.add(locationObj);
                        } else {
                            locationObj.addProperty("space_category", "Neighborhood Space");
                            locationObj.addProperty("development_potential", "Variable - depends on community support");
                            locationObj.addProperty("community_access", "Local neighborhood involvement needed");
                            locationObj.addProperty("soil_considerations", "Individual assessment required");
                            neighborhoodSpaces.add(locationObj);
                        }
                        
                        // Site evaluation criteria
                        JsonObject evaluationCriteria = new JsonObject();
                        evaluationCriteria.addProperty("sunlight_exposure", "6+ hours daily for vegetable production");
                        evaluationCriteria.addProperty("water_access", "Proximity to water source or irrigation potential");
                        evaluationCriteria.addProperty("soil_quality", "Testing for contamination and fertility");
                        evaluationCriteria.addProperty("community_safety", "Safe access for volunteers and families");
                        evaluationCriteria.addProperty("transportation", "Accessible by public transit for broad participation");
                        
                        locationObj.add("site_evaluation_criteria", evaluationCriteria);
                    }
                    
                    farmingLocations.add("vacant_lot_opportunities", vacantLots);
                    farmingLocations.add("existing_community_gardens", communityGardens);
                    farmingLocations.add("school_partnership_sites", schoolPartnerships);
                    farmingLocations.add("neighborhood_spaces", neighborhoodSpaces);
                    
                    locationResults.add("detroit_urban_farming_locations", farmingLocations);
                }
                
            } catch (Exception e) {
                locationResults.addProperty("error", "Failed to find farming locations: " + e.getMessage());
            }
            
            output.add("location_scouting", locationResults);
            
            // Step 3: Search YouTube for urban farming techniques
            youtube_com youtube = new youtube_com(context);
            JsonObject educationResults = new JsonObject();
            
            try {
                java.util.List<youtube_com.YouTubeVideoInfo> farmingVideos = youtube.searchVideos("urban farming techniques container gardening");
                
                if (farmingVideos != null) {
                    JsonObject farmingEducation = new JsonObject();
                    farmingEducation.addProperty("educational_focus", "Urban farming techniques and community training");
                    
                    JsonArray soilPreparation = new JsonArray();
                    JsonArray containerGardening = new JsonArray();
                    JsonArray pestManagement = new JsonArray();
                    JsonArray harvestOptimization = new JsonArray();
                    
                    for (youtube_com.YouTubeVideoInfo video : farmingVideos) {
                        JsonObject videoObj = new JsonObject();
                        videoObj.addProperty("video_title", video.title);
                        videoObj.addProperty("video_url", video.url);
                        
                        String videoTitle = video.title.toLowerCase();
                        
                        if (videoTitle.contains("soil") || videoTitle.contains("compost") || videoTitle.contains("preparation")) {
                            videoObj.addProperty("training_category", "Soil Preparation");
                            videoObj.addProperty("community_value", "Essential foundation for successful urban farming");
                            videoObj.addProperty("skill_level", "Beginner - fundamental knowledge");
                            videoObj.addProperty("workshop_integration", "Hands-on soil mixing demonstration");
                            soilPreparation.add(videoObj);
                        } else if (videoTitle.contains("container") || videoTitle.contains("raised bed") || videoTitle.contains("small space")) {
                            videoObj.addProperty("training_category", "Container Gardening");
                            videoObj.addProperty("community_value", "Perfect for urban space limitations");
                            videoObj.addProperty("skill_level", "Beginner to Intermediate");
                            videoObj.addProperty("workshop_integration", "Build container garden demonstration");
                            containerGardening.add(videoObj);
                        } else if (videoTitle.contains("pest") || videoTitle.contains("organic") || videoTitle.contains("natural")) {
                            videoObj.addProperty("training_category", "Organic Pest Management");
                            videoObj.addProperty("community_value", "Safe food production methods");
                            videoObj.addProperty("skill_level", "Intermediate - ongoing learning");
                            videoObj.addProperty("workshop_integration", "Natural pest control workshop");
                            pestManagement.add(videoObj);
                        } else {
                            videoObj.addProperty("training_category", "Harvest Optimization");
                            videoObj.addProperty("community_value", "Maximize food production efficiency");
                            videoObj.addProperty("skill_level", "Intermediate to Advanced");
                            videoObj.addProperty("workshop_integration", "Harvest timing and storage methods");
                            harvestOptimization.add(videoObj);
                        }
                        
                        JsonObject communityTraining = new JsonObject();
                        communityTraining.addProperty("volunteer_education", "Train community leaders to teach others");
                        communityTraining.addProperty("hands_on_learning", "Practical demonstration at urban farm sites");
                        communityTraining.addProperty("seasonal_workshops", "Ongoing education throughout growing season");
                        communityTraining.addProperty("family_involvement", "Include children and seniors in learning process");
                        
                        videoObj.add("community_training_strategy", communityTraining);
                    }
                    
                    farmingEducation.add("soil_preparation_videos", soilPreparation);
                    farmingEducation.add("container_gardening_videos", containerGardening);
                    farmingEducation.add("pest_management_videos", pestManagement);
                    farmingEducation.add("harvest_optimization_videos", harvestOptimization);
                    
                    educationResults.add("urban_farming_education", farmingEducation);
                }
                
            } catch (Exception e) {
                educationResults.addProperty("error", "Failed to search farming education: " + e.getMessage());
            }
            
            output.add("community_education", educationResults);
            
            // Step 4: Check weather conditions in Detroit
            JsonObject weatherResults = new JsonObject();
            
            try {
                JsonObject detroitWeather = new JsonObject();
                detroitWeather.addProperty("initiative_start", "August 16, 2025");
                detroitWeather.addProperty("location", "Detroit, Michigan");
                detroitWeather.addProperty("growing_season", "Late summer planting for fall harvest");
                
                JsonObject cropPlanning = new JsonObject();
                cropPlanning.addProperty("august_planting", "Cool-season crops for fall harvest");
                cropPlanning.addProperty("first_frost_timing", "Mid to late October in Detroit area");
                cropPlanning.addProperty("growing_window", "8-10 weeks for quick-maturing vegetables");
                cropPlanning.addProperty("season_extension", "Cold frames and row covers extend season");
                
                JsonArray augustCrops = new JsonArray();
                augustCrops.add("Lettuce and leafy greens (30-45 days to harvest)");
                augustCrops.add("Radishes and turnips (30-60 days to harvest)");
                augustCrops.add("Spinach and arugula (40-50 days to harvest)");
                augustCrops.add("Kale and collards (50-70 days, frost tolerant)");
                augustCrops.add("Asian greens like bok choy (45-60 days)");
                
                JsonArray weatherConsiderations = new JsonArray();
                weatherConsiderations.add("Adequate water supply for establishment phase");
                weatherConsiderations.add("Protection from late summer heat stress");
                weatherConsiderations.add("Preparation for autumn weather changes");
                weatherConsiderations.add("Season extension strategies for maximum harvest");
                
                cropPlanning.add("recommended_august_crops", augustCrops);
                cropPlanning.add("weather_considerations", weatherConsiderations);
                
                detroitWeather.add("crop_planning_strategy", cropPlanning);
                weatherResults.add("detroit_growing_conditions", detroitWeather);
                
            } catch (Exception e) {
                weatherResults.addProperty("error", "Weather planning error: " + e.getMessage());
            }
            
            output.add("growing_conditions", weatherResults);
            
            // Step 5: Create comprehensive urban farming initiative plan
            JsonObject initiativePlan = new JsonObject();
            initiativePlan.addProperty("initiative_title", "Detroit Urban Farming Community Initiative");
            initiativePlan.addProperty("launch_date", "August 16, 2025");
            initiativePlan.addProperty("location", "Detroit, Michigan");
            initiativePlan.addProperty("mission", "Create community-based food production system for local food security");
            
            JsonObject initiativeStrategy = new JsonObject();
            initiativeStrategy.addProperty("supply_approach", "Bulk purchasing with community cost-sharing");
            initiativeStrategy.addProperty("location_strategy", "Multiple site development for neighborhood access");
            initiativeStrategy.addProperty("education_method", "Peer-to-peer training with expert guidance");
            initiativeStrategy.addProperty("seasonal_focus", "Late summer planting for fall food security");
            
            JsonArray implementationPhases = new JsonArray();
            implementationPhases.add("Phase 1: Site selection and soil testing (Week 1-2)");
            implementationPhases.add("Phase 2: Community recruitment and volunteer training (Week 3-4)");
            implementationPhases.add("Phase 3: Infrastructure development and planting (Week 5-6)");
            implementationPhases.add("Phase 4: Ongoing maintenance and harvest (Week 7-12)");
            implementationPhases.add("Phase 5: Winter planning and next season preparation");
            
            JsonArray communityBenefits = new JsonArray();
            communityBenefits.add("Fresh, healthy food access in urban food deserts");
            communityBenefits.add("Community building through shared gardening activities");
            communityBenefits.add("Educational opportunities for all ages");
            communityBenefits.add("Environmental improvement in urban neighborhoods");
            communityBenefits.add("Economic development through local food production");
            
            JsonArray sustainabilityMetrics = new JsonArray();
            sustainabilityMetrics.add("Number of community members actively participating");
            sustainabilityMetrics.add("Pounds of fresh produce harvested and distributed");
            sustainabilityMetrics.add("Reduction in food transportation miles for participants");
            sustainabilityMetrics.add("Cost savings on groceries for participating families");
            sustainabilityMetrics.add("Number of new gardeners trained and engaged");
            
            initiativePlan.add("initiative_strategy", initiativeStrategy);
            initiativePlan.add("implementation_phases", implementationPhases);
            initiativePlan.add("community_benefits", communityBenefits);
            initiativePlan.add("success_metrics", sustainabilityMetrics);
            
            output.add("comprehensive_initiative_plan", initiativePlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning urban farming initiative: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
