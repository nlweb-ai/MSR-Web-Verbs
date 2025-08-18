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


public class Task0094 {
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
        
        // Trip details
        LocalDate tripDate = LocalDate.of(2025, 8, 26);
        LocalDate returnDate = LocalDate.of(2025, 8, 27);
        int totalStudents = 30;
        int totalTeachers = 3;
        int totalTravelers = totalStudents + totalTeachers;
        
        // Step 1: Search for flights from Boston to Washington D.C.
        alaskaair_com alaskaAir = new alaskaair_com(context);
        alaskaair_com.SearchFlightsResult flightResult = alaskaAir.searchFlights("BOS", "DCA", tripDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        flightInfo.addProperty("origin", "Boston (BOS)");
        flightInfo.addProperty("destination", "Washington D.C. (DCA)");
        flightInfo.addProperty("outbound_date", tripDate.toString());
        flightInfo.addProperty("return_date", returnDate.toString());
        flightInfo.addProperty("total_travelers", totalTravelers);
        
        if (flightResult.message != null) {
            flightInfo.addProperty("status", "No flights found");
            flightInfo.addProperty("message", flightResult.message);
            flightInfo.addProperty("estimated_cost_per_person", 0.0);
            flightInfo.addProperty("total_flight_cost", 0.0);
        } else if (flightResult.flightInfo != null && flightResult.flightInfo.price != null) {
            double costPerPerson = flightResult.flightInfo.price.amount;
            double totalFlightCost = costPerPerson * totalTravelers;
            
            flightInfo.addProperty("status", "Flights available");
            flightInfo.addProperty("cost_per_person", costPerPerson);
            flightInfo.addProperty("currency", flightResult.flightInfo.price.currency);
            flightInfo.addProperty("total_flight_cost", totalFlightCost);
            
            JsonArray flightsArray = new JsonArray();
            for (String flight : flightResult.flightInfo.flights) {
                flightsArray.add(flight);
            }
            flightInfo.add("available_flights", flightsArray);
        } else {
            flightInfo.addProperty("status", "Flight information incomplete");
            flightInfo.addProperty("estimated_cost_per_person", 300.0); // Estimated fallback
            flightInfo.addProperty("total_flight_cost", 300.0 * totalTravelers);
        }
        result.add("flight_information", flightInfo);
        
        // Step 2: Search for group accommodations in Washington D.C.
        booking_com booking = new booking_com(context);
        booking_com.HotelSearchResult hotelResult = booking.search_hotel("Washington D.C.", tripDate, returnDate);
        
        JsonObject accommodationInfo = new JsonObject();
        accommodationInfo.addProperty("destination", hotelResult.destination);
        accommodationInfo.addProperty("checkin_date", hotelResult.checkinDate.toString());
        accommodationInfo.addProperty("checkout_date", hotelResult.checkoutDate.toString());
        accommodationInfo.addProperty("group_size", totalTravelers);
        accommodationInfo.addProperty("accommodation_type", "Group accommodations/hostels");
        
        JsonArray hotelsArray = new JsonArray();
        double averageHotelCost = 0.0;
        int validHotels = 0;
        
        for (booking_com.HotelInfo hotel : hotelResult.hotels) {
            JsonObject hotelObj = new JsonObject();
            hotelObj.addProperty("hotel_name", hotel.hotelName);
            
            if (hotel.price != null) {
                hotelObj.addProperty("price_per_night", hotel.price.amount);
                hotelObj.addProperty("currency", hotel.price.currency);
                averageHotelCost += hotel.price.amount;
                validHotels++;
            } else {
                hotelObj.addProperty("price_per_night", "Price not available");
            }
            hotelsArray.add(hotelObj);
        }
        
        if (validHotels > 0) {
            averageHotelCost = averageHotelCost / validHotels;
        } else {
            averageHotelCost = 120.0; // Estimated fallback for group accommodation
        }
        
        // Estimate rooms needed (4 people per room for students, 1 room per teacher)
        int studentRooms = (totalStudents + 3) / 4; // Round up
        int teacherRooms = totalTeachers;
        int totalRooms = studentRooms + teacherRooms;
        double totalHotelCost = averageHotelCost * totalRooms;
        
        accommodationInfo.add("available_hotels", hotelsArray);
        accommodationInfo.addProperty("estimated_average_cost_per_room", averageHotelCost);
        accommodationInfo.addProperty("estimated_rooms_needed", totalRooms);
        accommodationInfo.addProperty("total_accommodation_cost", totalHotelCost);
        result.add("accommodation_information", accommodationInfo);
        
        // Step 3: Calculate total cost per student
        double totalFlightCost = flightInfo.has("total_flight_cost") ? flightInfo.get("total_flight_cost").getAsDouble() : 0.0;
        double totalTripCost = totalFlightCost + totalHotelCost;
        double costPerStudent = totalTripCost / totalStudents; // Only students pay, teachers might be covered
        
        JsonObject costBreakdown = new JsonObject();
        costBreakdown.addProperty("total_travelers", totalTravelers);
        costBreakdown.addProperty("students", totalStudents);
        costBreakdown.addProperty("teachers", totalTeachers);
        costBreakdown.addProperty("total_flight_cost", totalFlightCost);
        costBreakdown.addProperty("total_accommodation_cost", totalHotelCost);
        costBreakdown.addProperty("total_trip_cost", totalTripCost);
        costBreakdown.addProperty("cost_per_student", costPerStudent);
        result.add("cost_breakdown", costBreakdown);
        
        // Step 4: Find museums and educational attractions near National Mall
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "National Mall, Washington D.C.";
        String businessDescription = "museums educational attractions";
        int maxAttractions = 8;
        
        maps_google_com.NearestBusinessesResult attractionsResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxAttractions);
        
