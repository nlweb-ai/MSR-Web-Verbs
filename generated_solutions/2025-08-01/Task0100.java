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


public class Task0100 {
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
        
        // Cultural exchange program details
        LocalDate programStartDate = LocalDate.of(2025, 8, 10);
        LocalDate programEndDate = LocalDate.of(2025, 8, 17);
        String programLocation = "Los Angeles, California";
        int internationalStudents = 8;
        
        // Step 1: Search for flights from New York to Los Angeles using Alaska Airlines
        alaskaair_com alaskaAir = new alaskaair_com(context);
        alaskaair_com.SearchFlightsResult flightResult = alaskaAir.searchFlights("JFK", "LAX", programStartDate, programEndDate);
        
        JsonObject flightInfo = new JsonObject();
        flightInfo.addProperty("origin", "New York (JFK)");
        flightInfo.addProperty("destination", "Los Angeles (LAX)");
        flightInfo.addProperty("departure_date", programStartDate.toString());
        flightInfo.addProperty("return_date", programEndDate.toString());
        flightInfo.addProperty("international_students", internationalStudents);
        
        if (flightResult.message != null) {
            flightInfo.addProperty("status", "No flights found");
            flightInfo.addProperty("message", flightResult.message);
            flightInfo.addProperty("estimated_cost_per_student", 450.0); // Estimated fallback
            flightInfo.addProperty("total_flight_cost", 450.0 * internationalStudents);
        } else if (flightResult.flightInfo != null && flightResult.flightInfo.price != null) {
            double costPerStudent = flightResult.flightInfo.price.amount;
            double totalFlightCost = costPerStudent * internationalStudents;
            
            flightInfo.addProperty("status", "Flights available");
            flightInfo.addProperty("cost_per_student", costPerStudent);
            flightInfo.addProperty("currency", flightResult.flightInfo.price.currency);
            flightInfo.addProperty("total_flight_cost", totalFlightCost);
            
            JsonArray flightsArray = new JsonArray();
            for (String flight : flightResult.flightInfo.flights) {
                flightsArray.add(flight);
            }
            flightInfo.add("available_flights", flightsArray);
        } else {
            flightInfo.addProperty("status", "Flight information incomplete");
            flightInfo.addProperty("estimated_cost_per_student", 450.0); // Estimated fallback
            flightInfo.addProperty("total_flight_cost", 450.0 * internationalStudents);
        }
        result.add("flight_information", flightInfo);
        
        // Step 2: Search for group accommodations or student housing in Los Angeles
        booking_com booking = new booking_com(context);
        booking_com.HotelSearchResult housingResult = booking.search_hotel(programLocation, programStartDate, programEndDate);
        
        JsonObject accommodationInfo = new JsonObject();
        accommodationInfo.addProperty("destination", housingResult.destination);
        accommodationInfo.addProperty("checkin_date", housingResult.checkinDate.toString());
        accommodationInfo.addProperty("checkout_date", housingResult.checkoutDate.toString());
        accommodationInfo.addProperty("program_duration_days", 7);
        accommodationInfo.addProperty("international_students", internationalStudents);
        accommodationInfo.addProperty("accommodation_type", "Group accommodations/student housing");
        
        JsonArray housingArray = new JsonArray();
        double averageRoomCost = 0.0;
        int validHousing = 0;
        
        for (booking_com.HotelInfo housing : housingResult.hotels) {
            JsonObject housingObj = new JsonObject();
            housingObj.addProperty("property_name", housing.hotelName);
            
            // Filter for student-friendly and group accommodation
            String propertyName = housing.hotelName.toLowerCase();
            boolean isStudentFriendly = propertyName.contains("hostel") || propertyName.contains("student") || 
                                      propertyName.contains("dorm") || propertyName.contains("budget") ||
                                      propertyName.contains("inn") || propertyName.contains("lodge");
            
            if (housing.price != null) {
                housingObj.addProperty("price_per_night", housing.price.amount);
                housingObj.addProperty("currency", housing.price.currency);
                housingObj.addProperty("student_friendly", isStudentFriendly);
                
                if (isStudentFriendly || housing.price.amount < 150.0) { // Include budget options
                    averageRoomCost += housing.price.amount;
                    validHousing++;
                }
            } else {
                housingObj.addProperty("price_per_night", "Price not available");
                housingObj.addProperty("student_friendly", isStudentFriendly);
            }
            housingArray.add(housingObj);
        }
        
