import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0041 {
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
            // Step 1: Search for professional presentation equipment and tech accessories at Costco
            costco_com costco = new costco_com(context);
            JsonObject costcoResults = new JsonObject();
            
            try {
                costco_com.ProductListResult equipmentResults = costco.searchProducts("presentation equipment tech accessories");
                
                JsonArray equipmentArray = new JsonArray();
                double totalBasicCost = 0.0;
                double totalPremiumCost = 0.0;
                double totalExecutiveCost = 0.0;
                
                if (equipmentResults != null && equipmentResults.products != null) {
                    for (costco_com.ProductInfo product : equipmentResults.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("name", product.productName);
                        if (product.productPrice != null) {
                            productObj.addProperty("price", product.productPrice.amount);
                            productObj.addProperty("currency", product.productPrice.currency);
                            
                            // Calculate setup tiers based on price ranges
                            double price = product.productPrice.amount;
                            if (price <= 100) {
                                productObj.addProperty("tier", "Basic");
                                totalBasicCost += price;
                            } else if (price <= 500) {
                                productObj.addProperty("tier", "Premium");
                                totalPremiumCost += price;
                            } else {
                                productObj.addProperty("tier", "Executive");
                                totalExecutiveCost += price;
                            }
                        }
                        
                        if (product.error != null) {
                            productObj.addProperty("error", product.error);
                        }
                        equipmentArray.add(productObj);
                    }
                }
                
                costcoResults.add("equipment_options", equipmentArray);
                
                // Calculate setup packages for 50-person event
                JsonObject setupTiers = new JsonObject();
                setupTiers.addProperty("basic_package_total", totalBasicCost);
                setupTiers.addProperty("premium_package_total", totalBasicCost + totalPremiumCost);
                setupTiers.addProperty("executive_package_total", totalBasicCost + totalPremiumCost + totalExecutiveCost);
                setupTiers.addProperty("cost_per_person_basic", totalBasicCost / 50);
                setupTiers.addProperty("cost_per_person_premium", (totalBasicCost + totalPremiumCost) / 50);
                setupTiers.addProperty("cost_per_person_executive", (totalBasicCost + totalPremiumCost + totalExecutiveCost) / 50);
                setupTiers.addProperty("recommended_tier", (totalBasicCost + totalPremiumCost) <= 2500 ? "Premium" : "Basic");
                
                costcoResults.add("setup_tier_analysis", setupTiers);
                costcoResults.addProperty("event_size", "50 investors");
                costcoResults.addProperty("venue_type", "Tech startup investor meetup");
                
            } catch (Exception e) {
                costcoResults.addProperty("error", "Failed to search Costco equipment: " + e.getMessage());
            }
            
            output.add("costco_equipment_search", costcoResults);
            
            // Step 2: Search for hotels in downtown San Francisco for August 19-21, 2025
            booking_com booking = new booking_com(context);
            JsonObject bookingResults = new JsonObject();
            
            try {
                LocalDate checkinDate = LocalDate.of(2025, 8, 19);
                LocalDate checkoutDate = LocalDate.of(2025, 8, 21);
                
                booking_com.HotelSearchResult hotelResults = booking.search_hotel("San Francisco", checkinDate, checkoutDate);
                
                if (hotelResults != null) {
                    JsonObject hotelSearch = new JsonObject();
                    hotelSearch.addProperty("destination", hotelResults.destination);
                    hotelSearch.addProperty("checkin_date", hotelResults.checkinDate.toString());
                    hotelSearch.addProperty("checkout_date", hotelResults.checkoutDate.toString());
                    
                    JsonArray hotelsArray = new JsonArray();
                    double totalHotelCosts = 0.0;
                    int businessClassCount = 0;
                    
                    if (hotelResults.hotels != null) {
                        for (booking_com.HotelInfo hotel : hotelResults.hotels) {
                            JsonObject hotelObj = new JsonObject();
                            hotelObj.addProperty("hotel_name", hotel.hotelName);
                            
                            if (hotel.price != null) {
                                hotelObj.addProperty("price_per_night", hotel.price.amount);
                                hotelObj.addProperty("currency", hotel.price.currency);
                                hotelObj.addProperty("total_cost_2_nights", hotel.price.amount * 2);
                                totalHotelCosts += hotel.price.amount * 2;
                                
                                // Classify as business-class if price is reasonable for investors
                                if (hotel.price.amount >= 200 && hotel.price.amount <= 800) {
                                    hotelObj.addProperty("category", "Business-class suitable for investors");
                                    businessClassCount++;
                                } else if (hotel.price.amount > 800) {
                                    hotelObj.addProperty("category", "Luxury premium option");
                                } else {
                                    hotelObj.addProperty("category", "Budget option");
                                }
                            }
                            
                            hotelsArray.add(hotelObj);
                        }
                    }
                    
                    hotelSearch.add("available_hotels", hotelsArray);
                    hotelSearch.addProperty("business_class_options", businessClassCount);
                    hotelSearch.addProperty("average_cost_per_investor", hotelsArray.size() > 0 ? totalHotelCosts / hotelsArray.size() : 0);
                    hotelSearch.addProperty("recommended_budget_range", "$400-$1600 total per investor for 2 nights");
                    
                    bookingResults.add("hotel_search_results", hotelSearch);
                }
                
                bookingResults.addProperty("target_area", "Downtown San Francisco - Financial District");
                bookingResults.addProperty("investor_accommodation_focus", "Business-class properties for professional image");
                
            } catch (Exception e) {
                bookingResults.addProperty("error", "Failed to search hotels: " + e.getMessage());
            }
            
            output.add("hotel_accommodation_search", bookingResults);
            
            // Step 3: Get directions from San Francisco International Airport to downtown hotels
            maps_google_com maps = new maps_google_com(context);
            JsonObject directionsResults = new JsonObject();
            
            try {
                maps_google_com.DirectionResult directions = maps.get_direction("San Francisco International Airport", "downtown San Francisco hotels");
                
                if (directions != null) {
                    JsonObject routeInfo = new JsonObject();
                    routeInfo.addProperty("travel_time", directions.travelTime);
                    routeInfo.addProperty("distance", directions.distance);
                    routeInfo.addProperty("route_description", directions.route);
                    
                    // Calculate arrival planning recommendations
                    JsonArray arrivalTips = new JsonArray();
                    arrivalTips.add("Plan 45-60 minutes travel time from SFO to downtown hotels");
                    arrivalTips.add("Consider traffic during weekday afternoon hours (3-7 PM)");
                    arrivalTips.add("Uber/Lyft recommended for door-to-door convenience");
                    arrivalTips.add("BART public transit available as cost-effective alternative");
                    arrivalTips.add("Pre-arrange group transportation for multiple investors");
                    
                    routeInfo.add("investor_arrival_recommendations", arrivalTips);
                    routeInfo.addProperty("optimal_arrival_window", "Before 2 PM or after 8 PM to avoid peak traffic");
                    
                    directionsResults.add("airport_to_hotel_route", routeInfo);
                }
                
                directionsResults.addProperty("departure_point", "San Francisco International Airport (SFO)");
                directionsResults.addProperty("destination_area", "Downtown San Francisco Financial District");
                directionsResults.addProperty("transportation_purpose", "Investor arrival logistics for August 20 meetup");
                
            } catch (Exception e) {
                directionsResults.addProperty("error", "Failed to get directions: " + e.getMessage());
            }
            
            output.add("transportation_logistics", directionsResults);
            
            // Step 4: Find upscale restaurants and catering services around Union Square
            JsonObject cateringResults = new JsonObject();
            
            try {
                maps_google_com.NearestBusinessesResult restaurants = maps.get_nearestBusinesses("Union Square San Francisco", "upscale restaurants catering", 10);
                
                if (restaurants != null) {
                    JsonObject cateringSearch = new JsonObject();
                    cateringSearch.addProperty("search_area", restaurants.referencePoint);
                    cateringSearch.addProperty("business_type", restaurants.businessDescription);
                    
                    JsonArray restaurantArray = new JsonArray();
                    JsonArray networkingVenues = new JsonArray();
                    JsonArray cateringOptions = new JsonArray();
                    
                    if (restaurants.businesses != null) {
                        for (maps_google_com.BusinessInfo business : restaurants.businesses) {
                            JsonObject businessObj = new JsonObject();
                            businessObj.addProperty("name", business.name);
                            businessObj.addProperty("address", business.address);
                            
                            // Categorize venues based on likely suitability for investors
                            String lowerName = business.name.toLowerCase();
                            if (lowerName.contains("steakhouse") || lowerName.contains("fine dining") || 
                                lowerName.contains("rooftop") || lowerName.contains("wine")) {
                                businessObj.addProperty("category", "Premium networking venue");
                                businessObj.addProperty("investor_suitability", "Excellent for impressing investors");
                                networkingVenues.add(businessObj);
                            } else if (lowerName.contains("catering") || lowerName.contains("events")) {
                                businessObj.addProperty("category", "Professional catering service");
                                businessObj.addProperty("investor_suitability", "Suitable for meeting catering");
                                cateringOptions.add(businessObj);
                            } else {
                                businessObj.addProperty("category", "Upscale restaurant option");
                                businessObj.addProperty("investor_suitability", "Good for group dining");
                            }
                            
                            restaurantArray.add(businessObj);
                        }
                    }
                    
                    cateringSearch.add("all_dining_options", restaurantArray);
                    cateringSearch.add("premium_networking_venues", networkingVenues);
                    cateringSearch.add("catering_services", cateringOptions);
                    cateringSearch.addProperty("total_options_found", restaurantArray.size());
                    
                    // Dining strategy recommendations
                    JsonArray diningStrategy = new JsonArray();
                    diningStrategy.add("Book premium venue for investor dinner on August 19th");
                    diningStrategy.add("Arrange catered lunch during meetup presentations");
                    diningStrategy.add("Plan cocktail reception at rooftop venue for networking");
                    diningStrategy.add("Consider dietary restrictions for diverse investor group");
                    diningStrategy.add("Budget $150-300 per person for high-quality dining experience");
                    
                    cateringSearch.add("dining_strategy_recommendations", diningStrategy);
                    
                    cateringResults.add("union_square_dining_search", cateringSearch);
                }
                
                cateringResults.addProperty("catering_focus", "High-quality dining to impress potential investors");
                cateringResults.addProperty("networking_priority", "Facilitate investor connections through exceptional dining");
                
            } catch (Exception e) {
                cateringResults.addProperty("error", "Failed to find restaurants: " + e.getMessage());
            }
            
            output.add("dining_catering_options", cateringResults);
            
            // Step 5: Create comprehensive meetup planning summary
            JsonObject meetupSummary = new JsonObject();
            meetupSummary.addProperty("event_title", "Tech Startup Investor Meetup San Francisco");
            meetupSummary.addProperty("event_date", "August 20, 2025");
            meetupSummary.addProperty("event_location", "San Francisco, California");
            meetupSummary.addProperty("expected_attendees", "50 investors");
            
            // Budget analysis
            JsonObject budgetAnalysis = new JsonObject();
            budgetAnalysis.addProperty("equipment_budget_range", "$1,000 - $5,000 depending on setup tier");
            budgetAnalysis.addProperty("accommodation_per_investor", "$400 - $1,600 for 2 nights");
            budgetAnalysis.addProperty("dining_per_person", "$150 - $300 for premium experience");
            budgetAnalysis.addProperty("transportation_coordination", "Arrange group pickup service from SFO");
            budgetAnalysis.addProperty("total_estimated_budget", "$35,000 - $85,000 for complete event");
            
            meetupSummary.add("budget_analysis", budgetAnalysis);
            
            // Success factors
            JsonArray successFactors = new JsonArray();
            successFactors.add("Professional presentation setup creates strong first impressions");
            successFactors.add("Convenient downtown accommodation keeps investors engaged");
            successFactors.add("Premium dining experiences facilitate meaningful connections");
            successFactors.add("Smooth logistics allow focus on startup presentations");
            successFactors.add("Union Square location provides easy access to city attractions");
            
            meetupSummary.add("event_success_factors", successFactors);
            
            // Next steps
            JsonArray nextSteps = new JsonArray();
            nextSteps.add("Finalize equipment tier selection based on startup presentation needs");
            nextSteps.add("Book 10-15 hotel rooms in financial district for out-of-town investors");
            nextSteps.add("Reserve premium restaurant for August 19th welcome dinner");
            nextSteps.add("Arrange catering for August 20th meetup lunch and networking session");
            nextSteps.add("Coordinate airport pickup schedule with investor travel plans");
            
            meetupSummary.add("recommended_next_steps", nextSteps);
            
            output.add("meetup_planning_summary", meetupSummary);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning investor meetup: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
