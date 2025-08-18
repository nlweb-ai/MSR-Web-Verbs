import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0018 {
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
        
        // 1. Search for hotels in Nashville, Tennessee for August 18-21
        booking_com booking = new booking_com(context);
        LocalDate checkinDate = LocalDate.of(2025, 8, 18);
        LocalDate checkoutDate = LocalDate.of(2025, 8, 21);
        
        booking_com.HotelSearchResult hotelResults = booking.search_hotel("Nashville, Tennessee", checkinDate, checkoutDate);
        
        JsonObject accommodationInfo = new JsonObject();
        accommodationInfo.addProperty("destination", hotelResults.destination);
        accommodationInfo.addProperty("checkinDate", hotelResults.checkinDate.toString());
        accommodationInfo.addProperty("checkoutDate", hotelResults.checkoutDate.toString());
        accommodationInfo.addProperty("purpose", "Family reunion accommodation for extended family members");
        accommodationInfo.addProperty("duration", "3 nights");
        
        JsonArray hotelsArray = new JsonArray();
        double totalHotelCost = 0.0;
        double minHotelPrice = Double.MAX_VALUE;
        double maxHotelPrice = 0.0;
        int validHotelPrices = 0;
        
        for (booking_com.HotelInfo hotel : hotelResults.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotelName", hotel.hotelName);
            
            if (hotel.price != null) {
                hotelObj.addProperty("pricePerNight", hotel.price.amount);
                hotelObj.addProperty("currency", hotel.price.currency);
                
                // Categorize hotels for family reunion needs
                String familySuitability = categorizeFamilyHotel(hotel.price.amount, hotel.hotelName);
                hotelObj.addProperty("familySuitability", familySuitability);
                
                // Group assignment based on budget
                String budgetGroup;
                if (hotel.price.amount <= 120) {
                    budgetGroup = "Budget Group - Extended family members with cost constraints";
                } else if (hotel.price.amount <= 200) {
                    budgetGroup = "Standard Group - Most family members comfortable with moderate pricing";
                } else {
                    budgetGroup = "Premium Group - Family members preferring luxury accommodations";
                }
                hotelObj.addProperty("recommendedFor", budgetGroup);
                
                totalHotelCost += hotel.price.amount;
                validHotelPrices++;
                minHotelPrice = Math.min(minHotelPrice, hotel.price.amount);
                maxHotelPrice = Math.max(maxHotelPrice, hotel.price.amount);
            } else {
                hotelObj.addProperty("pricePerNight", (String) null);
                hotelObj.addProperty("currency", (String) null);
                hotelObj.addProperty("familySuitability", "Pricing information not available");
            }
            
            hotelsArray.add(hotelObj);
        }
        
        accommodationInfo.add("hotels", hotelsArray);
        
        // Family accommodation analysis
        JsonObject familyAccommodationAnalysis = new JsonObject();
        familyAccommodationAnalysis.addProperty("totalHotelsFound", hotelResults.hotels.size());
        if (validHotelPrices > 0) {
            double avgPrice = totalHotelCost / validHotelPrices;
            familyAccommodationAnalysis.addProperty("averagePricePerNight", Math.round(avgPrice * 100.0) / 100.0);
            familyAccommodationAnalysis.addProperty("budgetRangeMin", Math.round(minHotelPrice * 100.0) / 100.0);
            familyAccommodationAnalysis.addProperty("budgetRangeMax", Math.round(maxHotelPrice * 100.0) / 100.0);
            familyAccommodationAnalysis.addProperty("total3NightCost", Math.round(avgPrice * 3 * 100.0) / 100.0);
            
            // Family group recommendations
            JsonObject groupRecommendations = new JsonObject();
            int budgetCount = 0, standardCount = 0, premiumCount = 0;
            for (booking_com.HotelInfo hotel : hotelResults.hotels) {
                if (hotel.price != null) {
                    if (hotel.price.amount <= 120) budgetCount++;
                    else if (hotel.price.amount <= 200) standardCount++;
                    else premiumCount++;
                }
            }
            
            groupRecommendations.addProperty("budgetGroupOptions", budgetCount);
            groupRecommendations.addProperty("standardGroupOptions", standardCount);
            groupRecommendations.addProperty("premiumGroupOptions", premiumCount);
            groupRecommendations.addProperty("recommendedStrategy", "Book multiple room blocks to accommodate different budget preferences");
            
            familyAccommodationAnalysis.add("familyGrouping", groupRecommendations);
        }
        
        accommodationInfo.add("accommodationAnalysis", familyAccommodationAnalysis);
        result.add("familyAccommodation", accommodationInfo);
        
        // 2. Get directions from Nashville International Airport to downtown Nashville
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.DirectionResult directions = maps.get_direction("Nashville International Airport", "downtown Nashville");
        
        JsonObject travelDirectionsInfo = new JsonObject();
        travelDirectionsInfo.addProperty("origin", "Nashville International Airport (BNA)");
        travelDirectionsInfo.addProperty("destination", "Downtown Nashville");
        travelDirectionsInfo.addProperty("purpose", "Travel instructions for flying family members");
        travelDirectionsInfo.addProperty("travelTime", directions.travelTime);
        travelDirectionsInfo.addProperty("distance", directions.distance);
        travelDirectionsInfo.addProperty("route", directions.route);
        
        // Family travel recommendations
        JsonObject familyTravelTips = new JsonObject();
        familyTravelTips.addProperty("airportPickup", "Coordinate pickup schedules based on arrival times from different states");
        familyTravelTips.addProperty("rentalCars", "Consider group rental discounts for families driving from airport");
        familyTravelTips.addProperty("rideshare", "Uber/Lyft available but coordinate rides for elderly family members");
        familyTravelTips.addProperty("publicTransport", "Nashville WeGo bus system connects airport to downtown area");
        familyTravelTips.addProperty("timing", "Allow extra time for elderly relatives and families with young children");
        
        JsonArray arrivalCoordination = new JsonArray();
        arrivalCoordination.add("Create shared spreadsheet with flight arrival times");
        arrivalCoordination.add("Assign pickup volunteers for each arrival window");
        arrivalCoordination.add("Share contact information for all family members");
        arrivalCoordination.add("Prepare welcome packets with hotel information and reunion schedule");
        
        familyTravelTips.add("coordinationTips", arrivalCoordination);
        travelDirectionsInfo.add("familyTravelRecommendations", familyTravelTips);
        
        result.add("travelDirections", travelDirectionsInfo);
        
        // 3. Search for party supplies and decorations at Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult partySuppliesResults = costco.searchProducts("party supplies");
        
        JsonObject partyPlanningInfo = new JsonObject();
        partyPlanningInfo.addProperty("searchTerm", "party supplies");
        partyPlanningInfo.addProperty("purpose", "Family reunion celebration planning and bulk purchase savings");
        
        if (partySuppliesResults.error != null) {
            partyPlanningInfo.addProperty("error", partySuppliesResults.error);
        }
        
        JsonArray partySuppliesArray = new JsonArray();
        double totalPartySuppliesCost = 0.0;
        
        for (costco_com.ProductInfo product : partySuppliesResults.products) {
            JsonObject productObj = new JsonObject();
            productObj.addProperty("productName", product.productName);
            
            if (product.productPrice != null) {
                productObj.addProperty("priceAmount", product.productPrice.amount);
                productObj.addProperty("priceCurrency", product.productPrice.currency);
                
                // Calculate bulk savings for family reunion
                String bulkValue = assessBulkValue(product.productName, product.productPrice.amount);
                productObj.addProperty("bulkSavingsAssessment", bulkValue);
                
                // Reunion suitability
                String reunionSuitability = assessReunionSuitability(product.productName);
                productObj.addProperty("reunionSuitability", reunionSuitability);
                
                totalPartySuppliesCost += product.productPrice.amount;
            }
            
            if (product.error != null) {
                productObj.addProperty("error", product.error);
            }
            
            partySuppliesArray.add(productObj);
        }
        
        partyPlanningInfo.add("partySupplies", partySuppliesArray);
        
        // Bulk purchase analysis
        JsonObject bulkPurchaseAnalysis = new JsonObject();
        bulkPurchaseAnalysis.addProperty("totalEstimatedCost", Math.round(totalPartySuppliesCost * 100.0) / 100.0);
        bulkPurchaseAnalysis.addProperty("costcoAdvantage", "Bulk quantities perfect for large family gatherings");
        bulkPurchaseAnalysis.addProperty("estimatedSavings", "20-40% savings compared to regular retail stores");
        
        JsonArray partyPlanningTips = new JsonArray();
        partyPlanningTips.add("Focus on non-perishable decorations that can be stored");
        partyPlanningTips.add("Buy paper products and disposables in bulk for easy cleanup");
        partyPlanningTips.add("Consider themed decorations that celebrate family history");
        partyPlanningTips.add("Purchase extra supplies for unexpected family members");
        
        bulkPurchaseAnalysis.add("planningRecommendations", partyPlanningTips);
        partyPlanningInfo.add("bulkPurchaseAnalysis", bulkPurchaseAnalysis);
        
        result.add("partyPlanning", partyPlanningInfo);
        
        // 4. Find museums and entertainment venues near downtown Nashville
        maps_google_com.NearestBusinessesResult museums = maps.get_nearestBusinesses(
            "downtown Nashville, Tennessee", "museum", 10);
        
        maps_google_com.NearestBusinessesResult entertainment = maps.get_nearestBusinesses(
            "downtown Nashville, Tennessee", "entertainment venue", 10);
        
        JsonObject familyActivitiesInfo = new JsonObject();
        familyActivitiesInfo.addProperty("searchArea", "downtown Nashville, Tennessee");
        familyActivitiesInfo.addProperty("purpose", "Family-friendly activities for all ages during reunion");
        
        JsonArray museumsArray = new JsonArray();
        for (maps_google_com.BusinessInfo museum : museums.businesses) {
            JsonObject museumObj = new JsonObject();
            museumObj.addProperty("name", museum.name);
            museumObj.addProperty("address", museum.address);
            
            String familyAppeal = assessFamilyAppeal(museum.name, "museum");
            museumObj.addProperty("familyAppeal", familyAppeal);
            
            String ageAppropriate = determineAgeAppropriateness(museum.name);
            museumObj.addProperty("ageAppropriateness", ageAppropriate);
            
            museumsArray.add(museumObj);
        }
        
        JsonArray entertainmentArray = new JsonArray();
        for (maps_google_com.BusinessInfo venue : entertainment.businesses) {
            JsonObject venueObj = new JsonObject();
            venueObj.addProperty("name", venue.name);
            venueObj.addProperty("address", venue.address);
            
            String familyAppeal = assessFamilyAppeal(venue.name, "entertainment");
            venueObj.addProperty("familyAppeal", familyAppeal);
            
            String ageAppropriate = determineAgeAppropriateness(venue.name);
            venueObj.addProperty("ageAppropriateness", ageAppropriate);
            
            entertainmentArray.add(venueObj);
        }
        
        familyActivitiesInfo.add("museums", museumsArray);
        familyActivitiesInfo.add("entertainmentVenues", entertainmentArray);
        
        // Activity planning recommendations
        JsonObject activityPlanning = new JsonObject();
        activityPlanning.addProperty("totalMuseums", museums.businesses.size());
        activityPlanning.addProperty("totalEntertainmentVenues", entertainment.businesses.size());
        
        JsonArray itineraryTips = new JsonArray();
        itineraryTips.add("Plan activities for different age groups - kids, teens, adults, seniors");
        itineraryTips.add("Include Nashville's music heritage in the itinerary");
        itineraryTips.add("Schedule both indoor and outdoor activities for weather flexibility");
        itineraryTips.add("Allow free time for family members to explore individual interests");
        itineraryTips.add("Consider group discounts for large family parties");
        
        JsonObject nashvilleHighlights = new JsonObject();
        nashvilleHighlights.addProperty("musicScene", "Country Music Hall of Fame and live music venues");
        nashvilleHighlights.addProperty("familyFriendly", "Adventure Science Center and Nashville Zoo");
        nashvilleHighlights.addProperty("cultural", "Tennessee State Museum and historic sites");
        nashvilleHighlights.addProperty("outdoor", "Centennial Park and riverfront activities");
        
        activityPlanning.add("itineraryRecommendations", itineraryTips);
        activityPlanning.add("nashvilleHighlights", nashvilleHighlights);
        
        familyActivitiesInfo.add("activityPlanning", activityPlanning);
        result.add("familyActivities", familyActivitiesInfo);
        
        // 5. Family reunion planning summary
        JsonObject reunionSummary = new JsonObject();
        reunionSummary.addProperty("event", "Family Reunion - Nashville, Tennessee");
        reunionSummary.addProperty("dates", "August 18-21, 2025 (3 nights)");
        reunionSummary.addProperty("focus", "Multi-generational family gathering with diverse activities");
        
        // Budget estimation for family reunion
        if (validHotelPrices > 0) {
            double avgHotelCost = totalHotelCost / validHotelPrices;
            JsonObject budgetEstimate = new JsonObject();
            budgetEstimate.addProperty("accommodationPerRoom3Nights", Math.round(avgHotelCost * 3 * 100.0) / 100.0);
            budgetEstimate.addProperty("partySuppliesTotal", Math.round(totalPartySuppliesCost * 100.0) / 100.0);
            budgetEstimate.addProperty("estimatedActivitiesCost", 500.0); // Estimated for group activities
            budgetEstimate.addProperty("totalEstimatedCost", Math.round((avgHotelCost * 3 + totalPartySuppliesCost + 500) * 100.0) / 100.0);
            budgetEstimate.addProperty("note", "Costs per family unit - multiply by number of rooms needed");
            
            reunionSummary.add("budgetEstimate", budgetEstimate);
        }
        
        JsonArray organizationChecklist = new JsonArray();
        organizationChecklist.add("Create shared document with hotel options by budget level");
        organizationChecklist.add("Coordinate airport pickup schedules and volunteers");
        organizationChecklist.add("Purchase party supplies and decorations in bulk from Costco");
        organizationChecklist.add("Plan diverse activities for all family age groups");
        organizationChecklist.add("Arrange group discounts for museums and attractions");
        organizationChecklist.add("Prepare welcome packets with schedules and contact information");
        organizationChecklist.add("Set up family photo session at Nashville landmarks");
        
        reunionSummary.add("organizationSteps", organizationChecklist);
        
        JsonArray specialConsiderations = new JsonArray();
        specialConsiderations.add("Accommodate elderly family members with mobility considerations");
        specialConsiderations.add("Plan child-friendly activities and supervision options");
        specialConsiderations.add("Consider dietary restrictions for group meals");
        specialConsiderations.add("Prepare backup indoor activities for weather contingencies");
        
        reunionSummary.add("specialConsiderations", specialConsiderations);
        result.add("familyReunionSummary", reunionSummary);
        
        return result;
    }
    
    // Helper method to categorize hotels for family reunion suitability
    private static String categorizeFamilyHotel(double price, String hotelName) {
        String nameLower = hotelName.toLowerCase();
        
        if (nameLower.contains("suite") || nameLower.contains("extended")) {
            return "Excellent for families - Spacious suites with kitchenettes for large groups";
        } else if (nameLower.contains("hampton") || nameLower.contains("holiday") || nameLower.contains("hilton")) {
            return "Family-friendly chain - Reliable amenities and group booking options";
        } else if (price >= 200) {
            return "Premium family option - Luxury amenities suitable for special occasions";
        } else if (price <= 120) {
            return "Budget-friendly family choice - Basic amenities, good for cost-conscious relatives";
        } else {
            return "Standard family accommodation - Good balance of price and amenities";
        }
    }
    
    // Helper method to assess bulk value for party supplies
    private static String assessBulkValue(String productName, double price) {
        String nameLower = productName.toLowerCase();
        
        if (nameLower.contains("decoration") || nameLower.contains("banner")) {
            if (price > 50) {
                return "High bulk value - Premium decorations perfect for large family gatherings";
            }
            return "High bulk value - Perfect for large family gatherings, significant cost savings";
        } else if (nameLower.contains("plate") || nameLower.contains("cup") || nameLower.contains("napkin")) {
            return "Excellent bulk purchase - Disposable items needed in large quantities";
        } else if (nameLower.contains("balloon") || nameLower.contains("streamer")) {
            return "Good bulk value - Festive decorations for celebration atmosphere";
        } else {
            return "Standard bulk savings - Compare with regular retail prices";
        }
    }
    
    // Helper method to assess reunion suitability
    private static String assessReunionSuitability(String productName) {
        String nameLower = productName.toLowerCase();
        
        if (nameLower.contains("photo") || nameLower.contains("frame")) {
            return "Perfect for reunion - Memory-making and keepsake opportunities";
        } else if (nameLower.contains("table") || nameLower.contains("chair")) {
            return "Essential for large gatherings - Accommodate extended family seating";
        } else if (nameLower.contains("game") || nameLower.contains("activity")) {
            return "Great for family bonding - Multi-generational entertainment options";
        } else {
            return "General party use - Suitable for celebration atmosphere";
        }
    }
    
    // Helper method to assess family appeal of venues
    private static String assessFamilyAppeal(String venueName, String venueType) {
        String nameLower = venueName.toLowerCase();
        
        if (venueType.equals("museum")) {
            if (nameLower.contains("music") || nameLower.contains("country")) {
                return "High family appeal - Nashville's signature music heritage attracts all ages";
            } else if (nameLower.contains("science") || nameLower.contains("children")) {
                return "Excellent for families - Interactive exhibits engage kids and adults";
            } else if (nameLower.contains("history") || nameLower.contains("civil")) {
                return "Educational family value - Historical significance for all generations";
            }
        } else if (venueType.equals("entertainment")) {
            if (nameLower.contains("theater") || nameLower.contains("show")) {
                return "Family entertainment - Live performances create shared memories";
            } else if (nameLower.contains("park") || nameLower.contains("outdoor")) {
                return "Active family fun - Outdoor activities for various fitness levels";
            }
        }
        
        return "General family interest - Research specific offerings for age appropriateness";
    }
    
    // Helper method to determine age appropriateness
    private static String determineAgeAppropriateness(String venueName) {
        String nameLower = venueName.toLowerCase();
        
        if (nameLower.contains("children") || nameLower.contains("kid") || nameLower.contains("adventure")) {
            return "Great for children and teens - Interactive and engaging for younger family members";
        } else if (nameLower.contains("music") || nameLower.contains("hall of fame")) {
            return "All ages - Music appeals to multiple generations in family";
        } else if (nameLower.contains("history") || nameLower.contains("heritage")) {
            return "Best for teens and adults - Educational content more engaging for older family members";
        } else {
            return "Mixed age appeal - Check specific programs and accessibility for all family members";
        }
    }
}