        if (validHousing > 0) {
            averageRoomCost = averageRoomCost / validHousing;
        } else {
            averageRoomCost = 120.0; // Estimated for student housing in LA
        }
        
        // Calculate accommodation costs (2 students per room for 7 nights)
        int roomsNeeded = (internationalStudents + 1) / 2;
        double totalAccommodationCost = averageRoomCost * roomsNeeded * 7;
        
        accommodationInfo.add("housing_options", housingArray);
        accommodationInfo.addProperty("estimated_average_cost_per_room_per_night", averageRoomCost);
        accommodationInfo.addProperty("rooms_needed", roomsNeeded);
        accommodationInfo.addProperty("total_nights", 7);
        accommodationInfo.addProperty("total_accommodation_cost", totalAccommodationCost);
        result.add("accommodation_information", accommodationInfo);
        
        // Step 3: Calculate program fee per student
        double totalFlightCost = flightInfo.has("total_flight_cost") ? flightInfo.get("total_flight_cost").getAsDouble() : 0.0;
        double accommodationCostPerStudent = totalAccommodationCost / internationalStudents;
        double programAdministrationFee = 200.0; // Administrative costs, orientation, materials
        double totalCostPerStudent = (totalFlightCost / internationalStudents) + accommodationCostPerStudent + programAdministrationFee;
        double programFeePerStudent = totalCostPerStudent * 1.15; // 15% margin for contingencies
        
        JsonObject pricingInfo = new JsonObject();
        pricingInfo.addProperty("international_students", internationalStudents);
        pricingInfo.addProperty("flight_cost_per_student", totalFlightCost / internationalStudents);
        pricingInfo.addProperty("accommodation_cost_per_student", accommodationCostPerStudent);
        pricingInfo.addProperty("administration_fee_per_student", programAdministrationFee);
        pricingInfo.addProperty("total_cost_per_student", totalCostPerStudent);
        pricingInfo.addProperty("recommended_program_fee_per_student", Math.ceil(programFeePerStudent));
        pricingInfo.addProperty("total_program_revenue", Math.ceil(programFeePerStudent) * internationalStudents);
        pricingInfo.addProperty("contingency_buffer", "15% margin included for unexpected costs");
        result.add("program_pricing", pricingInfo);
        
        // Step 4: Find cultural centers and museums near Hollywood
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "Hollywood, Los Angeles, California";
        String businessDescription = "cultural centers museums";
        int maxLocations = 12;
        
