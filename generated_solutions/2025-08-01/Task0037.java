import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0037 {
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
            // Step 1: Search for flights from Atlanta to Miami for August 23-25, 2025
            alaskaair_com alaskaAir = new alaskaair_com(context);
            JsonObject flightSearchResult = new JsonObject();
            
            try {
                LocalDate outboundDate = LocalDate.of(2025, 8, 23);
                LocalDate returnDate = LocalDate.of(2025, 8, 25);
                
                alaskaair_com.SearchFlightsResult flightResult = alaskaAir.searchFlights("ATL", "MIA", outboundDate, returnDate);
                
                if (flightResult != null) {
                    if (flightResult.flightInfo != null && flightResult.flightInfo.flights != null) {
                        JsonArray flightsArray = new JsonArray();
                        
                        for (String flightDetails : flightResult.flightInfo.flights) {
                            JsonObject flightObj = new JsonObject();
                            flightObj.addProperty("flight_details", flightDetails);
                            flightObj.addProperty("route", "Atlanta (ATL) to Miami (MIA)");
                            flightsArray.add(flightObj);
                        }
                        
                        flightSearchResult.add("available_flights", flightsArray);
                        flightSearchResult.addProperty("price", flightResult.flightInfo.price != null ? flightResult.flightInfo.price.amount : 0.0);
                        flightSearchResult.addProperty("currency", flightResult.flightInfo.price != null ? flightResult.flightInfo.price.currency : "USD");
                        flightSearchResult.addProperty("outbound_date", outboundDate.toString());
                        flightSearchResult.addProperty("return_date", returnDate.toString());
                        flightSearchResult.addProperty("search_status", "Found flights");
                    } else if (flightResult.message != null) {
                        flightSearchResult.addProperty("message", flightResult.message);
                        flightSearchResult.addProperty("search_status", "No flights found");
                    }
                } else {
                    flightSearchResult.addProperty("error", "Flight search returned null result");
                }
                
            } catch (Exception e) {
                flightSearchResult.addProperty("error", "Failed to search flights: " + e.getMessage());
            }
            
            output.add("flight_search", flightSearchResult);
            
            // Step 2: Find short-term apartment rentals in Miami within budget
            redfin_com redfin = new redfin_com(context);
            JsonObject rentalSearchResult = new JsonObject();
            
            try {
                // Search for apartments in Miami within a reasonable weekend budget (assuming $150-300/night range)
                redfin_com.ApartmentSearchResult apartmentResult = redfin.searchApartments("Miami, FL", 150, 300);
                
                if (apartmentResult != null) {
                    if (apartmentResult.apartments != null && !apartmentResult.apartments.isEmpty()) {
                        JsonArray apartmentsArray = new JsonArray();
                        
                        for (redfin_com.ApartmentInfo apartment : apartmentResult.apartments) {
                            JsonObject apartmentObj = new JsonObject();
                            apartmentObj.addProperty("address", apartment.address);
                            apartmentObj.addProperty("price", apartment.price != null ? apartment.price.amount : 0.0);
                            apartmentObj.addProperty("currency", apartment.price != null ? apartment.price.currency : "USD");
                            apartmentObj.addProperty("url", apartment.url);
                            apartmentObj.addProperty("rental_type", "Short-term Miami Rental");
                            apartmentsArray.add(apartmentObj);
                        }
                        
                        rentalSearchResult.add("available_rentals", apartmentsArray);
                        rentalSearchResult.addProperty("search_location", "Miami, FL");
                        rentalSearchResult.addProperty("price_range", "$150-300 per night");
                        rentalSearchResult.addProperty("rentals_found", apartmentResult.apartments.size());
                    }
                    
                    if (apartmentResult.error != null) {
                        rentalSearchResult.addProperty("search_error", apartmentResult.error);
                    }
                } else {
                    rentalSearchResult.addProperty("error", "Rental search returned null result");
                }
                
            } catch (Exception e) {
                rentalSearchResult.addProperty("error", "Failed to search rentals: " + e.getMessage());
            }
            
            output.add("rental_search", rentalSearchResult);
            
            // Step 3: Search for beach gear and sunscreen at Costco
            costco_com costco = new costco_com(context);
            JsonArray beachGearArray = new JsonArray();
            
            try {
                // Search for beach gear
                costco_com.ProductListResult beachGear = costco.searchProducts("beach umbrella chair cooler");
                if (beachGear != null && beachGear.products != null) {
                    for (costco_com.ProductInfo product : beachGear.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("name", product.productName);
                        productObj.addProperty("price", product.productPrice != null ? product.productPrice.amount : 0.0);
                        productObj.addProperty("currency", product.productPrice != null ? product.productPrice.currency : "USD");
                        productObj.addProperty("category", "Beach Gear");
                        if (product.error != null) {
                            productObj.addProperty("error", product.error);
                        }
                        beachGearArray.add(productObj);
                    }
                }
                
                // Search for sunscreen
                costco_com.ProductListResult sunscreenProducts = costco.searchProducts("sunscreen SPF beach");
                if (sunscreenProducts != null && sunscreenProducts.products != null) {
                    for (costco_com.ProductInfo product : sunscreenProducts.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("name", product.productName);
                        productObj.addProperty("price", product.productPrice != null ? product.productPrice.amount : 0.0);
                        productObj.addProperty("currency", product.productPrice != null ? product.productPrice.currency : "USD");
                        productObj.addProperty("category", "Sun Protection");
                        if (product.error != null) {
                            productObj.addProperty("error", product.error);
                        }
                        beachGearArray.add(productObj);
                    }
                }
                
            } catch (Exception e) {
                JsonObject gearError = new JsonObject();
                gearError.addProperty("error", "Failed to search beach gear: " + e.getMessage());
                beachGearArray.add(gearError);
            }
            
            output.add("beach_gear", beachGearArray);
            
            // Step 4: Find top 5 tourist attractions near the rental using Google Maps
            maps_google_com maps = new maps_google_com(context);
            JsonObject attractionsResult = new JsonObject();
            
            try {
                // Search for tourist attractions in Miami
                maps_google_com.NearestBusinessesResult touristAttractions = maps.get_nearestBusinesses("Miami, FL", "tourist attraction", 5);
                maps_google_com.NearestBusinessesResult beaches = maps.get_nearestBusinesses("Miami, FL", "beach", 3);
                maps_google_com.NearestBusinessesResult museums = maps.get_nearestBusinesses("Miami, FL", "museum", 3);
                
                JsonArray attractionsArray = new JsonArray();
                
                // Add tourist attractions
                if (touristAttractions != null && touristAttractions.businesses != null) {
                    for (maps_google_com.BusinessInfo attraction : touristAttractions.businesses) {
                        JsonObject attractionObj = new JsonObject();
                        attractionObj.addProperty("name", attraction.name);
                        attractionObj.addProperty("address", attraction.address);
                        attractionObj.addProperty("type", "Tourist Attraction");
                        attractionObj.addProperty("priority", "High");
                        attractionsArray.add(attractionObj);
                    }
                }
                
                // Add beaches
                if (beaches != null && beaches.businesses != null) {
                    for (maps_google_com.BusinessInfo beach : beaches.businesses) {
                        JsonObject beachObj = new JsonObject();
                        beachObj.addProperty("name", beach.name);
                        beachObj.addProperty("address", beach.address);
                        beachObj.addProperty("type", "Beach");
                        beachObj.addProperty("priority", "High");
                        attractionsArray.add(beachObj);
                    }
                }
                
                // Add museums
                if (museums != null && museums.businesses != null) {
                    for (maps_google_com.BusinessInfo museum : museums.businesses) {
                        JsonObject museumObj = new JsonObject();
                        museumObj.addProperty("name", museum.name);
                        museumObj.addProperty("address", museum.address);
                        museumObj.addProperty("type", "Museum");
                        museumObj.addProperty("priority", "Medium");
                        attractionsArray.add(museumObj);
                    }
                }
                
                attractionsResult.add("attractions", attractionsArray);
                attractionsResult.addProperty("total_attractions_found", attractionsArray.size());
                
                // Get directions to top attraction if available
                if (attractionsArray.size() > 0) {
                    JsonObject topAttraction = attractionsArray.get(0).getAsJsonObject();
                    String attractionAddress = topAttraction.get("address").getAsString();
                    
                    maps_google_com.DirectionResult directions = maps.get_direction("Miami, FL", attractionAddress);
                    if (directions != null) {
                        JsonObject directionsObj = new JsonObject();
                        directionsObj.addProperty("destination", topAttraction.get("name").getAsString());
                        directionsObj.addProperty("travel_time", directions.travelTime);
                        directionsObj.addProperty("distance", directions.distance);
                        directionsObj.addProperty("route", directions.route);
                        
                        attractionsResult.add("sample_directions", directionsObj);
                    }
                }
                
            } catch (Exception e) {
                attractionsResult.addProperty("error", "Failed to find tourist attractions: " + e.getMessage());
            }
            
            output.add("tourist_attractions", attractionsResult);
            
            // Step 5: Create comprehensive weekend getaway plan
            JsonObject getawayPlan = new JsonObject();
            getawayPlan.addProperty("trip_name", "Miami Weekend Getaway");
            getawayPlan.addProperty("dates", "August 23-25, 2025");
            getawayPlan.addProperty("origin", "Atlanta, GA");
            getawayPlan.addProperty("destination", "Miami, FL");
            getawayPlan.addProperty("trip_duration", "3 days, 2 nights");
            
            // Budget analysis
            JsonObject budgetAnalysis = new JsonObject();
            
            double flightCost = 0.0;
            if (flightSearchResult.has("price")) {
                flightCost = flightSearchResult.get("price").getAsDouble();
            }
            
            double rentalCost = 0.0;
            if (rentalSearchResult.has("available_rentals")) {
                JsonArray rentals = rentalSearchResult.get("available_rentals").getAsJsonArray();
                if (rentals.size() > 0) {
                    JsonObject firstRental = rentals.get(0).getAsJsonObject();
                    if (firstRental.has("price")) {
                        rentalCost = firstRental.get("price").getAsDouble() * 2; // 2 nights
                    }
                }
            }
            
            double gearCost = 0.0;
            for (int i = 0; i < beachGearArray.size(); i++) {
                JsonObject item = beachGearArray.get(i).getAsJsonObject();
                if (item.has("price") && item.has("name")) {
                    gearCost += item.get("price").getAsDouble();
                }
            }
            
            budgetAnalysis.addProperty("estimated_flight_cost", flightCost);
            budgetAnalysis.addProperty("estimated_accommodation_cost", rentalCost);
            budgetAnalysis.addProperty("estimated_gear_cost", gearCost);
            budgetAnalysis.addProperty("total_estimated_cost", flightCost + rentalCost + gearCost);
            budgetAnalysis.addProperty("budget_category", "Weekend Beach Getaway");
            
            getawayPlan.add("budget_analysis", budgetAnalysis);
            
            // Sightseeing plan
            JsonObject sightseeingPlan = new JsonObject();
            
            JsonArray dayPlans = new JsonArray();
            
            // Day 1 - Arrival
            JsonObject day1 = new JsonObject();
            day1.addProperty("day", "Friday, August 23");
            day1.addProperty("theme", "Arrival and Beach Time");
            day1.addProperty("activities", "Arrive in Miami, check into rental, visit nearby beach, sunset dinner");
            dayPlans.add(day1);
            
            // Day 2 - Exploration
            JsonObject day2 = new JsonObject();
            day2.addProperty("day", "Saturday, August 24");
            day2.addProperty("theme", "Tourist Attractions and Culture");
            day2.addProperty("activities", "Visit top-rated attractions, explore local museums, beach activities");
            dayPlans.add(day2);
            
            // Day 3 - Departure
            JsonObject day3 = new JsonObject();
            day3.addProperty("day", "Sunday, August 25");
            day3.addProperty("theme", "Final Beach Time and Departure");
            day3.addProperty("activities", "Morning beach visit, souvenir shopping, departure");
            dayPlans.add(day3);
            
            sightseeingPlan.add("daily_plans", dayPlans);
            
            if (attractionsResult.has("attractions")) {
                JsonArray topAttractions = new JsonArray();
                JsonArray attractions = attractionsResult.get("attractions").getAsJsonArray();
                for (int i = 0; i < Math.min(5, attractions.size()); i++) {
                    JsonObject attraction = attractions.get(i).getAsJsonObject();
                    topAttractions.add(attraction.get("name").getAsString() + " (" + attraction.get("type").getAsString() + ")");
                }
                sightseeingPlan.add("must_visit_attractions", topAttractions);
            }
            
            getawayPlan.add("sightseeing_plan", sightseeingPlan);
            
            // Travel tips and preparation
            JsonObject travelTips = new JsonObject();
            
            JsonArray packingList = new JsonArray();
            packingList.add("Beach gear (chairs, umbrella, cooler)");
            packingList.add("High SPF sunscreen");
            packingList.add("Swimwear and beach clothes");
            packingList.add("Light evening wear for dining");
            packingList.add("Comfortable walking shoes");
            packingList.add("Camera and portable charger");
            
            travelTips.add("packing_checklist", packingList);
            
            JsonArray recommendations = new JsonArray();
            recommendations.add("Book flights and accommodation early for better prices");
            recommendations.add("Check weather forecast before departure");
            recommendations.add("Research restaurant reservations in advance");
            recommendations.add("Download offline maps for navigation");
            recommendations.add("Bring reef-safe sunscreen for ocean activities");
            
            travelTips.add("travel_recommendations", recommendations);
            
            getawayPlan.add("travel_tips", travelTips);
            
            output.add("weekend_getaway_plan", getawayPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning the Miami weekend getaway: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
