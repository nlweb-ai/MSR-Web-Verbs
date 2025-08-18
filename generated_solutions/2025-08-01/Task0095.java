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


public class Task0095 {
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
        
        // Wellness retreat details
        LocalDate retreatDate = LocalDate.of(2025, 8, 29);
        LocalDate checkoutDate = retreatDate.plusDays(2); // 3-day retreat
        int totalParticipants = 15;
        String retreatLocation = "Sedona, Arizona";
        
        // Step 1: Search for spa and wellness hotels in Sedona
        booking_com booking = new booking_com(context);
        booking_com.HotelSearchResult hotelResult = booking.search_hotel(retreatLocation, retreatDate, checkoutDate);
        
        JsonObject accommodationInfo = new JsonObject();
        accommodationInfo.addProperty("destination", hotelResult.destination);
        accommodationInfo.addProperty("checkin_date", hotelResult.checkinDate.toString());
        accommodationInfo.addProperty("checkout_date", hotelResult.checkoutDate.toString());
        accommodationInfo.addProperty("retreat_participants", totalParticipants);
        accommodationInfo.addProperty("accommodation_type", "Spa and wellness hotels");
        
        JsonArray hotelArray = new JsonArray();
        double averageRoomCost = 0.0;
        int validHotels = 0;
        
        for (booking_com.HotelInfo hotel : hotelResult.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotel_name", hotel.hotelName);
            
            // Filter for spa/wellness keywords
            String hotelName = hotel.hotelName.toLowerCase();
            boolean isWellnessHotel = hotelName.contains("spa") || hotelName.contains("wellness") || 
                                    hotelName.contains("resort") || hotelName.contains("retreat");
            
            if (hotel.price != null) {
                hotelObj.addProperty("price_per_night", hotel.price.amount);
                hotelObj.addProperty("currency", hotel.price.currency);
                hotelObj.addProperty("wellness_focused", isWellnessHotel);
                
                if (isWellnessHotel) {
                    averageRoomCost += hotel.price.amount;
                    validHotels++;
                }
            } else {
                hotelObj.addProperty("price_per_night", "Price not available");
                hotelObj.addProperty("wellness_focused", isWellnessHotel);
            }
            hotelArray.add(hotelObj);
        }
        
        if (validHotels > 0) {
            averageRoomCost = averageRoomCost / validHotels;
        } else {
            averageRoomCost = 250.0; // Estimated fallback for wellness hotels in Sedona
        }
        
        // Estimate rooms needed (2 participants per room for retreat setting)
        int roomsNeeded = (totalParticipants + 1) / 2;
        double totalAccommodationCost = averageRoomCost * roomsNeeded * 2; // 2 nights
        
        accommodationInfo.add("wellness_hotels", hotelArray);
        accommodationInfo.addProperty("estimated_average_cost_per_room_per_night", averageRoomCost);
        accommodationInfo.addProperty("rooms_needed", roomsNeeded);
        accommodationInfo.addProperty("total_nights", 2);
        accommodationInfo.addProperty("total_accommodation_cost", totalAccommodationCost);
        result.add("accommodation_information", accommodationInfo);
        
        // Step 2: Search for yoga and meditation supplies at Costco
        costco_com costco = new costco_com(context);
        String[] wellnessSupplies = {"yoga mat", "meditation cushion", "essential oils", "wellness tea"};
        
        JsonObject wellnessKitInfo = new JsonObject();
        JsonArray suppliesArray = new JsonArray();
        double totalSupplyCost = 0.0;
        