        maps_google_com.NearestBusinessesResult culturalSitesResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxLocations);
        
        JsonObject itineraryInfo = new JsonObject();
        itineraryInfo.addProperty("reference_point", culturalSitesResult.referencePoint);
        itineraryInfo.addProperty("search_type", culturalSitesResult.businessDescription);
        itineraryInfo.addProperty("purpose", "Create educational itinerary showcasing American culture");
        
        JsonArray culturalSitesArray = new JsonArray();
        for (maps_google_com.BusinessInfo site : culturalSitesResult.businesses) {
            JsonObject siteObj = new JsonObject();
            siteObj.addProperty("name", site.name);
            siteObj.addProperty("address", site.address);
            
            // Categorize cultural site type based on name
            String siteName = site.name.toLowerCase();
            String siteType = "other";
            if (siteName.contains("museum")) {
                siteType = "museum";
            } else if (siteName.contains("theater") || siteName.contains("performance")) {
                siteType = "performing_arts";
            } else if (siteName.contains("cultural") || siteName.contains("culture")) {
                siteType = "cultural_center";
            } else if (siteName.contains("gallery") || siteName.contains("art")) {
                siteType = "art_gallery";
            } else if (siteName.contains("hollywood") || siteName.contains("entertainment")) {
                siteType = "entertainment_venue";
            }
            
            siteObj.addProperty("site_type", siteType);
            siteObj.addProperty("cultural_value", assessCulturalValue(siteName, siteType));
            siteObj.addProperty("educational_potential", assessEducationalPotential(siteType));
            culturalSitesArray.add(siteObj);
        }
        itineraryInfo.add("cultural_sites", culturalSitesArray);
        itineraryInfo.addProperty("total_sites_found", culturalSitesArray.size());
        result.add("cultural_itinerary", itineraryInfo);
        
        // Step 5: Search for cross-cultural communication and American culture books
        OpenLibrary openLibrary = new OpenLibrary();
        JsonObject orientationMaterialsInfo = new JsonObject();
        
        try {
            String[] culturalTopics = {"cross-cultural communication", "American culture", "cultural exchange", "international students"};
            JsonArray booksArray = new JsonArray();
            
            for (String topic : culturalTopics) {
                List<OpenLibrary.BookInfo> books = openLibrary.search(topic, null, null, null, 3, 1);
                
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
            
            orientationMaterialsInfo.addProperty("purpose", "Prepare orientation materials for international participants");
            orientationMaterialsInfo.add("orientation_categories", booksArray);
            
            // Get additional American culture subjects
            List<OpenLibrary.SubjectInfo> americanCultureSubjects = openLibrary.getSubject("American culture", false, 5, 0);
            JsonArray subjectsArray = new JsonArray();
            for (OpenLibrary.SubjectInfo subject : americanCultureSubjects) {
                subjectsArray.add(subject.info);
            }
            orientationMaterialsInfo.add("related_cultural_subjects", subjectsArray);
            
        } catch (IOException | InterruptedException e) {
            orientationMaterialsInfo.addProperty("error", "Failed to fetch orientation materials: " + e.getMessage());
            orientationMaterialsInfo.addProperty("recommendation", "Use professional cultural orientation resources and academic materials");
        }
        
        result.add("orientation_materials", orientationMaterialsInfo);
        
        // Cultural exchange program summary and recommendations
        JsonObject programSummary = new JsonObject();
        programSummary.addProperty("program_type", "Cultural Exchange Program");
        programSummary.addProperty("location", programLocation);
        programSummary.addProperty("dates", programStartDate.toString() + " to " + programEndDate.toString());
        programSummary.addProperty("duration_days", 7);
        programSummary.addProperty("international_students", internationalStudents);
        programSummary.addProperty("recommended_fee_per_student", Math.ceil(programFeePerStudent));
        programSummary.addProperty("cultural_sites_identified", culturalSitesArray.size());
        
        // Program recommendations
        StringBuilder recommendations = new StringBuilder();
        recommendations.append("Los Angeles offers exceptional diversity and entertainment industry exposure for international students. ");
        
        if (Math.ceil(programFeePerStudent) < 1200) {
            recommendations.append("Competitive program pricing allows for comprehensive cultural immersion experience. ");
        } else {
            recommendations.append("Higher program costs - consider partnerships or scholarships to ensure accessibility. ");
        }
        
        if (culturalSitesArray.size() >= 10) {
            recommendations.append("Excellent variety of cultural sites available - create themed daily excursions. ");
        } else {
            recommendations.append("Limited cultural sites found - expand search to include beaches, studios, and neighborhoods. ");
        }
        
        recommendations.append("Include Hollywood entertainment industry tours and multicultural neighborhood visits. ");
        recommendations.append("Arrange homestay opportunities or cultural mentor pairings with local students. ");
        recommendations.append("Focus on practical cultural skills like dining etiquette, social norms, and slang.");
        
        programSummary.addProperty("program_recommendations", recommendations.toString());
        
        // Program structure and cultural learning objectives
        JsonObject programStructure = new JsonObject();
        programStructure.addProperty("orientation_day", "Cultural briefing, city orientation, welcome dinner");
        programStructure.addProperty("daily_structure", "Morning cultural site visit, afternoon activities, evening reflection");
        programStructure.addProperty("language_component", "Conversational English practice with local volunteers");
        programStructure.addProperty("cultural_immersion", "Home visits, local dining experiences, community events");
        
        JsonArray weeklySchedule = new JsonArray();
        weeklySchedule.add("Day 1: Arrival, orientation, Hollywood Walk of Fame");
        weeklySchedule.add("Day 2: Getty Center, Beverly Hills cultural tour");
        weeklySchedule.add("Day 3: Santa Monica Pier, beach culture experience");
        weeklySchedule.add("Day 4: Downtown LA museums, Arts District exploration");
        weeklySchedule.add("Day 5: Studio tours, entertainment industry insights");
        weeklySchedule.add("Day 6: Multicultural neighborhoods, ethnic cuisines");
        weeklySchedule.add("Day 7: Farewell ceremony, cultural presentations, departure");
        programStructure.add("suggested_daily_schedule", weeklySchedule);
        
        JsonArray learningObjectives = new JsonArray();
        learningObjectives.add("Understand American social customs and communication styles");
        learningObjectives.add("Experience diverse cultural communities within LA");
        learningObjectives.add("Develop practical language skills for daily interactions");
        learningObjectives.add("Gain insights into American entertainment and media culture");
        learningObjectives.add("Build lasting connections with local students and mentors");
        learningObjectives.add("Enhance global perspective and cultural sensitivity");
        programStructure.add("cultural_learning_objectives", learningObjectives);
        
        programSummary.add("program_structure", programStructure);
        
        // Logistics and support services
        JsonObject logisticsInfo = new JsonObject();
        logisticsInfo.addProperty("airport_pickup", "Coordinated group transportation from LAX");
        logisticsInfo.addProperty("local_transportation", "Metro passes and group van for excursions");
        logisticsInfo.addProperty("meal_arrangements", "Mix of group dining and independent exploration");
        logisticsInfo.addProperty("emergency_support", "24/7 program coordinator contact");
        
        JsonArray supportServices = new JsonArray();
        supportServices.add("Pre-arrival cultural preparation materials");
        supportServices.add("Local SIM cards and communication setup");
        supportServices.add("Cultural mentor assignments");
        supportServices.add("Emergency contact information and procedures");
        supportServices.add("Post-program cultural adjustment resources");
        logisticsInfo.add("student_support_services", supportServices);
        
        JsonArray partnerships = new JsonArray();
        partnerships.add("Local universities for peer mentor program");
        partnerships.add("Cultural organizations for authentic experiences");
        partnerships.add("Homestay families for immersive cultural exchange");
        partnerships.add("Entertainment industry for behind-the-scenes access");
        logisticsInfo.add("recommended_partnerships", partnerships);
        
        programSummary.add("logistics_and_support", logisticsInfo);
        
        // Assessment and follow-up
        JsonObject assessmentPlan = new JsonObject();
        assessmentPlan.addProperty("daily_reflection", "Group discussions on cultural observations and insights");
        assessmentPlan.addProperty("final_presentation", "Students present cultural learning to local audience");
        assessmentPlan.addProperty("post_program_survey", "Evaluation of cultural learning and program satisfaction");
        assessmentPlan.addProperty("alumni_network", "Ongoing connection with program participants");
        
        JsonArray successMetrics = new JsonArray();
        successMetrics.add("Increased cultural awareness and sensitivity");
        successMetrics.add("Improved English communication confidence");
        successMetrics.add("Positive program evaluation scores (4.5+ out of 5)");
        successMetrics.add("Sustained friendships with American students");
        successMetrics.add("Interest in future educational exchanges");
        assessmentPlan.add("program_success_indicators", successMetrics);
        
        programSummary.add("assessment_and_follow_up", assessmentPlan);
        
        result.add("cultural_exchange_program_summary", programSummary);
        
        return result;
    }
    
    // Helper method to assess cultural value of sites
    private static String assessCulturalValue(String siteName, String siteType) {
        if (siteType.equals("museum") || siteType.equals("cultural_center")) {
            return "high";
        } else if (siteType.equals("art_gallery") || siteType.equals("performing_arts")) {
            return "medium-high";
        } else if (siteName.contains("hollywood") || siteName.contains("american")) {
            return "high";
        } else {
            return "medium";
        }
    }
    
    // Helper method to assess educational potential
    private static String assessEducationalPotential(String siteType) {
        switch (siteType) {
            case "museum":
            case "cultural_center":
                return "excellent";
            case "art_gallery":
            case "performing_arts":
                return "good";
            case "entertainment_venue":
                return "medium";
            default:
                return "fair";
        }
    }
}
