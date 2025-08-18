import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0043 {
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
            // Step 1: Get NASA's Astronomy Picture of the Day for August 22, 2025
            Nasa nasa = new Nasa();
            JsonObject nasaResults = new JsonObject();
            
            try {
                Nasa.ApodResult apod = nasa.getApod("2025-08-22", true);
                
                if (apod != null) {
                    JsonObject apodInfo = new JsonObject();
                    apodInfo.addProperty("title", apod.title);
                    apodInfo.addProperty("url", apod.url);
                    apodInfo.addProperty("explanation", apod.explanation);
                    apodInfo.addProperty("date", apod.date.toString());
                    
                    // Analyze content for educational talking points
                    JsonArray talkingPoints = new JsonArray();
                    JsonArray discussionQuestions = new JsonArray();
                    
                    if (apod.title != null && apod.explanation != null) {
                        String title = apod.title.toLowerCase();
                        String explanation = apod.explanation.toLowerCase();
                        
                        // Generate educational content based on APOD content
                        if (title.contains("galaxy") || explanation.contains("galaxy")) {
                            talkingPoints.add("Explore the structure and formation of galaxies");
                            talkingPoints.add("Discuss the Milky Way's position relative to other galaxies");
                            discussionQuestions.add("How do galaxies form and evolve over billions of years?");
                            discussionQuestions.add("What can we observe about distant galaxies from Earth?");
                        }
                        
                        if (title.contains("nebula") || explanation.contains("nebula")) {
                            talkingPoints.add("Understand stellar nurseries and star formation");
                            talkingPoints.add("Learn about different types of nebulae and their characteristics");
                            discussionQuestions.add("How do nebulae contribute to the birth of new stars?");
                            discussionQuestions.add("What equipment do we need to observe nebulae tonight?");
                        }
                        
                        if (title.contains("planet") || explanation.contains("planet")) {
                            talkingPoints.add("Compare planetary characteristics within our solar system");
                            talkingPoints.add("Discuss exoplanet discovery methods and recent findings");
                            discussionQuestions.add("What makes a planet habitable for life as we know it?");
                            discussionQuestions.add("How do we detect planets orbiting other stars?");
                        }
                        
                        if (title.contains("comet") || explanation.contains("comet") || 
                            title.contains("asteroid") || explanation.contains("asteroid")) {
                            talkingPoints.add("Explore the origin and composition of small solar system bodies");
                            talkingPoints.add("Understand the difference between comets, asteroids, and meteoroids");
                            discussionQuestions.add("Why do comets develop tails when approaching the Sun?");
                            discussionQuestions.add("How do these objects help us understand solar system formation?");
                        }
                        
                        // General astronomy talking points
                        talkingPoints.add("Connect today's image to ongoing space exploration missions");
                        talkingPoints.add("Discuss how amateur astronomers can contribute to scientific discovery");
                        talkingPoints.add("Explore the technology behind modern astronomical imaging");
                        
                        discussionQuestions.add("What questions does this image raise about our universe?");
                        discussionQuestions.add("How might future technology change our understanding of this phenomenon?");
                        discussionQuestions.add("What similar objects or events can we observe tonight?");
                    }
                    
                    apodInfo.add("educational_talking_points", talkingPoints);
                    apodInfo.add("group_discussion_questions", discussionQuestions);
                    apodInfo.addProperty("centerpiece_role", "Featured as main discussion starter for astronomy gathering");
                    
                    nasaResults.add("astronomy_picture_of_day", apodInfo);
                }
                
                nasaResults.addProperty("gathering_date", "August 22, 2025");
                nasaResults.addProperty("educational_purpose", "Centerpiece content for astronomical discussion and learning");
                
            } catch (Exception e) {
                nasaResults.addProperty("error", "Failed to get NASA APOD: " + e.getMessage());
            }
            
            output.add("nasa_educational_content", nasaResults);
            
            // Step 2: Search for telescopes and astronomy equipment at Costco
            costco_com costco = new costco_com(context);
            JsonObject costcoResults = new JsonObject();
            
            try {
                costco_com.ProductListResult telescopeEquipment = costco.searchProducts("telescopes astronomy equipment");
                
                JsonArray telescopesArray = new JsonArray();
                JsonArray accessoriesArray = new JsonArray();
                JsonArray groupPurchaseOptions = new JsonArray();
                double totalEquipmentCost = 0.0;
                int beginnerFriendlyCount = 0;
                int advancedEquipmentCount = 0;
                
                if (telescopeEquipment != null && telescopeEquipment.products != null) {
                    for (costco_com.ProductInfo product : telescopeEquipment.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("name", product.productName);
                        
                        if (product.productPrice != null) {
                            productObj.addProperty("price", product.productPrice.amount);
                            productObj.addProperty("currency", product.productPrice.currency);
                            totalEquipmentCost += product.productPrice.amount;
                            
                            // Categorize equipment by price and suitability
                            double price = product.productPrice.amount;
                            String productName = product.productName.toLowerCase();
                            
                            if (productName.contains("telescope")) {
                                if (price <= 200) {
                                    productObj.addProperty("category", "Beginner Telescope");
                                    productObj.addProperty("group_suitability", "Excellent for newcomers - affordable entry point");
                                    productObj.addProperty("group_purchase_benefit", "Multiple units for hands-on learning");
                                    beginnerFriendlyCount++;
                                } else if (price <= 800) {
                                    productObj.addProperty("category", "Intermediate Telescope");
                                    productObj.addProperty("group_suitability", "Good for serious hobbyists");
                                    productObj.addProperty("group_purchase_benefit", "Shared cost for quality equipment");
                                } else {
                                    productObj.addProperty("category", "Advanced Telescope");
                                    productObj.addProperty("group_suitability", "Premium option for dedicated enthusiasts");
                                    productObj.addProperty("group_purchase_benefit", "Professional-grade shared resource");
                                    advancedEquipmentCount++;
                                }
                                telescopesArray.add(productObj);
                            } else {
                                productObj.addProperty("category", "Astronomy Accessory");
                                if (productName.contains("eyepiece") || productName.contains("filter") || 
                                    productName.contains("mount") || productName.contains("finder")) {
                                    productObj.addProperty("accessory_type", "Essential telescope enhancement");
                                } else {
                                    productObj.addProperty("accessory_type", "General astronomy equipment");
                                }
                                accessoriesArray.add(productObj);
                            }
                            
                            // Group purchase calculations
                            if (price >= 100) {
                                JsonObject groupOption = new JsonObject();
                                groupOption.addProperty("item", product.productName);
                                groupOption.addProperty("individual_cost", price);
                                groupOption.addProperty("cost_per_member_25_people", price / 25);
                                groupOption.addProperty("cost_per_member_10_people", price / 10);
                                groupOption.addProperty("cost_per_member_5_people", price / 5);
                                groupOption.addProperty("recommendation", price <= 500 ? "Excellent group purchase opportunity" : "Consider for dedicated sub-group");
                                groupPurchaseOptions.add(groupOption);
                            }
                        }
                        
                        // Telescope type comparison for education
                        String productName = product.productName.toLowerCase();
                        if (productName.contains("refractor")) {
                            productObj.addProperty("telescope_type", "Refractor");
                            productObj.addProperty("best_for", "Planetary observation and lunar details");
                            productObj.addProperty("learning_advantage", "Simple design, easy maintenance");
                        } else if (productName.contains("reflector")) {
                            productObj.addProperty("telescope_type", "Reflector");
                            productObj.addProperty("best_for", "Deep sky objects and nebulae");
                            productObj.addProperty("learning_advantage", "Larger aperture for light gathering");
                        } else if (productName.contains("compound") || productName.contains("schmidt")) {
                            productObj.addProperty("telescope_type", "Compound/Schmidt-Cassegrain");
                            productObj.addProperty("best_for", "Versatile all-around observations");
                            productObj.addProperty("learning_advantage", "Compact design with good performance");
                        }
                        
                        if (product.error != null) {
                            productObj.addProperty("error", product.error);
                        }
                    }
                }
                
                costcoResults.add("telescopes", telescopesArray);
                costcoResults.add("accessories", accessoriesArray);
                costcoResults.add("group_purchase_options", groupPurchaseOptions);
                costcoResults.addProperty("total_equipment_found", telescopeEquipment != null && telescopeEquipment.products != null ? telescopeEquipment.products.size() : 0);
                costcoResults.addProperty("beginner_friendly_options", beginnerFriendlyCount);
                costcoResults.addProperty("advanced_equipment_count", advancedEquipmentCount);
                costcoResults.addProperty("estimated_total_value", totalEquipmentCost);
                
                // Group purchase strategy
                JsonObject purchaseStrategy = new JsonObject();
                purchaseStrategy.addProperty("bulk_advantage", "Costco membership allows group purchases with significant savings");
                purchaseStrategy.addProperty("sharing_model", "Pool resources for premium equipment accessible to all members");
                purchaseStrategy.addProperty("starter_package_cost", "Estimate $50-150 per person for quality beginner setup");
                purchaseStrategy.addProperty("advanced_package_cost", "Estimate $200-500 per person for serious equipment");
                
                JsonArray purchaseRecommendations = new JsonArray();
                purchaseRecommendations.add("Start with 2-3 beginner telescopes for group learning sessions");
                purchaseRecommendations.add("Pool funds for 1 premium telescope for advanced observations");
                purchaseRecommendations.add("Purchase variety of eyepieces for different magnifications");
                purchaseRecommendations.add("Consider red LED flashlights for night vision preservation");
                purchaseRecommendations.add("Invest in star charts and astronomical reference materials");
                
                purchaseStrategy.add("group_buying_recommendations", purchaseRecommendations);
                costcoResults.add("purchase_strategy", purchaseStrategy);
                
            } catch (Exception e) {
                costcoResults.addProperty("error", "Failed to search telescope equipment: " + e.getMessage());
            }
            
            output.add("equipment_research", costcoResults);
            
            // Step 3: Search YouTube for astronomy beginner guides
            youtube_com youtube = new youtube_com(context);
            JsonObject youtubeResults = new JsonObject();
            
            try {
                List<youtube_com.YouTubeVideoInfo> astronomyVideos = youtube.searchVideos("astronomy beginner telescope guide");
                
                JsonArray videosArray = new JsonArray();
                JsonArray beginnerContent = new JsonArray();
                JsonArray advancedContent = new JsonArray();
                long totalEducationalTime = 0;
                
                if (astronomyVideos != null) {
                    for (youtube_com.YouTubeVideoInfo video : astronomyVideos) {
                        JsonObject videoObj = new JsonObject();
                        videoObj.addProperty("title", video.title);
                        videoObj.addProperty("url", video.url);
                        
                        // Format duration
                        long seconds = video.length.getSeconds();
                        long hours = seconds / 3600;
                        long minutes = (seconds % 3600) / 60;
                        long secs = seconds % 60;
                        String durationStr = hours > 0 ? 
                            String.format("%d:%02d:%02d", hours, minutes, secs) : 
                            String.format("%d:%02d", minutes, secs);
                        videoObj.addProperty("duration", durationStr);
                        videoObj.addProperty("duration_seconds", seconds);
                        
                        totalEducationalTime += seconds;
                        
                        // Categorize content by topic and difficulty
                        String title = video.title.toLowerCase();
                        
                        if (title.contains("beginner") || title.contains("start") || title.contains("basic")) {
                            videoObj.addProperty("difficulty_level", "Beginner");
                            beginnerContent.add(videoObj);
                        } else if (title.contains("advanced") || title.contains("expert") || title.contains("professional")) {
                            videoObj.addProperty("difficulty_level", "Advanced");
                            advancedContent.add(videoObj);
                        } else {
                            videoObj.addProperty("difficulty_level", "Intermediate");
                        }
                        
                        // Topic categorization
                        if (title.contains("telescope") && (title.contains("setup") || title.contains("operation"))) {
                            videoObj.addProperty("topic_category", "Telescope Operation");
                            videoObj.addProperty("learning_objective", "Master telescope setup and basic operation");
                        } else if (title.contains("constellation") || title.contains("star") || title.contains("identify")) {
                            videoObj.addProperty("topic_category", "Constellation Identification");
                            videoObj.addProperty("learning_objective", "Learn to navigate the night sky");
                        } else if (title.contains("astrophotography") || title.contains("photography") || title.contains("imaging")) {
                            videoObj.addProperty("topic_category", "Astrophotography Basics");
                            videoObj.addProperty("learning_objective", "Introduction to astronomical imaging");
                        } else if (title.contains("planet") || title.contains("moon") || title.contains("solar system")) {
                            videoObj.addProperty("topic_category", "Solar System Observation");
                            videoObj.addProperty("learning_objective", "Observe and understand planetary features");
                        } else {
                            videoObj.addProperty("topic_category", "General Astronomy");
                            videoObj.addProperty("learning_objective", "Foundational astronomy knowledge");
                        }
                        
                        // Gathering relevance assessment
                        if (seconds <= 900) { // 15 minutes or less
                            videoObj.addProperty("gathering_suitability", "Perfect for group viewing during event");
                        } else if (seconds <= 1800) { // 30 minutes or less
                            videoObj.addProperty("gathering_suitability", "Good for dedicated learning session");
                        } else {
                            videoObj.addProperty("gathering_suitability", "Best as pre-event homework or follow-up resource");
                        }
                        
                        videosArray.add(videoObj);
                    }
                }
                
                youtubeResults.add("all_educational_videos", videosArray);
                youtubeResults.add("beginner_friendly_content", beginnerContent);
                youtubeResults.add("advanced_content", advancedContent);
                youtubeResults.addProperty("total_videos", videosArray.size());
                youtubeResults.addProperty("total_educational_time_minutes", totalEducationalTime / 60);
                
                // Create learning resource structure
                JsonObject learningStructure = new JsonObject();
                learningStructure.addProperty("pre_event_preparation", "Share beginner videos 1 week before gathering");
                learningStructure.addProperty("during_event_content", "Quick 10-15 minute educational segments");
                learningStructure.addProperty("post_event_resources", "Advanced content for continued learning");
                learningStructure.addProperty("hands_on_correlation", "Match video topics with telescope demonstrations");
                
                JsonArray curriculumModules = new JsonArray();
                curriculumModules.add("Module 1: Telescope basics and setup (15 minutes)");
                curriculumModules.add("Module 2: Finding and identifying constellations (20 minutes)");
                curriculumModules.add("Module 3: Observing planets and moon features (25 minutes)");
                curriculumModules.add("Module 4: Introduction to deep sky objects (20 minutes)");
                curriculumModules.add("Module 5: Astrophotography fundamentals (15 minutes)");
                
                learningStructure.add("suggested_curriculum_modules", curriculumModules);
                youtubeResults.add("learning_resource_structure", learningStructure);
                
            } catch (Exception e) {
                youtubeResults.addProperty("error", "Failed to search astronomy videos: " + e.getMessage());
            }
            
            output.add("educational_video_resources", youtubeResults);
            
            // Step 4: Find dark sky areas and observatories near Denver
            maps_google_com maps = new maps_google_com(context);
            JsonObject locationsResults = new JsonObject();
            
            try {
                maps_google_com.NearestBusinessesResult darkSkyAreas = maps.get_nearestBusinesses("Denver Colorado", "observatories dark sky areas", 8);
                
                JsonArray observationSites = new JsonArray();
                JsonArray accessibilityInfo = new JsonArray();
                
                if (darkSkyAreas != null && darkSkyAreas.businesses != null) {
                    int siteIndex = 1;
                    for (maps_google_com.BusinessInfo location : darkSkyAreas.businesses) {
                        JsonObject siteObj = new JsonObject();
                        siteObj.addProperty("site_name", location.name);
                        siteObj.addProperty("address", location.address);
                        siteObj.addProperty("site_number", siteIndex++);
                        
                        // Categorize sites based on name and type
                        String locationName = location.name.toLowerCase();
                        if (locationName.contains("observatory") || locationName.contains("planetarium")) {
                            siteObj.addProperty("site_type", "Professional Observatory");
                            siteObj.addProperty("advantages", "Expert facilities, guided observations, educational programs");
                            siteObj.addProperty("group_suitability", "Excellent for structured learning experience");
                            siteObj.addProperty("estimated_cost", "May require admission fees or group booking");
                        } else if (locationName.contains("park") && (locationName.contains("dark") || locationName.contains("sky"))) {
                            siteObj.addProperty("site_type", "Dark Sky Park");
                            siteObj.addProperty("advantages", "Minimal light pollution, natural setting, free access");
                            siteObj.addProperty("group_suitability", "Perfect for large group stargazing");
                            siteObj.addProperty("estimated_cost", "Free or minimal park entry fee");
                        } else if (locationName.contains("mountain") || locationName.contains("peak") || locationName.contains("elevation")) {
                            siteObj.addProperty("site_type", "High Elevation Site");
                            siteObj.addProperty("advantages", "Clear atmosphere, excellent visibility, dramatic setting");
                            siteObj.addProperty("group_suitability", "Good for experienced groups with proper preparation");
                            siteObj.addProperty("estimated_cost", "Free access, but require weather preparation");
                        } else {
                            siteObj.addProperty("site_type", "General Dark Sky Area");
                            siteObj.addProperty("advantages", "Reduced light pollution for better observations");
                            siteObj.addProperty("group_suitability", "Suitable with proper site evaluation");
                            siteObj.addProperty("estimated_cost", "Typically free access");
                        }
                        
                        // Estimate drive times and logistics for 25-person group
                        JsonObject logistics = new JsonObject();
                        logistics.addProperty("estimated_drive_time", "45-90 minutes from Denver (varies by traffic and location)");
                        logistics.addProperty("group_transportation", "Recommend carpooling - 5-6 vehicles for 25 people");
                        logistics.addProperty("arrival_timing", "Arrive 1 hour before sunset for setup");
                        logistics.addProperty("departure_planning", "Plan for 2-3 hours of observation time");
                        
                        // Accessibility considerations
                        if (locationName.contains("park") || locationName.contains("center")) {
                            logistics.addProperty("accessibility", "Good - likely has parking and basic facilities");
                            logistics.addProperty("terrain", "Generally accessible for most group members");
                        } else if (locationName.contains("mountain") || locationName.contains("trail")) {
                            logistics.addProperty("accessibility", "Moderate - may require hiking or 4WD access");
                            logistics.addProperty("terrain", "Check conditions, bring appropriate footwear");
                        } else {
                            logistics.addProperty("accessibility", "Unknown - recommend advance scouting");
                            logistics.addProperty("terrain", "Evaluate site before bringing large group");
                        }
                        
                        siteObj.add("group_logistics", logistics);
                        observationSites.add(siteObj);
                        
                        // Create accessibility summary
                        JsonObject accessibilityItem = new JsonObject();
                        accessibilityItem.addProperty("location", location.name);
                        accessibilityItem.addProperty("group_size_suitability", "25 astronomy enthusiasts");
                        accessibilityItem.addProperty("equipment_transport", "Space needed for telescopes and supplies");
                        accessibilityItem.addProperty("safety_considerations", "Night driving, weather awareness, group coordination");
                        accessibilityInfo.add(accessibilityItem);
                    }
                }
                
                locationsResults.add("stargazing_locations", observationSites);
                locationsResults.add("accessibility_analysis", accessibilityInfo);
                locationsResults.addProperty("total_sites_found", observationSites.size());
                locationsResults.addProperty("search_area", "Denver, Colorado region");
                
                // Create driving and logistics recommendations
                JsonArray logisticsRecommendations = new JsonArray();
                logisticsRecommendations.add("Scout locations in advance during daylight hours");
                logisticsRecommendations.add("Create detailed driving directions for all participants");
                logisticsRecommendations.add("Establish group leaders for each carpool vehicle");
                logisticsRecommendations.add("Plan for variable weather conditions in Colorado mountains");
                logisticsRecommendations.add("Bring red flashlights to preserve night vision");
                logisticsRecommendations.add("Coordinate arrival times to avoid light pollution from vehicle headlights");
                logisticsRecommendations.add("Have backup indoor location for weather emergencies");
                
                locationsResults.add("logistics_recommendations", logisticsRecommendations);
                
                // Site selection criteria
                JsonObject selectionCriteria = new JsonObject();
                selectionCriteria.addProperty("light_pollution", "Minimize artificial light sources for best observations");
                selectionCriteria.addProperty("accessibility", "Balance dark skies with group transportation needs");
                selectionCriteria.addProperty("weather_protection", "Consider shelter options for unpredictable conditions");
                selectionCriteria.addProperty("group_safety", "Well-known locations with reliable cell service preferred");
                selectionCriteria.addProperty("equipment_setup", "Flat areas suitable for telescope mounting");
                
                locationsResults.add("site_selection_criteria", selectionCriteria);
                
            } catch (Exception e) {
                locationsResults.addProperty("error", "Failed to find observation locations: " + e.getMessage());
            }
            
            output.add("stargazing_locations_research", locationsResults);
            
            // Step 5: Create comprehensive astronomy gathering plan
            JsonObject gatheringPlan = new JsonObject();
            gatheringPlan.addProperty("event_title", "Denver Astronomy Enthusiast Gathering");
            gatheringPlan.addProperty("date", "August 22, 2025");
            gatheringPlan.addProperty("location", "Denver, Colorado Area");
            gatheringPlan.addProperty("group_size", "25 astronomy enthusiasts");
            gatheringPlan.addProperty("focus", "Scientific learning combined with practical observation");
            
            // Event structure and timeline
            JsonObject eventStructure = new JsonObject();
            eventStructure.addProperty("pre_event_phase", "1 week preparation with educational video sharing");
            eventStructure.addProperty("gathering_phase", "6-hour event combining education and observation");
            eventStructure.addProperty("observation_phase", "3-4 hours of guided stargazing experience");
            eventStructure.addProperty("follow_up_phase", "Resource sharing and future planning");
            
            JsonArray eventTimeline = new JsonArray();
            eventTimeline.add("6:00 PM: Welcome and NASA APOD presentation");
            eventTimeline.add("6:30 PM: Telescope equipment demonstration and education");
            eventTimeline.add("7:00 PM: Quick educational video segments");
            eventTimeline.add("7:30 PM: Drive to dark sky location (carpool coordination)");
            eventTimeline.add("8:30 PM: Telescope setup and safety briefing");
            eventTimeline.add("9:00 PM: Begin stargazing observations");
            eventTimeline.add("11:30 PM: Group discussion and experience sharing");
            eventTimeline.add("12:00 AM: Pack up and safe return coordination");
            
            eventStructure.add("suggested_timeline", eventTimeline);
            gatheringPlan.add("event_structure", eventStructure);
            
            // Educational objectives and outcomes
            JsonObject educationalGoals = new JsonObject();
            educationalGoals.addProperty("astronomical_knowledge", "Understanding of current space discoveries and phenomena");
            educationalGoals.addProperty("practical_skills", "Telescope operation and sky navigation abilities");
            educationalGoals.addProperty("observational_experience", "Hands-on stargazing with quality equipment");
            educationalGoals.addProperty("community_building", "Connections among local astronomy enthusiasts");
            
            JsonArray learningOutcomes = new JsonArray();
            learningOutcomes.add("Participants can independently set up and operate telescopes");
            learningOutcomes.add("Knowledge of constellation identification and celestial navigation");
            learningOutcomes.add("Understanding of current astronomical discoveries and research");
            learningOutcomes.add("Awareness of local dark sky resources and observation opportunities");
            learningOutcomes.add("Network of fellow astronomy enthusiasts for future collaborations");
            
            educationalGoals.add("expected_learning_outcomes", learningOutcomes);
            gatheringPlan.add("educational_objectives", educationalGoals);
            
            // Resource and budget planning
            JsonObject resourcePlanning = new JsonObject();
            resourcePlanning.addProperty("equipment_sharing", "Coordinate telescope access through Costco group purchases");
            resourcePlanning.addProperty("educational_materials", "NASA content and YouTube video resources");
            resourcePlanning.addProperty("location_access", "Free or low-cost dark sky areas near Denver");
            resourcePlanning.addProperty("transportation", "Participant carpooling with group coordination");
            
            JsonObject budgetEstimate = new JsonObject();
            budgetEstimate.addProperty("equipment_contribution", "$50-200 per person for group telescope purchases");
            budgetEstimate.addProperty("transportation_cost", "$15-30 per person for gas and parking");
            budgetEstimate.addProperty("location_fees", "$0-10 per person for park access if applicable");
            budgetEstimate.addProperty("educational_materials", "$0 (free NASA and YouTube resources)");
            budgetEstimate.addProperty("total_estimated_cost", "$65-240 per person depending on equipment participation");
            
            resourcePlanning.add("budget_breakdown", budgetEstimate);
            gatheringPlan.add("resource_planning", resourcePlanning);
            
            // Success metrics and follow-up
            JsonArray successMetrics = new JsonArray();
            successMetrics.add("Participant engagement and enthusiasm during observations");
            successMetrics.add("Successful telescope operation by newcomers");
            successMetrics.add("Quality of celestial objects observed and photographed");
            successMetrics.add("Formation of ongoing astronomy study groups");
            successMetrics.add("Commitment to future stargazing events and activities");
            
            JsonArray followUpActions = new JsonArray();
            followUpActions.add("Share photos and observations from the gathering");
            followUpActions.add("Organize monthly stargazing meetups at identified locations");
            followUpActions.add("Create equipment sharing library for group members");
            followUpActions.add("Plan advanced astrophotography workshop for interested participants");
            followUpActions.add("Coordinate group trips to major observatories and astronomy events");
            
            gatheringPlan.add("success_metrics", successMetrics);
            gatheringPlan.add("follow_up_opportunities", followUpActions);
            
            output.add("comprehensive_gathering_plan", gatheringPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning astronomy gathering: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