        for (String supply : wellnessSupplies) {
            costco_com.ProductInfo productResult = costco.searchProduct(supply);
            JsonObject supplyObj = new JsonObject();
            supplyObj.addProperty("item_type", supply);
            
            if (productResult.error != null) {
                supplyObj.addProperty("error", productResult.error);
                supplyObj.addProperty("estimated_cost_per_item", getEstimatedCost(supply));
                totalSupplyCost += getEstimatedCost(supply);
            } else {
                supplyObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    supplyObj.addProperty("cost_per_item", productResult.productPrice.amount);
                    supplyObj.addProperty("currency", productResult.productPrice.currency);
                    totalSupplyCost += productResult.productPrice.amount;
                } else {
                    double estimatedCost = getEstimatedCost(supply);
                    supplyObj.addProperty("estimated_cost_per_item", estimatedCost);
                    totalSupplyCost += estimatedCost;
                }
            }
            suppliesArray.add(supplyObj);
        }
        
        double wellnessKitCostPerParticipant = totalSupplyCost;
        double totalWellnessKitCost = wellnessKitCostPerParticipant * totalParticipants;
        
        wellnessKitInfo.add("wellness_supplies", suppliesArray);
        wellnessKitInfo.addProperty("kit_cost_per_participant", wellnessKitCostPerParticipant);
        wellnessKitInfo.addProperty("total_participants", totalParticipants);
        wellnessKitInfo.addProperty("total_wellness_kit_cost", totalWellnessKitCost);
        result.add("wellness_kit_information", wellnessKitInfo);
        
        // Step 3: Calculate retreat pricing for 15 participants
        double accommodationCostPerParticipant = totalAccommodationCost / totalParticipants;
        double totalRetreatCostPerParticipant = accommodationCostPerParticipant + wellnessKitCostPerParticipant + 200.0; // Add instruction/facility fees
        double totalRetreatRevenue = totalRetreatCostPerParticipant * totalParticipants;
        
        JsonObject pricingInfo = new JsonObject();
        pricingInfo.addProperty("total_participants", totalParticipants);
        pricingInfo.addProperty("accommodation_cost_per_participant", accommodationCostPerParticipant);
        pricingInfo.addProperty("wellness_kit_cost_per_participant", wellnessKitCostPerParticipant);
        pricingInfo.addProperty("instruction_and_facility_fee_per_participant", 200.0);
        pricingInfo.addProperty("total_cost_per_participant", totalRetreatCostPerParticipant);
        pricingInfo.addProperty("suggested_retreat_price", Math.ceil(totalRetreatCostPerParticipant * 1.3)); // 30% markup
        pricingInfo.addProperty("total_retreat_revenue", totalRetreatRevenue);
        result.add("retreat_pricing", pricingInfo);
        
        // Step 4: Find hiking trails and wellness centers near Sedona
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "Sedona, Arizona";
        String businessDescription = "hiking trails wellness centers meditation";
        int maxLocations = 10;
        
        maps_google_com.NearestBusinessesResult outdoorResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxLocations);
        
        JsonObject outdoorActivitiesInfo = new JsonObject();
        outdoorActivitiesInfo.addProperty("reference_point", outdoorResult.referencePoint);
        outdoorActivitiesInfo.addProperty("search_type", outdoorResult.businessDescription);
        outdoorActivitiesInfo.addProperty("purpose", "Outdoor meditation and nature therapy sessions");
        
        JsonArray locationsArray = new JsonArray();
        for (maps_google_com.BusinessInfo location : outdoorResult.businesses) {
            JsonObject locationObj = new JsonObject();
            locationObj.addProperty("name", location.name);
            locationObj.addProperty("address", location.address);
            
            // Categorize location type based on name
            String locationName = location.name.toLowerCase();
            String locationType = "other";
            if (locationName.contains("trail") || locationName.contains("hike") || locationName.contains("canyon")) {
                locationType = "hiking_trail";
            } else if (locationName.contains("spa") || locationName.contains("wellness") || locationName.contains("meditation")) {
                locationType = "wellness_center";
            } else if (locationName.contains("park") || locationName.contains("rock") || locationName.contains("vortex")) {
                locationType = "natural_attraction";
            }
            
            locationObj.addProperty("location_type", locationType);
            locationsArray.add(locationObj);
        }
        outdoorActivitiesInfo.add("outdoor_locations", locationsArray);
        outdoorActivitiesInfo.addProperty("total_locations_found", locationsArray.size());
        result.add("outdoor_activities", outdoorActivitiesInfo);
        
        // Step 5: Search for meditation and mindfulness books in OpenLibrary
        OpenLibrary openLibrary = new OpenLibrary();
        JsonObject readingListInfo = new JsonObject();
        
        try {
            String[] bookTopics = {"meditation", "mindfulness", "wellness", "spiritual healing"};
            JsonArray booksArray = new JsonArray();
            
            for (String topic : bookTopics) {
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
            
            readingListInfo.addProperty("purpose", "Curated reading list for continued wellness journey");
            readingListInfo.add("reading_categories", booksArray);
            
            // Get additional mindfulness subjects
            List<OpenLibrary.SubjectInfo> mindfulnessSubjects = openLibrary.getSubject("mindfulness", false, 5, 0);
            JsonArray subjectsArray = new JsonArray();
            for (OpenLibrary.SubjectInfo subject : mindfulnessSubjects) {
                subjectsArray.add(subject.info);
            }
            readingListInfo.add("related_subjects", subjectsArray);
            
        } catch (IOException | InterruptedException e) {
            readingListInfo.addProperty("error", "Failed to fetch reading materials: " + e.getMessage());
            readingListInfo.addProperty("recommendation", "Use backup wellness book list");
        }
        
        result.add("wellness_reading_list", readingListInfo);
        
        // Wellness retreat summary and recommendations
        JsonObject retreatSummary = new JsonObject();
        retreatSummary.addProperty("retreat_type", "Wellness Retreat");
        retreatSummary.addProperty("location", retreatLocation);
        retreatSummary.addProperty("dates", retreatDate.toString() + " to " + checkoutDate.toString());
        retreatSummary.addProperty("duration_days", 3);
        retreatSummary.addProperty("participants", totalParticipants);
        retreatSummary.addProperty("cost_per_participant", totalRetreatCostPerParticipant);
        retreatSummary.addProperty("suggested_price_per_participant", Math.ceil(totalRetreatCostPerParticipant * 1.3));
        retreatSummary.addProperty("outdoor_locations_identified", locationsArray.size());
        
        // Retreat recommendations
        StringBuilder recommendations = new StringBuilder();
        recommendations.append("Sedona's natural vortex energy makes it ideal for wellness retreats. ");
        
        if (locationsArray.size() >= 8) {
            recommendations.append("Excellent variety of outdoor locations for meditation and nature therapy. ");
        } else {
            recommendations.append("Limited outdoor options found - scout additional hiking trails and vortex sites. ");
        }
        
        if (totalRetreatCostPerParticipant < 400) {
            recommendations.append("Competitive pricing allows for premium experience additions. ");
        } else {
            recommendations.append("High cost per participant - consider group discounts or package deals. ");
        }
        
        recommendations.append("Include personalized wellness kits and curated reading materials for lasting impact. ");
        recommendations.append("Schedule sessions at Sedona's famous vortex sites for enhanced spiritual experience.");
        
        retreatSummary.addProperty("planning_recommendations", recommendations.toString());
        
        // Wellness program structure
        JsonObject programStructure = new JsonObject();
        programStructure.addProperty("day_1_focus", "Arrival and grounding - hotel check-in, welcome meditation");
        programStructure.addProperty("day_2_focus", "Active wellness - hiking meditation, vortex visits, yoga sessions");
        programStructure.addProperty("day_3_focus", "Integration and departure - final meditation, kit distribution, reading list sharing");
        programStructure.addProperty("daily_schedule", "Morning meditation, nature activity, afternoon wellness session, evening reflection");
        
        JsonArray kitContents = new JsonArray();
        for (String supply : wellnessSupplies) {
            kitContents.add(supply);
        }
        programStructure.add("personalized_wellness_kit_contents", kitContents);
        programStructure.addProperty("reading_list_purpose", "Continue wellness journey at home");
        
        retreatSummary.add("program_structure", programStructure);
        
        // Business viability assessment
        JsonObject viabilityAssessment = new JsonObject();
        double profitMargin = (Math.ceil(totalRetreatCostPerParticipant * 1.3) - totalRetreatCostPerParticipant) / totalRetreatCostPerParticipant * 100;
        viabilityAssessment.addProperty("profit_margin_percentage", Math.round(profitMargin));
        viabilityAssessment.addProperty("break_even_participants", Math.max(1, (int)Math.ceil(totalRetreatCostPerParticipant * totalParticipants / (totalRetreatCostPerParticipant * 1.1))));
        viabilityAssessment.addProperty("location_advantages", "Sedona's spiritual reputation, natural beauty, established wellness tourism");
        viabilityAssessment.addProperty("scalability", "Can accommodate 10-25 participants with venue adjustments");
        retreatSummary.add("business_viability", viabilityAssessment);
        
        result.add("wellness_retreat_summary", retreatSummary);
        
        return result;
    }
    
    // Helper method to estimate costs for wellness supplies when Costco search fails
    private static double getEstimatedCost(String supply) {
        switch (supply.toLowerCase()) {
            case "yoga mat":
                return 25.0;
            case "meditation cushion":
                return 35.0;
            case "essential oils":
                return 15.0;
            case "wellness tea":
                return 20.0;
            default:
                return 20.0;
        }
    }
}