        JsonObject itineraryInfo = new JsonObject();
        itineraryInfo.addProperty("reference_point", attractionsResult.referencePoint);
        itineraryInfo.addProperty("search_type", attractionsResult.businessDescription);
        itineraryInfo.addProperty("purpose", "Educational field trip itinerary");
        
        JsonArray attractionsArray = new JsonArray();
        for (maps_google_com.BusinessInfo attraction : attractionsResult.businesses) {
            JsonObject attractionObj = new JsonObject();
            attractionObj.addProperty("name", attraction.name);
            attractionObj.addProperty("address", attraction.address);
            attractionsArray.add(attractionObj);
        }
        itineraryInfo.add("educational_attractions", attractionsArray);
        itineraryInfo.addProperty("total_attractions_found", attractionsArray.size());
        result.add("educational_itinerary", itineraryInfo);
        
        // Step 5: Get NASA Near Earth Objects data for educational content
        Nasa nasa = new Nasa();
        JsonObject nasaInfo = new JsonObject();
        
        try {
            // Get NEO data for the trip dates to make it relevant
            List<Nasa.NeoResult> neoResults = nasa.getNeoFeed(tripDate.toString(), returnDate.toString());
            
            nasaInfo.addProperty("purpose", "Space science educational content for museum visits");
            nasaInfo.addProperty("data_period", tripDate.toString() + " to " + returnDate.toString());
            
            JsonArray neoArray = new JsonArray();
            for (Nasa.NeoResult neo : neoResults) {
                JsonObject neoObj = new JsonObject();
                neoObj.addProperty("name", neo.name);
                neoObj.addProperty("id", neo.id);
                neoObj.addProperty("close_approach_date", neo.closeApproachDate != null ? neo.closeApproachDate.toString() : "Unknown");
                neoObj.addProperty("estimated_diameter_km", neo.estimatedDiameterKm != null ? neo.estimatedDiameterKm : 0.0);
                
                if (neo.missDistance != null) {
                    neoObj.addProperty("miss_distance", neo.missDistance.amount);
                    neoObj.addProperty("distance_unit", neo.missDistance.currency); // Using currency field for unit
                }
                
                neoArray.add(neoObj);
            }
            nasaInfo.add("near_earth_objects", neoArray);
            nasaInfo.addProperty("total_neos_found", neoArray.size());
            
            // Get APOD for educational content
            Nasa.ApodResult apod = nasa.getApod(tripDate.toString(), false);
            if (apod != null) {
                JsonObject apodObj = new JsonObject();
                apodObj.addProperty("title", apod.title);
                apodObj.addProperty("url", apod.url);
                apodObj.addProperty("explanation", apod.explanation);
                apodObj.addProperty("date", apod.date != null ? apod.date.toString() : tripDate.toString());
                nasaInfo.add("astronomy_picture_of_day", apodObj);
            }
            
        } catch (IOException | InterruptedException e) {
            nasaInfo.addProperty("error", "Failed to fetch NASA data: " + e.getMessage());
            nasaInfo.addProperty("educational_content_status", "Use backup space science materials");
        }
        
        result.add("nasa_educational_content", nasaInfo);
        
        // Field trip summary and recommendations
        JsonObject fieldTripSummary = new JsonObject();
        fieldTripSummary.addProperty("trip_type", "Educational Field Trip");
        fieldTripSummary.addProperty("destination", "Washington D.C.");
        fieldTripSummary.addProperty("dates", tripDate.toString() + " to " + returnDate.toString());
        fieldTripSummary.addProperty("group_size", totalTravelers);
        fieldTripSummary.addProperty("students", totalStudents);
        fieldTripSummary.addProperty("estimated_cost_per_student", costPerStudent);
        fieldTripSummary.addProperty("educational_venues_identified", attractionsArray.size());
        
        // Trip recommendations
        StringBuilder recommendations = new StringBuilder();
        recommendations.append("Book flights early for group discounts. ");
        recommendations.append("Contact museums in advance for group rates and guided tours. ");
        
        if (costPerStudent > 500) {
            recommendations.append("Consider fundraising activities to reduce student costs. ");
        }
        
        if (attractionsArray.size() >= 6) {
            recommendations.append("Excellent variety of educational attractions available - plan 2-day itinerary. ");
        } else {
            recommendations.append("Limited attractions found - supplement with additional research. ");
        }
        
        recommendations.append("Incorporate NASA space science data into Air and Space Museum visit for enhanced learning experience.");
        
        fieldTripSummary.addProperty("planning_recommendations", recommendations.toString());
        
        // Educational value assessment
        JsonObject educationalValue = new JsonObject();
        educationalValue.addProperty("primary_focus", "American History and Government");
        educationalValue.addProperty("secondary_focus", "Space Science and Technology");
        educationalValue.addProperty("learning_objectives", "Civic engagement, historical understanding, scientific literacy");
        educationalValue.addProperty("real_time_science_integration", nasaInfo.has("near_earth_objects") ? "Available" : "Limited");
        fieldTripSummary.add("educational_assessment", educationalValue);
        
        result.add("field_trip_summary", fieldTripSummary);
        
        return result;
    }
}
