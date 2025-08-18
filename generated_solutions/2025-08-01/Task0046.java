import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0046 {
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
            // Step 1: Search for senior-friendly technology devices at Costco
            costco_com costco = new costco_com(context);
            JsonObject deviceResults = new JsonObject();
            
            try {
                costco_com.ProductListResult techDevices = costco.searchProducts("tablet smartphone smart home devices");
                
                if (techDevices != null) {
                    JsonObject seniorTechSetup = new JsonObject();
                    seniorTechSetup.addProperty("workshop_date", "August 12, 2025");
                    seniorTechSetup.addProperty("location", "Phoenix, Arizona");
                    seniorTechSetup.addProperty("target_audience", "30 seniors aged 65 and older");
                    seniorTechSetup.addProperty("focus", "Beginner-friendly technology with accessibility features");
                    
                    JsonArray basicCommunication = new JsonArray();
                    JsonArray homeAutomation = new JsonArray();
                    JsonArray entertainment = new JsonArray();
                    JsonArray assistiveTech = new JsonArray();
                    
                    double basicPackageCost = 0.0;
                    double homeAutomationCost = 0.0;
                    double entertainmentCost = 0.0;
                    
                    if (techDevices.products != null) {
                        for (costco_com.ProductInfo device : techDevices.products) {
                            JsonObject deviceObj = new JsonObject();
                            deviceObj.addProperty("device_name", device.productName);
                            
                            if (device.productPrice != null) {
                                deviceObj.addProperty("price", device.productPrice.amount);
                                deviceObj.addProperty("currency", device.productPrice.currency);
                                
                                String deviceName = device.productName.toLowerCase();
                                double price = device.productPrice.amount;
                                
                                // Categorize devices for senior accessibility
                                if (deviceName.contains("tablet") || deviceName.contains("ipad")) {
                                    deviceObj.addProperty("device_category", "Communication Tablet");
                                    deviceObj.addProperty("senior_benefits", "Large screen, simple interface for video calls and messaging");
                                    deviceObj.addProperty("accessibility_features", "Text size adjustment, voice commands, simplified apps");
                                    deviceObj.addProperty("learning_difficulty", "Beginner - intuitive touch interface");
                                    basicCommunication.add(deviceObj);
                                    basicPackageCost += price;
                                } else if (deviceName.contains("smartphone") || deviceName.contains("phone")) {
                                    deviceObj.addProperty("device_category", "Senior Smartphone");
                                    deviceObj.addProperty("senior_benefits", "Emergency features, health monitoring, family connectivity");
                                    deviceObj.addProperty("accessibility_features", "Large buttons, loud speaker, emergency SOS");
                                    deviceObj.addProperty("learning_difficulty", "Intermediate - requires practice with apps");
                                    basicCommunication.add(deviceObj);
                                    basicPackageCost += price;
                                } else if (deviceName.contains("smart") && (deviceName.contains("speaker") || deviceName.contains("alexa") || deviceName.contains("google"))) {
                                    deviceObj.addProperty("device_category", "Voice Assistant");
                                    deviceObj.addProperty("senior_benefits", "Voice control for lights, music, weather, reminders");
                                    deviceObj.addProperty("accessibility_features", "No screen needed, voice-only interaction");
                                    deviceObj.addProperty("learning_difficulty", "Easy - natural speech commands");
                                    homeAutomation.add(deviceObj);
                                    homeAutomationCost += price;
                                } else if (deviceName.contains("tv") || deviceName.contains("streaming") || deviceName.contains("roku")) {
                                    deviceObj.addProperty("device_category", "Entertainment Device");
                                    deviceObj.addProperty("senior_benefits", "Access to movies, music, educational content");
                                    deviceObj.addProperty("accessibility_features", "Large remote buttons, voice search");
                                    deviceObj.addProperty("learning_difficulty", "Beginner - simple remote control");
                                    entertainment.add(deviceObj);
                                    entertainmentCost += price;
                                } else {
                                    deviceObj.addProperty("device_category", "General Technology");
                                    deviceObj.addProperty("senior_benefits", "Various technology assistance");
                                    deviceObj.addProperty("accessibility_features", "Depends on specific device");
                                    deviceObj.addProperty("learning_difficulty", "Variable");
                                    assistiveTech.add(deviceObj);
                                }
                                
                                // Workshop teaching strategy
                                JsonObject teachingStrategy = new JsonObject();
                                teachingStrategy.addProperty("demo_time", "15-20 minutes hands-on practice");
                                teachingStrategy.addProperty("instruction_pace", "Slow and repetitive with patience");
                                teachingStrategy.addProperty("support_ratio", "1 instructor per 5 seniors for personalized help");
                                teachingStrategy.addProperty("practice_sessions", "Multiple short sessions rather than long tutorials");
                                
                                deviceObj.add("workshop_teaching_approach", teachingStrategy);
                            }
                        }
                    }
                    
                    seniorTechSetup.add("basic_communication_package", basicCommunication);
                    seniorTechSetup.add("home_automation_package", homeAutomation);
                    seniorTechSetup.add("entertainment_package", entertainment);
                    seniorTechSetup.add("assistive_technology", assistiveTech);
                    
                    seniorTechSetup.addProperty("basic_package_cost", basicPackageCost);
                    seniorTechSetup.addProperty("home_automation_cost", homeAutomationCost);
                    seniorTechSetup.addProperty("entertainment_cost", entertainmentCost);
                    
                    // Workshop budget planning
                    JsonObject budgetPlanning = new JsonObject();
                    budgetPlanning.addProperty("devices_per_participant", "1 practice device per 2-3 seniors");
                    budgetPlanning.addProperty("total_devices_needed", "10-15 devices for hands-on learning");
                    budgetPlanning.addProperty("demonstration_budget", "$2,000-4,000 for workshop devices");
                    budgetPlanning.addProperty("take_home_options", "Information packets for personal purchasing");
                    
                    seniorTechSetup.add("workshop_budget_planning", budgetPlanning);
                    deviceResults.add("senior_technology_workshop_setup", seniorTechSetup);
                }
                
                deviceResults.addProperty("workshop_objective", "Help seniors become comfortable with modern technology");
                deviceResults.addProperty("teaching_approach", "Patient, hands-on instruction with accessibility focus");
                
            } catch (Exception e) {
                deviceResults.addProperty("error", "Failed to search technology devices: " + e.getMessage());
            }
            
            output.add("technology_device_planning", deviceResults);
            
            // Step 2: Search YouTube for technology tutorials for seniors
            youtube_com youtube = new youtube_com(context);
            JsonObject educationResults = new JsonObject();
            
            try {
                java.util.List<youtube_com.YouTubeVideoInfo> seniorTutorials = youtube.searchVideos("technology tutorials for seniors");
                
                if (seniorTutorials != null) {
                    JsonObject educationalContent = new JsonObject();
                    educationalContent.addProperty("content_focus", "Age-appropriate technology education");
                    educationalContent.addProperty("teaching_style", "Slow, clear explanations with visual demonstrations");
                    
                    JsonArray emailTutorials = new JsonArray();
                    JsonArray videoCallingTutorials = new JsonArray();
                    JsonArray safetyTutorials = new JsonArray();
                    JsonArray basicSkillsTutorials = new JsonArray();
                    
                    for (youtube_com.YouTubeVideoInfo video : seniorTutorials) {
                        JsonObject videoObj = new JsonObject();
                        videoObj.addProperty("video_title", video.title);
                        videoObj.addProperty("video_url", video.url);
                        
                        String videoTitle = video.title.toLowerCase();
                        
                        if (videoTitle.contains("email") || videoTitle.contains("gmail") || videoTitle.contains("mail")) {
                            videoObj.addProperty("tutorial_category", "Email Communication");
                            videoObj.addProperty("workshop_value", "Essential skill for staying connected with family");
                            videoObj.addProperty("difficulty_level", "Beginner - step-by-step email basics");
                            videoObj.addProperty("workshop_use", "Project tutorial during hands-on session");
                            emailTutorials.add(videoObj);
                        } else if (videoTitle.contains("video") && (videoTitle.contains("call") || videoTitle.contains("chat") || videoTitle.contains("zoom"))) {
                            videoObj.addProperty("tutorial_category", "Video Calling");
                            videoObj.addProperty("workshop_value", "Face-to-face communication with distant family");
                            videoObj.addProperty("difficulty_level", "Intermediate - requires camera and audio setup");
                            videoObj.addProperty("workshop_use", "Live demonstration with partner practice");
                            videoCallingTutorials.add(videoObj);
                        } else if (videoTitle.contains("safety") || videoTitle.contains("scam") || videoTitle.contains("security")) {
                            videoObj.addProperty("tutorial_category", "Online Safety");
                            videoObj.addProperty("workshop_value", "Protect against fraud and maintain privacy");
                            videoObj.addProperty("difficulty_level", "Important - critical safety awareness");
                            videoObj.addProperty("workshop_use", "Educational presentation with practical examples");
                            safetyTutorials.add(videoObj);
                        } else {
                            videoObj.addProperty("tutorial_category", "Basic Technology Skills");
                            videoObj.addProperty("workshop_value", "General technology confidence building");
                            videoObj.addProperty("difficulty_level", "Varies - assess individual needs");
                            videoObj.addProperty("workshop_use", "Supplementary learning material");
                            basicSkillsTutorials.add(videoObj);
                        }
                        
                        // Workshop integration strategy
                        JsonObject integrationStrategy = new JsonObject();
                        integrationStrategy.addProperty("presentation_method", "Large screen projection with audio enhancement");
                        integrationStrategy.addProperty("pause_frequency", "Every 2-3 minutes for questions and practice");
                        integrationStrategy.addProperty("repetition_strategy", "Show key steps multiple times");
                        integrationStrategy.addProperty("follow_up", "Provide video links for home practice");
                        
                        videoObj.add("workshop_integration", integrationStrategy);
                    }
                    
                    educationalContent.add("email_communication_tutorials", emailTutorials);
                    educationalContent.add("video_calling_tutorials", videoCallingTutorials);
                    educationalContent.add("online_safety_tutorials", safetyTutorials);
                    educationalContent.add("basic_skills_tutorials", basicSkillsTutorials);
                    
                    // Curriculum development
                    JsonObject curriculumPlan = new JsonObject();
                    curriculumPlan.addProperty("session_1", "Device basics and safety awareness (1 hour)");
                    curriculumPlan.addProperty("session_2", "Email setup and basic communication (1 hour)");
                    curriculumPlan.addProperty("session_3", "Video calling with family practice (1 hour)");
                    curriculumPlan.addProperty("session_4", "Questions, troubleshooting, and advanced tips (30 minutes)");
                    
                    JsonArray teachingPrinciples = new JsonArray();
                    teachingPrinciples.add("Use large fonts and high contrast displays");
                    teachingPrinciples.add("Speak clearly and repeat instructions");
                    teachingPrinciples.add("Allow extra time for each step");
                    teachingPrinciples.add("Encourage questions and provide patient support");
                    teachingPrinciples.add("Focus on practical, relevant applications");
                    
                    curriculumPlan.add("senior_teaching_principles", teachingPrinciples);
                    educationalContent.add("workshop_curriculum", curriculumPlan);
                    
                    educationResults.add("senior_technology_education", educationalContent);
                }
                
                educationResults.addProperty("educational_strategy", "Patient, step-by-step learning appropriate for seniors");
                educationResults.addProperty("accessibility_focus", "Large fonts, clear audio, simplified interfaces");
                
            } catch (Exception e) {
                educationResults.addProperty("error", "Failed to search education videos: " + e.getMessage());
            }
            
            output.add("educational_content_planning", educationResults);
            
            // Step 3: Check weather conditions in Phoenix, Arizona
            JsonObject weatherResults = new JsonObject();
            
            try {
                // Note: Using placeholder weather data since exact API method unknown
                JsonObject workshopWeather = new JsonObject();
                workshopWeather.addProperty("workshop_date", "August 12, 2025");
                workshopWeather.addProperty("location", "Phoenix, Arizona");
                workshopWeather.addProperty("expected_temperature", "105-110°F typical for August");
                workshopWeather.addProperty("weather_concerns", "Extreme heat requires indoor air-conditioned venue");
                
                // Indoor climate planning for senior comfort
                JsonObject climateConsiderations = new JsonObject();
                climateConsiderations.addProperty("air_conditioning_priority", "Essential for senior comfort in Phoenix heat");
                climateConsiderations.addProperty("room_temperature_target", "72-76°F for optimal learning environment");
                climateConsiderations.addProperty("humidity_control", "Maintain comfortable humidity for respiratory health");
                climateConsiderations.addProperty("ventilation_needs", "Good air circulation for 30+ person workshop");
                
                // Workshop logistics based on weather
                JsonObject weatherLogistics = new JsonObject();
                weatherLogistics.addProperty("indoor_venue_requirement", "Fully air-conditioned facility mandatory");
                weatherLogistics.addProperty("arrival_timing", "Early morning setup before peak heat");
                weatherLogistics.addProperty("hydration_stations", "Multiple water stations for senior participants");
                weatherLogistics.addProperty("emergency_protocols", "Heat-related health monitoring for seniors");
                
                JsonArray outdoorDemonstrations = new JsonArray();
                outdoorDemonstrations.add("Smart garden devices - brief covered patio demonstration only");
                outdoorDemonstrations.add("Home security cameras - indoor simulation preferred");
                outdoorDemonstrations.add("Smart thermostats - indoor demonstration with AC unit");
                
                weatherLogistics.add("modified_outdoor_activities", outdoorDemonstrations);
                
                workshopWeather.add("senior_climate_considerations", climateConsiderations);
                workshopWeather.add("weather_based_logistics", weatherLogistics);
                
                weatherResults.add("phoenix_workshop_weather_planning", workshopWeather);
                
                weatherResults.addProperty("weather_priority", "Ensure senior comfort and safety in Phoenix summer heat");
                weatherResults.addProperty("venue_requirement", "Indoor air-conditioned facility essential");
                
            } catch (Exception e) {
                weatherResults.addProperty("error", "Failed to get weather data: " + e.getMessage());
            }
            
            output.add("weather_planning", weatherResults);
            
            // Step 4: Find senior centers and accessible community facilities near Phoenix
            maps_google_com maps = new maps_google_com(context);
            JsonObject venueResults = new JsonObject();
            
            try {
                maps_google_com.NearestBusinessesResult seniorFacilities = maps.get_nearestBusinesses("Phoenix Arizona", "senior centers community facilities", 10);
                
                if (seniorFacilities != null) {
                    JsonObject workshopVenues = new JsonObject();
                    workshopVenues.addProperty("search_area", seniorFacilities.referencePoint);
                    workshopVenues.addProperty("accessibility_focus", "Wheelchair accessible with proper lighting and seating");
                    workshopVenues.addProperty("capacity_requirement", "30 seniors plus instructors and assistants");
                    
                    JsonArray accessibleVenues = new JsonArray();
                    JsonArray seniorCenters = new JsonArray();
                    JsonArray communityFacilities = new JsonArray();
                    JsonArray librarySpaces = new JsonArray();
                    
                    if (seniorFacilities.businesses != null) {
                        for (maps_google_com.BusinessInfo facility : seniorFacilities.businesses) {
                            JsonObject facilityObj = new JsonObject();
                            facilityObj.addProperty("facility_name", facility.name);
                            facilityObj.addProperty("address", facility.address);
                            
                            String facilityName = facility.name.toLowerCase();
                            
                            if (facilityName.contains("senior") || facilityName.contains("aging") || facilityName.contains("elder")) {
                                facilityObj.addProperty("venue_category", "Senior Center");
                                facilityObj.addProperty("accessibility_advantages", "Designed specifically for senior accessibility");
                                facilityObj.addProperty("equipment_likelihood", "May have large-screen displays and assistive listening");
                                facilityObj.addProperty("audience_comfort", "Familiar environment for target demographic");
                                seniorCenters.add(facilityObj);
                            } else if (facilityName.contains("community") || facilityName.contains("recreation") || facilityName.contains("civic")) {
                                facilityObj.addProperty("venue_category", "Community Center");
                                facilityObj.addProperty("accessibility_advantages", "Public accessibility compliance required");
                                facilityObj.addProperty("equipment_likelihood", "Meeting rooms with AV equipment available");
                                facilityObj.addProperty("audience_comfort", "Neutral public space welcoming to all");
                                communityFacilities.add(facilityObj);
                            } else if (facilityName.contains("library") || facilityName.contains("learning")) {
                                facilityObj.addProperty("venue_category", "Library Learning Center");
                                facilityObj.addProperty("accessibility_advantages", "ADA compliant with quiet learning environment");
                                facilityObj.addProperty("equipment_likelihood", "Technology labs and presentation equipment");
                                facilityObj.addProperty("audience_comfort", "Educational atmosphere supports learning goals");
                                librarySpaces.add(facilityObj);
                            } else {
                                facilityObj.addProperty("venue_category", "General Community Facility");
                                facilityObj.addProperty("accessibility_advantages", "Varies - requires individual assessment");
                                facilityObj.addProperty("equipment_likelihood", "Unknown - needs site visit");
                                facilityObj.addProperty("audience_comfort", "Depends on facility type and atmosphere");
                            }
                            
                            // Accessibility requirements assessment
                            JsonObject accessibilityRequirements = new JsonObject();
                            accessibilityRequirements.addProperty("wheelchair_access", "Ramps, wide doorways, accessible restrooms");
                            accessibilityRequirements.addProperty("lighting_requirements", "Bright, even lighting for reading and device visibility");
                            accessibilityRequirements.addProperty("seating_needs", "Comfortable chairs with back support for 3+ hour session");
                            accessibilityRequirements.addProperty("audio_support", "Microphone system and hearing loop if available");
                            accessibilityRequirements.addProperty("climate_control", "Reliable air conditioning for Phoenix summer");
                            
                            facilityObj.add("senior_accessibility_requirements", accessibilityRequirements);
                            
                            // Workshop setup considerations
                            JsonObject setupConsiderations = new JsonObject();
                            setupConsiderations.addProperty("table_arrangement", "Small groups of 4-5 seniors for peer support");
                            setupConsiderations.addProperty("technology_setup", "Power outlets for device charging stations");
                            setupConsiderations.addProperty("projection_needs", "Large screen visible from all seats");
                            setupConsiderations.addProperty("support_stations", "Help desk areas for individual assistance");
                            
                            facilityObj.add("workshop_setup_considerations", setupConsiderations);
                            accessibleVenues.add(facilityObj);
                        }
                    }
                    
                    workshopVenues.add("senior_center_options", seniorCenters);
                    workshopVenues.add("community_facility_options", communityFacilities);
                    workshopVenues.add("library_learning_spaces", librarySpaces);
                    workshopVenues.add("all_accessible_venues", accessibleVenues);
                    
                    // Venue selection criteria
                    JsonObject selectionCriteria = new JsonObject();
                    selectionCriteria.addProperty("primary_criterion", "Full wheelchair accessibility and senior-friendly design");
                    selectionCriteria.addProperty("secondary_criterion", "Reliable air conditioning and comfortable seating");
                    selectionCriteria.addProperty("technology_criterion", "Large screen capability and good acoustics");
                    selectionCriteria.addProperty("logistics_criterion", "Convenient parking and public transportation access");
                    
                    JsonArray evaluationChecklist = new JsonArray();
                    evaluationChecklist.add("Site visit to verify accessibility features");
                    evaluationChecklist.add("Test audio/visual equipment capabilities");
                    evaluationChecklist.add("Confirm air conditioning reliability for August");
                    evaluationChecklist.add("Assess parking availability and proximity");
                    evaluationChecklist.add("Verify restroom accessibility and location");
                    
                    selectionCriteria.add("venue_evaluation_checklist", evaluationChecklist);
                    workshopVenues.add("venue_selection_criteria", selectionCriteria);
                    
                    venueResults.add("phoenix_workshop_venues", workshopVenues);
                }
                
                venueResults.addProperty("venue_priority", "Accessibility and comfort for 30 seniors aged 65+");
                venueResults.addProperty("location_focus", "Phoenix area with convenient access and parking");
                
            } catch (Exception e) {
                venueResults.addProperty("error", "Failed to find suitable venues: " + e.getMessage());
            }
            
            output.add("venue_planning", venueResults);
            
            // Step 5: Create comprehensive senior technology workshop plan
            JsonObject workshopPlan = new JsonObject();
            workshopPlan.addProperty("workshop_title", "Senior Citizens Technology Workshop");
            workshopPlan.addProperty("date", "August 12, 2025");
            workshopPlan.addProperty("location", "Phoenix, Arizona");
            workshopPlan.addProperty("target_audience", "30 seniors aged 65 and older");
            workshopPlan.addProperty("mission", "Help seniors become more comfortable with modern technology");
            
            // Comprehensive workshop strategy
            JsonObject workshopStrategy = new JsonObject();
            workshopStrategy.addProperty("device_approach", "Senior-friendly technology with accessibility features");
            workshopStrategy.addProperty("educational_method", "Patient, hands-on instruction with peer support");
            workshopStrategy.addProperty("venue_strategy", "Accessible, comfortable environment with reliable climate control");
            workshopStrategy.addProperty("weather_accommodation", "Indoor air-conditioned facility for Phoenix summer");
            
            JsonArray workshopObjectives = new JsonArray();
            workshopObjectives.add("Reduce technology anxiety through patient, supportive instruction");
            workshopObjectives.add("Teach practical skills for staying connected with family");
            workshopObjectives.add("Promote online safety and fraud awareness");
            workshopObjectives.add("Build confidence in using everyday technology");
            workshopObjectives.add("Create ongoing support network among participants");
            
            workshopStrategy.add("learning_objectives", workshopObjectives);
            
            // Implementation timeline
            JsonObject implementationPlan = new JsonObject();
            
            JsonArray preparationPhase = new JsonArray();
            preparationPhase.add("Week 1: Secure accessible venue with air conditioning");
            preparationPhase.add("Week 2: Purchase demonstration devices and setup materials");
            preparationPhase.add("Week 3: Prepare educational content and practice presentations");
            preparationPhase.add("Week 4: Recruit additional volunteers and confirm attendance");
            
            JsonArray workshopDay = new JsonArray();
            workshopDay.add("8:00 AM: Setup equipment and test air conditioning");
            workshopDay.add("9:00 AM: Welcome and introduction to technology basics");
            workshopDay.add("10:00 AM: Hands-on device practice with tablets");
            workshopDay.add("11:00 AM: Break and individual assistance");
            workshopDay.add("11:30 AM: Email and communication skills");
            workshopDay.add("12:30 PM: Lunch break with tech discussion");
            workshopDay.add("1:30 PM: Video calling demonstration and practice");
            workshopDay.add("2:30 PM: Online safety and fraud prevention");
            workshopDay.add("3:30 PM: Q&A, troubleshooting, and resources");
            
            implementationPlan.add("preparation_timeline", preparationPhase);
            implementationPlan.add("workshop_day_schedule", workshopDay);
            
            // Success metrics and follow-up
            JsonArray successIndicators = new JsonArray();
            successIndicators.add("90% of participants complete basic device operation");
            successIndicators.add("75% successfully send an email during workshop");
            successIndicators.add("60% make a video call with assistance");
            successIndicators.add("100% learn key online safety practices");
            successIndicators.add("80% express increased confidence with technology");
            
            JsonArray followUpSupport = new JsonArray();
            followUpSupport.add("Provide resource cards with key contact information");
            followUpSupport.add("Schedule monthly follow-up sessions for ongoing support");
            followUpSupport.add("Create buddy system for peer learning partnerships");
            followUpSupport.add("Establish help hotline for technology questions");
            followUpSupport.add("Develop family caregiver educational materials");
            
            workshopPlan.add("workshop_strategy", workshopStrategy);
            workshopPlan.add("implementation_plan", implementationPlan);
            workshopPlan.add("success_metrics", successIndicators);
            workshopPlan.add("ongoing_support", followUpSupport);
            
            output.add("comprehensive_workshop_plan", workshopPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning senior technology workshop: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
