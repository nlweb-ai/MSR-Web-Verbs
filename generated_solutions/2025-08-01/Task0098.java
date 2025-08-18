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


public class Task0098 {
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
        
        // Adventure club meetup details
        LocalDate meetupDate = LocalDate.of(2025, 8, 17);
        String meetupLocation = "Denver, Colorado";
        double idealTempMin = 60.0;
        double idealTempMax = 80.0;
        
        // Step 1: Check weather forecast for Denver
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // Get location coordinates for Denver
            List<OpenWeather.LocationData> locations = weather.getLocationsByName(meetupLocation);
            if (locations.isEmpty()) {
                weatherInfo.addProperty("error", "Denver location not found");
                weatherInfo.addProperty("outdoor_suitable", false);
                weatherInfo.addProperty("proceed_with_outdoor_planning", false);
            } else {
                OpenWeather.LocationData denverLocation = locations.get(0);
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(
                    denverLocation.getLatitude(), denverLocation.getLongitude());
                
                weatherInfo.addProperty("city", currentWeather.getCityName());
                weatherInfo.addProperty("temperature", currentWeather.getTemperature());
                weatherInfo.addProperty("condition", currentWeather.getCondition());
                weatherInfo.addProperty("description", currentWeather.getDescription());
                weatherInfo.addProperty("humidity", currentWeather.getHumidity());
                weatherInfo.addProperty("wind_speed", currentWeather.getWindSpeed());
                
                // Determine if suitable for outdoor activities
                boolean tempSuitable = currentWeather.getTemperature() >= idealTempMin && 
                                     currentWeather.getTemperature() <= idealTempMax;
                boolean conditionsClear = !currentWeather.getCondition().toLowerCase().contains("rain") &&
                                        !currentWeather.getCondition().toLowerCase().contains("storm") &&
                                        !currentWeather.getCondition().toLowerCase().contains("snow");
                boolean outdoorSuitable = tempSuitable && conditionsClear;
                
                weatherInfo.addProperty("temperature_suitable", tempSuitable);
                weatherInfo.addProperty("conditions_clear", conditionsClear);
                weatherInfo.addProperty("outdoor_suitable", outdoorSuitable);
                weatherInfo.addProperty("proceed_with_outdoor_planning", outdoorSuitable);
                weatherInfo.addProperty("weather_assessment", outdoorSuitable ? 
                    "Excellent conditions for outdoor adventure activities" : 
                    "Weather not ideal - consider indoor alternatives or rescheduling");
            }
        } catch (IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to fetch Denver weather: " + e.getMessage());
            weatherInfo.addProperty("outdoor_suitable", false);
            weatherInfo.addProperty("proceed_with_outdoor_planning", true); // Default to proceed for planning purposes
            weatherInfo.addProperty("weather_assessment", "Weather data unavailable - plan for all conditions");
        }
        result.add("weather_forecast", weatherInfo);
        
        // Note: Weather planning logic can be expanded here for future use
        
        // Step 2: Search for camping and hiking gear at Costco (proceed regardless of weather for preparedness)
        costco_com costco = new costco_com(context);
        String[] outdoorGear = {"camping gear", "hiking equipment", "outdoor clothing", "emergency supplies"};
        
        JsonObject gearInfo = new JsonObject();
        JsonArray gearArray = new JsonArray();
        double totalGearCost = 0.0;
        
        for (String gear : outdoorGear) {
            costco_com.ProductInfo productResult = costco.searchProduct(gear);
            JsonObject gearObj = new JsonObject();
            gearObj.addProperty("gear_type", gear);
            
            if (productResult.error != null) {
                gearObj.addProperty("error", productResult.error);
                double estimatedCost = getEstimatedGearCost(gear);
                gearObj.addProperty("estimated_cost", estimatedCost);
                totalGearCost += estimatedCost;
            } else {
                gearObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    gearObj.addProperty("cost", productResult.productPrice.amount);
                    gearObj.addProperty("currency", productResult.productPrice.currency);
                    totalGearCost += productResult.productPrice.amount;
                } else {
                    double estimatedCost = getEstimatedGearCost(gear);
                    gearObj.addProperty("estimated_cost", estimatedCost);
                    totalGearCost += estimatedCost;
                }
            }
            gearArray.add(gearObj);
        }
        
        // Calculate gear needs for club members (assuming 20 members)
        int clubMembers = 20;
        double gearCostPerMember = totalGearCost / 2; // Assume shared/bulk equipment reduces individual cost
        double totalClubGearInvestment = gearCostPerMember * clubMembers;
        
        gearInfo.add("outdoor_gear", gearArray);
        gearInfo.addProperty("estimated_club_members", clubMembers);
        gearInfo.addProperty("gear_cost_per_member", gearCostPerMember);
        gearInfo.addProperty("total_club_gear_investment", totalClubGearInvestment);
        gearInfo.addProperty("purpose", "Equip club members for safe outdoor adventures");
        result.add("gear_procurement", gearInfo);
        
        // Step 3: Find outdoor gear stores and adventure tour companies near Denver
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "Denver, Colorado";
        String businessDescription = "outdoor gear stores adventure tour companies";
        int maxLocations = 8;
        
        maps_google_com.NearestBusinessesResult partnersResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxLocations);
        
        JsonObject partnershipsInfo = new JsonObject();
        partnershipsInfo.addProperty("reference_point", partnersResult.referencePoint);
        partnershipsInfo.addProperty("search_type", partnersResult.businessDescription);
        partnershipsInfo.addProperty("purpose", "Establish partnerships and equipment rental relationships");
        
        JsonArray partnersArray = new JsonArray();
        for (maps_google_com.BusinessInfo partner : partnersResult.businesses) {
            JsonObject partnerObj = new JsonObject();
            partnerObj.addProperty("name", partner.name);
            partnerObj.addProperty("address", partner.address);
            
            // Categorize partner type based on name
            String partnerName = partner.name.toLowerCase();
            String partnerType = "other";
            if (partnerName.contains("gear") || partnerName.contains("equipment") || partnerName.contains("outdoor")) {
                partnerType = "outdoor_gear_store";
            } else if (partnerName.contains("tour") || partnerName.contains("guide") || partnerName.contains("adventure")) {
                partnerType = "adventure_tour_company";
            } else if (partnerName.contains("rental") || partnerName.contains("rent")) {
                partnerType = "equipment_rental";
            } else if (partnerName.contains("climbing") || partnerName.contains("hiking")) {
                partnerType = "specialized_adventure";
            }
            
            partnerObj.addProperty("partner_type", partnerType);
            partnerObj.addProperty("partnership_potential", assessPartnershipPotential(partnerType));
            partnersArray.add(partnerObj);
        }
        partnershipsInfo.add("potential_partners", partnersArray);
        partnershipsInfo.addProperty("total_partners_found", partnersArray.size());
        result.add("partnership_opportunities", partnershipsInfo);
        
        // Step 4: Search for outdoor adventure and hiking books in OpenLibrary
        OpenLibrary openLibrary = new OpenLibrary();
        JsonObject resourceLibraryInfo = new JsonObject();
        
        try {
            String[] adventureTopics = {"outdoor adventure", "hiking guides", "camping survival", "wilderness safety"};
            JsonArray booksArray = new JsonArray();
            
            for (String topic : adventureTopics) {
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
            
            resourceLibraryInfo.addProperty("purpose", "Create resource library for club members and plan future expeditions");
            resourceLibraryInfo.add("adventure_education_categories", booksArray);
            
            // Get additional outdoor adventure subjects
            List<OpenLibrary.SubjectInfo> outdoorSubjects = openLibrary.getSubject("outdoor adventure", false, 6, 0);
            JsonArray subjectsArray = new JsonArray();
            for (OpenLibrary.SubjectInfo subject : outdoorSubjects) {
                subjectsArray.add(subject.info);
            }
            resourceLibraryInfo.add("related_outdoor_subjects", subjectsArray);
            
        } catch (IOException | InterruptedException e) {
            resourceLibraryInfo.addProperty("error", "Failed to fetch adventure education materials: " + e.getMessage());
            resourceLibraryInfo.addProperty("recommendation", "Build resource library from local outdoor stores and guides");
        }
        
        result.add("resource_library", resourceLibraryInfo);
        
        // Adventure club meetup summary and recommendations
        JsonObject clubSummary = new JsonObject();
        clubSummary.addProperty("club_type", "Outdoor Adventure Club Meetup");
        clubSummary.addProperty("location", meetupLocation);
        clubSummary.addProperty("meetup_date", meetupDate.toString());
        clubSummary.addProperty("estimated_members", clubMembers);
        clubSummary.addProperty("weather_suitable", weatherInfo.has("outdoor_suitable") && weatherInfo.get("outdoor_suitable").getAsBoolean());
        clubSummary.addProperty("gear_investment_per_member", gearCostPerMember);
        clubSummary.addProperty("partnerships_identified", partnersArray.size());
        
        // Club recommendations based on weather and resources
        StringBuilder recommendations = new StringBuilder();
        recommendations.append("Denver's proximity to Rocky Mountains provides excellent outdoor adventure opportunities. ");
        
        boolean weatherSuitable = weatherInfo.has("outdoor_suitable") && weatherInfo.get("outdoor_suitable").getAsBoolean();
        if (weatherSuitable) {
            recommendations.append("Weather conditions are perfect for outdoor activities - proceed with hiking and camping plans. ");
        } else {
            recommendations.append("Weather may not be ideal - have backup indoor activities or consider rescheduling. ");
        }
        
        if (partnersArray.size() >= 6) {
            recommendations.append("Excellent variety of gear stores and tour companies for partnerships and rentals. ");
        } else {
            recommendations.append("Limited partnership options - expand search or focus on club-owned equipment. ");
        }
        
        if (totalClubGearInvestment > 15000) {
            recommendations.append("High gear investment - consider gradual acquisition or member equipment sharing program. ");
        } else {
            recommendations.append("Reasonable gear costs - club can build comprehensive equipment library. ");
        }
        
        recommendations.append("Focus on safety training and establish emergency protocols for all adventures. ");
        recommendations.append("Create progressive difficulty levels to accommodate members of all experience levels.");
        
        clubSummary.addProperty("planning_recommendations", recommendations.toString());
        
        // Adventure club program structure
        JsonObject programStructure = new JsonObject();
        if (weatherSuitable) {
            programStructure.addProperty("primary_activities", "Hiking, camping, rock climbing, wilderness survival");
            programStructure.addProperty("meetup_format", "Full-day outdoor adventure with safety briefing");
        } else {
            programStructure.addProperty("primary_activities", "Indoor climbing, gear maintenance, trip planning");
            programStructure.addProperty("meetup_format", "Indoor meeting with future adventure planning");
        }
        
        programStructure.addProperty("safety_focus", "Equipment training, emergency procedures, wilderness first aid");
        programStructure.addProperty("skill_development", "Progressive training from beginner to advanced levels");
        
        JsonArray activitySchedule = new JsonArray();
        if (weatherSuitable) {
            activitySchedule.add("9:00 AM - Safety briefing and equipment check");
            activitySchedule.add("10:00 AM - Departure to hiking location");
            activitySchedule.add("12:00 PM - Lunch break and group photos");
            activitySchedule.add("2:00 PM - Advanced hiking or skill workshops");
            activitySchedule.add("4:00 PM - Return and equipment maintenance");
        } else {
            activitySchedule.add("10:00 AM - Indoor meetup and introductions");
            activitySchedule.add("11:00 AM - Equipment demonstration and maintenance");
            activitySchedule.add("1:00 PM - Lunch and trip planning session");
            activitySchedule.add("3:00 PM - Indoor climbing or fitness activities");
            activitySchedule.add("5:00 PM - Resource sharing and future planning");
        }
        programStructure.add("meetup_schedule", activitySchedule);
        
        clubSummary.add("program_structure", programStructure);
        
        // Club growth and sustainability
        JsonObject clubDevelopment = new JsonObject();
        clubDevelopment.addProperty("growth_strategy", "Start with local Denver area, expand to Rocky Mountain expeditions");
        clubDevelopment.addProperty("membership_model", "Monthly dues for equipment and insurance, optional trip fees");
        clubDevelopment.addProperty("safety_certification", "Require wilderness first aid and leave-no-trace principles");
        
        JsonArray futureExpeditions = new JsonArray();
        futureExpeditions.add("Rocky Mountain National Park multi-day backpacking");
        futureExpeditions.add("14er peak climbing challenges");
        futureExpeditions.add("Winter snowshoeing and cross-country skiing");
        futureExpeditions.add("Desert camping in Colorado Plateau");
        clubDevelopment.add("planned_future_expeditions", futureExpeditions);
        
        // Equipment sharing and sustainability
        JsonObject equipmentManagement = new JsonObject();
        equipmentManagement.addProperty("shared_equipment", "Tents, cooking gear, emergency supplies, specialized climbing gear");
        equipmentManagement.addProperty("member_equipment", "Personal hiking boots, clothing, sleeping bags, daypacks");
        equipmentManagement.addProperty("rental_partnerships", "Leverage local gear stores for specialized equipment");
        equipmentManagement.addProperty("maintenance_schedule", "Monthly gear check and repair sessions");
        
        clubDevelopment.add("equipment_management", equipmentManagement);
        clubSummary.add("club_development", clubDevelopment);
        
        result.add("adventure_club_summary", clubSummary);
        
        return result;
    }
    
    // Helper method to estimate gear costs when Costco search fails
    private static double getEstimatedGearCost(String gear) {
        switch (gear.toLowerCase()) {
            case "camping gear":
                return 150.0;
            case "hiking equipment":
                return 200.0;
            case "outdoor clothing":
                return 100.0;
            case "emergency supplies":
                return 75.0;
            default:
                return 125.0;
        }
    }
    
    // Helper method to assess partnership potential
    private static String assessPartnershipPotential(String partnerType) {
        switch (partnerType) {
            case "outdoor_gear_store":
            case "equipment_rental":
                return "high";
            case "adventure_tour_company":
            case "specialized_adventure":
                return "medium";
            default:
                return "low";
        }
    }
}
