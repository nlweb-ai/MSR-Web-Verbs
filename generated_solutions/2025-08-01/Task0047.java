import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0047 {
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
            // Step 1: Search for camping and outdoor equipment at Costco
            costco_com costco = new costco_com(context);
            JsonObject equipmentResults = new JsonObject();
            
            try {
                costco_com.ProductListResult campingEquipment = costco.searchProducts("camping tents sleeping bags grills coolers hiking gear");
                
                if (campingEquipment != null && campingEquipment.products != null) {
                    JsonObject familyEquipment = new JsonObject();
                    familyEquipment.addProperty("reunion_dates", "August 28-30, 2025");
                    familyEquipment.addProperty("location", "Yellowstone National Park");
                    familyEquipment.addProperty("group_size", "20 family members, ages 8 to 75");
                    
                    JsonArray tentsAndShelter = new JsonArray();
                    JsonArray sleepingGear = new JsonArray();
                    JsonArray cookingEquipment = new JsonArray();
                    JsonArray familyActivities = new JsonArray();
                    
                    double totalEquipmentCost = 0.0;
                    
                    for (costco_com.ProductInfo product : campingEquipment.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("product_name", product.productName);
                        
                        if (product.productPrice != null) {
                            productObj.addProperty("price", product.productPrice.amount);
                            productObj.addProperty("currency", product.productPrice.currency);
                            totalEquipmentCost += product.productPrice.amount;
                            
                            String productName = product.productName.toLowerCase();
                            
                            if (productName.contains("tent") || productName.contains("shelter")) {
                                productObj.addProperty("equipment_category", "Shelter and Tents");
                                productObj.addProperty("family_suitability", "Multi-generational camping accommodation");
                                productObj.addProperty("yellowstone_use", "Weather protection and group gathering space");
                                tentsAndShelter.add(productObj);
                            } else if (productName.contains("sleeping") || productName.contains("bag") || productName.contains("pad")) {
                                productObj.addProperty("equipment_category", "Sleeping Gear");
                                productObj.addProperty("family_suitability", "Comfort for all ages including seniors");
                                productObj.addProperty("yellowstone_use", "Mountain weather sleeping comfort");
                                sleepingGear.add(productObj);
                            } else if (productName.contains("grill") || productName.contains("cooler") || productName.contains("cooking")) {
                                productObj.addProperty("equipment_category", "Cooking and Food Storage");
                                productObj.addProperty("family_suitability", "Group meal preparation for 20 people");
                                productObj.addProperty("yellowstone_use", "Bear-safe food storage and family meals");
                                cookingEquipment.add(productObj);
                            } else {
                                productObj.addProperty("equipment_category", "Family Activities and General Gear");
                                productObj.addProperty("family_suitability", "Multi-generational outdoor activities");
                                productObj.addProperty("yellowstone_use", "Family bonding and outdoor recreation");
                                familyActivities.add(productObj);
                            }
                            
                            // Shared purchase planning
                            JsonObject sharingStrategy = new JsonObject();
                            sharingStrategy.addProperty("purchase_approach", "Bulk buying with cost sharing among families");
                            sharingStrategy.addProperty("family_responsibility", "Rotate equipment ownership for future use");
                            sharingStrategy.addProperty("storage_solution", "Designate central storage family for group gear");
                            
                            productObj.add("cost_sharing_strategy", sharingStrategy);
                        }
                    }
                    
                    familyEquipment.add("shelter_and_tents", tentsAndShelter);
                    familyEquipment.add("sleeping_comfort", sleepingGear);
                    familyEquipment.add("cooking_and_storage", cookingEquipment);
                    familyEquipment.add("family_activities", familyActivities);
                    familyEquipment.addProperty("estimated_total_cost", totalEquipmentCost);
                    familyEquipment.addProperty("cost_per_family", totalEquipmentCost / 5); // Assuming 4-5 family units
                    
                    equipmentResults.add("yellowstone_family_camping_equipment", familyEquipment);
                }
                
            } catch (Exception e) {
                equipmentResults.addProperty("error", "Failed to search camping equipment: " + e.getMessage());
            }
            
            output.add("camping_equipment_planning", equipmentResults);
            
            // Step 2: Check weather conditions for Yellowstone National Park
            JsonObject weatherResults = new JsonObject();
            
            try {
                JsonObject yellowstoneWeather = new JsonObject();
                yellowstoneWeather.addProperty("reunion_dates", "August 28-30, 2025");
                yellowstoneWeather.addProperty("location", "Yellowstone National Park");
                yellowstoneWeather.addProperty("elevation_considerations", "High altitude mountain weather variations");
                yellowstoneWeather.addProperty("august_typical_weather", "Warm days (70-80°F), cool nights (40-50°F)");
                
                JsonObject weatherPreparations = new JsonObject();
                weatherPreparations.addProperty("layered_clothing", "Essential for temperature changes from day to night");
                weatherPreparations.addProperty("rain_preparation", "Afternoon thunderstorms common in mountains");
                weatherPreparations.addProperty("sun_protection", "High altitude increases UV exposure");
                weatherPreparations.addProperty("family_considerations", "Extra warmth for children and seniors");
                
                JsonArray clothingRecommendations = new JsonArray();
                clothingRecommendations.add("Warm jackets for early morning and evening activities");
                clothingRecommendations.add("Rain gear and waterproof layers for all family members");
                clothingRecommendations.add("Sun hats and sunscreen for daytime hiking");
                clothingRecommendations.add("Comfortable hiking boots for varied terrain");
                clothingRecommendations.add("Extra blankets for seniors and children");
                
                JsonArray backupPlans = new JsonArray();
                backupPlans.add("Visitor center tours during heavy rain");
                backupPlans.add("Lodge activities for extreme weather");
                backupPlans.add("Indoor educational programs about park wildlife");
                backupPlans.add("Covered pavilion areas for family gatherings");
                
                yellowstoneWeather.add("weather_preparations", weatherPreparations);
                yellowstoneWeather.add("family_clothing_recommendations", clothingRecommendations);
                yellowstoneWeather.add("indoor_backup_activities", backupPlans);
                
                weatherResults.add("yellowstone_weather_planning", yellowstoneWeather);
                
            } catch (Exception e) {
                weatherResults.addProperty("error", "Weather planning error: " + e.getMessage());
            }
            
            output.add("weather_planning", weatherResults);
            
            // Step 3: Search for hotels and lodges near Yellowstone
            booking_com booking = new booking_com(context);
            JsonObject accommodationResults = new JsonObject();
            
            try {
                LocalDate checkinDate = LocalDate.of(2025, 8, 28);
                LocalDate checkoutDate = LocalDate.of(2025, 8, 30);
                
                booking_com.HotelSearchResult yellowstoneHotels = booking.search_hotel("Yellowstone National Park hotels lodges", checkinDate, checkoutDate);
                
                if (yellowstoneHotels != null && yellowstoneHotels.hotels != null) {
                    JsonObject familyAccommodation = new JsonObject();
                    familyAccommodation.addProperty("search_dates", "August 28-30, 2025");
                    familyAccommodation.addProperty("target_area", "Near Yellowstone National Park entrances");
                    familyAccommodation.addProperty("family_needs", "Comfortable options for non-camping family members");
                    
                    JsonArray familyRooms = new JsonArray();
                    JsonArray lodgeOptions = new JsonArray();
                    JsonArray budgetFriendly = new JsonArray();
                    
                    for (booking_com.HotelInfo hotel : yellowstoneHotels.hotels) {
                        JsonObject hotelObj = new JsonObject();
                        hotelObj.addProperty("hotel_name", hotel.hotelName);
                        
                        if (hotel.price != null) {
                            hotelObj.addProperty("price_per_night", hotel.price.amount);
                            hotelObj.addProperty("total_cost_2_nights", hotel.price.amount * 2);
                            
                            String hotelName = hotel.hotelName.toLowerCase();
                            double pricePerNight = hotel.price.amount;
                            
                            if (hotelName.contains("family") || hotelName.contains("suite")) {
                                hotelObj.addProperty("accommodation_type", "Family-Friendly Rooms");
                                hotelObj.addProperty("family_advantage", "Spacious rooms for multi-generational comfort");
                                familyRooms.add(hotelObj);
                            } else if (hotelName.contains("lodge") || hotelName.contains("inn")) {
                                hotelObj.addProperty("accommodation_type", "Historic Lodge");
                                hotelObj.addProperty("family_advantage", "Authentic park experience with rustic charm");
                                lodgeOptions.add(hotelObj);
                            } else if (pricePerNight <= 150) {
                                hotelObj.addProperty("accommodation_type", "Budget-Friendly Option");
                                hotelObj.addProperty("family_advantage", "Affordable for multiple family rooms");
                                budgetFriendly.add(hotelObj);
                            }
                            
                            JsonObject familyConsiderations = new JsonObject();
                            familyConsiderations.addProperty("proximity_to_park", "Minimize driving time for daily activities");
                            familyConsiderations.addProperty("senior_comfort", "Easy access and comfortable amenities");
                            familyConsiderations.addProperty("child_safety", "Family-friendly environment and secure facilities");
                            familyConsiderations.addProperty("group_coordination", "Close to camping families for easy meetups");
                            
                            hotelObj.add("family_considerations", familyConsiderations);
                        }
                    }
                    
                    familyAccommodation.add("family_room_options", familyRooms);
                    familyAccommodation.add("historic_lodge_options", lodgeOptions);
                    familyAccommodation.add("budget_friendly_options", budgetFriendly);
                    
                    accommodationResults.add("yellowstone_family_accommodations", familyAccommodation);
                }
                
            } catch (Exception e) {
                accommodationResults.addProperty("error", "Failed to search accommodations: " + e.getMessage());
            }
            
            output.add("accommodation_planning", accommodationResults);
            
            // Step 4: Search YouTube for Yellowstone family activities and wildlife viewing
            youtube_com youtube = new youtube_com(context);
            JsonObject educationResults = new JsonObject();
            
            try {
                java.util.List<youtube_com.YouTubeVideoInfo> yellowstoneVideos = youtube.searchVideos("Yellowstone family activities wildlife viewing");
                
                if (yellowstoneVideos != null) {
                    JsonObject familyEducation = new JsonObject();
                    familyEducation.addProperty("educational_focus", "Yellowstone wildlife, geology, and family-friendly activities");
                    
                    JsonArray wildlifeEducation = new JsonArray();
                    JsonArray safetyGuidelines = new JsonArray();
                    JsonArray familyActivities = new JsonArray();
                    JsonArray conservationLearning = new JsonArray();
                    
                    for (youtube_com.YouTubeVideoInfo video : yellowstoneVideos) {
                        JsonObject videoObj = new JsonObject();
                        videoObj.addProperty("video_title", video.title);
                        videoObj.addProperty("video_url", video.url);
                        
                        String videoTitle = video.title.toLowerCase();
                        
                        if (videoTitle.contains("wildlife") || videoTitle.contains("animals") || videoTitle.contains("bear") || videoTitle.contains("bison")) {
                            videoObj.addProperty("education_category", "Wildlife Viewing");
                            videoObj.addProperty("family_value", "Teach children and adults about park animals");
                            videoObj.addProperty("safety_importance", "Critical for safe wildlife encounters");
                            wildlifeEducation.add(videoObj);
                        } else if (videoTitle.contains("safety") || videoTitle.contains("rules") || videoTitle.contains("guidelines")) {
                            videoObj.addProperty("education_category", "Park Safety");
                            videoObj.addProperty("family_value", "Essential safety knowledge for all ages");
                            videoObj.addProperty("safety_importance", "Prevent accidents and ensure family safety");
                            safetyGuidelines.add(videoObj);
                        } else if (videoTitle.contains("family") || videoTitle.contains("kids") || videoTitle.contains("activities")) {
                            videoObj.addProperty("education_category", "Family Activities");
                            videoObj.addProperty("family_value", "Age-appropriate park experiences");
                            videoObj.addProperty("safety_importance", "Plan safe activities for multi-generational group");
                            familyActivities.add(videoObj);
                        } else {
                            videoObj.addProperty("education_category", "Nature Conservation");
                            videoObj.addProperty("family_value", "Educational value about park preservation");
                            videoObj.addProperty("safety_importance", "Understand environmental protection");
                            conservationLearning.add(videoObj);
                        }
                        
                        JsonObject familyLearningPlan = new JsonObject();
                        familyLearningPlan.addProperty("pre_trip_viewing", "Watch videos together before visiting park");
                        familyLearningPlan.addProperty("discussion_points", "Create family discussion about wildlife respect");
                        familyLearningPlan.addProperty("child_engagement", "Use videos to build excitement and knowledge");
                        familyLearningPlan.addProperty("safety_emphasis", "Review safety rules with all family members");
                        
                        videoObj.add("family_education_strategy", familyLearningPlan);
                    }
                    
                    familyEducation.add("wildlife_education_videos", wildlifeEducation);
                    familyEducation.add("safety_guideline_videos", safetyGuidelines);
                    familyEducation.add("family_activity_videos", familyActivities);
                    familyEducation.add("conservation_learning_videos", conservationLearning);
                    
                    educationResults.add("yellowstone_family_education", familyEducation);
                }
                
            } catch (Exception e) {
                educationResults.addProperty("error", "Failed to search educational videos: " + e.getMessage());
            }
            
            output.add("educational_planning", educationResults);
            
            // Step 5: Create comprehensive family reunion plan
            JsonObject reunionPlan = new JsonObject();
            reunionPlan.addProperty("event_title", "Yellowstone Family Reunion Outdoor Adventure");
            reunionPlan.addProperty("dates", "August 28-30, 2025");
            reunionPlan.addProperty("location", "Yellowstone National Park");
            reunionPlan.addProperty("participants", "20 family members, ages 8 to 75");
            reunionPlan.addProperty("mission", "Create memorable multi-generational experiences in nature");
            
            JsonObject reunionStrategy = new JsonObject();
            reunionStrategy.addProperty("accommodation_approach", "Mixed camping and lodging for comfort preferences");
            reunionStrategy.addProperty("equipment_strategy", "Shared bulk purchasing with family cost-sharing");
            reunionStrategy.addProperty("weather_preparation", "Layered clothing and indoor backup plans");
            reunionStrategy.addProperty("education_focus", "Wildlife learning and conservation awareness");
            
            JsonArray reunionActivities = new JsonArray();
            reunionActivities.add("Day 1: Arrival, setup camp, lodge check-in, family dinner");
            reunionActivities.add("Day 2: Wildlife viewing tour, hiking (age-appropriate trails), evening campfire");
            reunionActivities.add("Day 3: Geyser tour, family photos, departure preparations");
            
            JsonArray safetyProtocols = new JsonArray();
            safetyProtocols.add("Wildlife safety briefing for all family members");
            safetyProtocols.add("Buddy system for hiking and exploring");
            safetyProtocols.add("Emergency contact and meeting point procedures");
            safetyProtocols.add("Weather monitoring and backup plan activation");
            safetyProtocols.add("Senior and child safety considerations");
            
            reunionPlan.add("reunion_strategy", reunionStrategy);
            reunionPlan.add("planned_activities", reunionActivities);
            reunionPlan.add("safety_protocols", safetyProtocols);
            
            output.add("comprehensive_reunion_plan", reunionPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning family reunion: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
