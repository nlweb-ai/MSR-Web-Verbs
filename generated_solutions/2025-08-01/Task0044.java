import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0044 {
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
            // Step 1: Search for flights from Chicago O'Hare to New Orleans for August 18-21, 2025
            alaskaair_com alaska = new alaskaair_com(context);
            JsonObject flightResults = new JsonObject();
            
            try {
                LocalDate outboundDate = LocalDate.of(2025, 8, 18);
                LocalDate returnDate = LocalDate.of(2025, 8, 21);
                
                alaskaair_com.SearchFlightsResult flightSearch = alaska.searchFlights("ORD", "MSY", outboundDate, returnDate);
                
                if (flightSearch != null) {
                    JsonObject flightInfo = new JsonObject();
                    flightInfo.addProperty("origin", "Chicago O'Hare (ORD)");
                    flightInfo.addProperty("destination", "New Orleans Louis Armstrong (MSY)");
                    flightInfo.addProperty("outbound_date", outboundDate.toString());
                    flightInfo.addProperty("return_date", returnDate.toString());
                    flightInfo.addProperty("trip_duration", "4 days, 3 nights");
                    
                    if (flightSearch.message != null) {
                        flightInfo.addProperty("search_message", flightSearch.message);
                    }
                    
                    if (flightSearch.flightInfo != null) {
                        JsonArray flightsArray = new JsonArray();
                        JsonObject flightAnalysis = new JsonObject();
                        
                        if (flightSearch.flightInfo.flights != null) {
                            for (String flight : flightSearch.flightInfo.flights) {
                                JsonObject flightObj = new JsonObject();
                                flightObj.addProperty("flight_details", flight);
                                
                                // Analyze flight timing for food exploration opportunities
                                String flightLower = flight.toLowerCase();
                                if (flightLower.contains("morning") || flightLower.contains("am")) {
                                    flightObj.addProperty("timing_category", "Morning Departure/Arrival");
                                    flightObj.addProperty("culinary_advantage", "Arrive early for lunch exploration or late breakfast at French Market");
                                } else if (flightLower.contains("afternoon") || flightLower.contains("pm")) {
                                    flightObj.addProperty("timing_category", "Afternoon Departure/Arrival");
                                    flightObj.addProperty("culinary_advantage", "Perfect timing for dinner at renowned Creole restaurants");
                                } else if (flightLower.contains("evening") || flightLower.contains("night")) {
                                    flightObj.addProperty("timing_category", "Evening Departure/Arrival");
                                    flightObj.addProperty("culinary_advantage", "Late arrival allows for next-day full food experience");
                                } else {
                                    flightObj.addProperty("timing_category", "Standard Timing");
                                    flightObj.addProperty("culinary_advantage", "Good flexibility for meal planning");
                                }
                                
                                flightsArray.add(flightObj);
                            }
                        }
                        
                        if (flightSearch.flightInfo.price != null) {
                            flightAnalysis.addProperty("total_price", flightSearch.flightInfo.price.amount);
                            flightAnalysis.addProperty("currency", flightSearch.flightInfo.price.currency);
                            
                            // Calculate value for culinary tourism
                            double price = flightSearch.flightInfo.price.amount;
                            if (price <= 300) {
                                flightAnalysis.addProperty("value_assessment", "Excellent - budget-friendly allows more spending on dining");
                                flightAnalysis.addProperty("dining_budget_impact", "Extra $200-400 available for premium restaurant experiences");
                            } else if (price <= 600) {
                                flightAnalysis.addProperty("value_assessment", "Good - reasonable cost for culinary tourism");
                                flightAnalysis.addProperty("dining_budget_impact", "Balanced budget for quality food experiences");
                            } else {
                                flightAnalysis.addProperty("value_assessment", "Premium - higher cost but worth it for food adventure");
                                flightAnalysis.addProperty("dining_budget_impact", "Focus on must-try signature restaurants");
                            }
                        }
                        
                        // Optimal timing analysis for food exploration
                        JsonObject timingOptimization = new JsonObject();
                        timingOptimization.addProperty("ideal_outbound", "Morning arrival to maximize first day dining opportunities");
                        timingOptimization.addProperty("ideal_return", "Evening departure to enjoy final New Orleans brunch or lunch");
                        timingOptimization.addProperty("food_exploration_time", "3 full days plus arrival/departure partial days");
                        timingOptimization.addProperty("meal_opportunities", "9-12 major meals plus snacks and market visits");
                        
                        JsonArray culinarySchedule = new JsonArray();
                        culinarySchedule.add("Day 1 (Aug 18): Arrival + French Market + dinner at classic Creole restaurant");
                        culinarySchedule.add("Day 2 (Aug 19): Breakfast + lunch + cooking class + dinner at fine dining");
                        culinarySchedule.add("Day 3 (Aug 20): Food tour + multiple tastings + po'boy crawl + jazz brunch");
                        culinarySchedule.add("Day 4 (Aug 21): Final breakfast/brunch + souvenir food shopping + departure");
                        
                        timingOptimization.add("suggested_culinary_schedule", culinarySchedule);
                        flightAnalysis.add("timing_optimization", timingOptimization);
                        
                        flightInfo.add("available_flights", flightsArray);
                        flightInfo.add("flight_analysis", flightAnalysis);
                    }
                    
                    flightResults.add("chicago_to_new_orleans_flights", flightInfo);
                }
                
                flightResults.addProperty("travel_purpose", "Culinary tourism and food culture immersion");
                flightResults.addProperty("trip_focus", "Maximum time for authentic New Orleans dining experiences");
                
            } catch (Exception e) {
                flightResults.addProperty("error", "Failed to search flights: " + e.getMessage());
            }
            
            output.add("flight_arrangements", flightResults);
            
            // Step 2: Search for hotels in French Quarter for August 18-21, 2025
            booking_com booking = new booking_com(context);
            JsonObject hotelResults = new JsonObject();
            
            try {
                LocalDate checkinDate = LocalDate.of(2025, 8, 18);
                LocalDate checkoutDate = LocalDate.of(2025, 8, 21);
                
                booking_com.HotelSearchResult hotelSearch = booking.search_hotel("New Orleans French Quarter", checkinDate, checkoutDate);
                
                if (hotelSearch != null) {
                    JsonObject accommodationInfo = new JsonObject();
                    accommodationInfo.addProperty("location", hotelSearch.destination);
                    accommodationInfo.addProperty("checkin_date", hotelSearch.checkinDate.toString());
                    accommodationInfo.addProperty("checkout_date", hotelSearch.checkoutDate.toString());
                    accommodationInfo.addProperty("target_area", "French Quarter - Heart of New Orleans culinary scene");
                    
                    JsonArray hotelsArray = new JsonArray();
                    JsonArray walkableOptions = new JsonArray();
                    double totalAccommodationCosts = 0.0;
                    int premiumLocationCount = 0;
                    
                    if (hotelSearch.hotels != null) {
                        for (booking_com.HotelInfo hotel : hotelSearch.hotels) {
                            JsonObject hotelObj = new JsonObject();
                            hotelObj.addProperty("hotel_name", hotel.hotelName);
                            
                            if (hotel.price != null) {
                                hotelObj.addProperty("price_per_night", hotel.price.amount);
                                hotelObj.addProperty("currency", hotel.price.currency);
                                hotelObj.addProperty("total_cost_3_nights", hotel.price.amount * 3);
                                totalAccommodationCosts += hotel.price.amount * 3;
                                
                                // Assess value for culinary tourism
                                double pricePerNight = hotel.price.amount;
                                if (pricePerNight <= 150) {
                                    hotelObj.addProperty("culinary_tourism_value", "Budget-friendly - more money for dining experiences");
                                    hotelObj.addProperty("location_advantage", "Good base for food exploration");
                                } else if (pricePerNight <= 300) {
                                    hotelObj.addProperty("culinary_tourism_value", "Mid-range - balanced comfort and dining budget");
                                    hotelObj.addProperty("location_advantage", "Prime location near top restaurants");
                                    premiumLocationCount++;
                                } else {
                                    hotelObj.addProperty("culinary_tourism_value", "Luxury - premium location with concierge dining assistance");
                                    hotelObj.addProperty("location_advantage", "Steps from finest restaurants and food markets");
                                    premiumLocationCount++;
                                }
                            }
                            
                            // Analyze hotel name for location indicators
                            String hotelName = hotel.hotelName.toLowerCase();
                            if (hotelName.contains("french quarter") || hotelName.contains("bourbon") || 
                                hotelName.contains("royal") || hotelName.contains("dauphine")) {
                                hotelObj.addProperty("location_category", "Prime French Quarter Location");
                                hotelObj.addProperty("walking_distance", "Within 2-3 blocks of major restaurants");
                                hotelObj.addProperty("food_access", "Walk to Cafe du Monde, Mother's, Commander's Palace area");
                                walkableOptions.add(hotelObj);
                            } else if (hotelName.contains("quarter") || hotelName.contains("old town") || 
                                      hotelName.contains("historic")) {
                                hotelObj.addProperty("location_category", "Historic District Location");
                                hotelObj.addProperty("walking_distance", "5-8 blocks to main restaurant corridors");
                                hotelObj.addProperty("food_access", "Easy walk to French Market and Decatur Street dining");
                            } else {
                                hotelObj.addProperty("location_category", "General French Quarter Area");
                                hotelObj.addProperty("walking_distance", "Variable - check specific location");
                                hotelObj.addProperty("food_access", "May require short streetcar or taxi to prime dining areas");
                            }
                            
                            // Transportation and convenience analysis
                            JsonObject convenienceFactors = new JsonObject();
                            convenienceFactors.addProperty("food_market_access", "Walking distance to French Market and local food vendors");
                            convenienceFactors.addProperty("restaurant_density", "High concentration of authentic Creole and Cajun restaurants");
                            convenienceFactors.addProperty("transportation_needs", "Minimal - most culinary experiences within walking distance");
                            convenienceFactors.addProperty("cultural_immersion", "Stay in heart of culinary traditions and local food culture");
                            
                            hotelObj.add("culinary_convenience", convenienceFactors);
                            hotelsArray.add(hotelObj);
                        }
                    }
                    
                    accommodationInfo.add("available_hotels", hotelsArray);
                    accommodationInfo.add("walkable_prime_locations", walkableOptions);
                    accommodationInfo.addProperty("total_hotels_found", hotelsArray.size());
                    accommodationInfo.addProperty("premium_location_count", premiumLocationCount);
                    accommodationInfo.addProperty("average_cost_3_nights", hotelsArray.size() > 0 ? totalAccommodationCosts / hotelsArray.size() : 0);
                    
                    // French Quarter culinary advantages
                    JsonObject quarterAdvantages = new JsonObject();
                    quarterAdvantages.addProperty("restaurant_walkability", "95% of top restaurants within 10-minute walk");
                    quarterAdvantages.addProperty("food_market_access", "French Market, farmers markets, and specialty food shops nearby");
                    quarterAdvantages.addProperty("cultural_authenticity", "Stay where locals and chefs live and work");
                    quarterAdvantages.addProperty("evening_dining", "Safe walking to dinner and late-night food spots");
                    
                    JsonArray quarterCulinaryHighlights = new JsonArray();
                    quarterCulinaryHighlights.add("Cafe du Monde for beignets and coffee (2-3 blocks from most hotels)");
                    quarterCulinaryHighlights.add("French Market for local ingredients and prepared foods");
                    quarterCulinaryHighlights.add("Royal Street for fine dining and chef-owned restaurants");
                    quarterCulinaryHighlights.add("Bourbon Street for casual po'boys and local bars with food");
                    quarterCulinaryHighlights.add("Magazine Street corridor accessible via streetcar for additional dining");
                    
                    quarterAdvantages.add("nearby_culinary_attractions", quarterCulinaryHighlights);
                    accommodationInfo.add("french_quarter_culinary_advantages", quarterAdvantages);
                    
                    hotelResults.add("french_quarter_accommodation", accommodationInfo);
                }
                
                hotelResults.addProperty("accommodation_strategy", "Minimize transportation to maximize food exploration time");
                hotelResults.addProperty("location_priority", "Walking distance to authentic restaurants and food markets");
                
            } catch (Exception e) {
                hotelResults.addProperty("error", "Failed to search hotels: " + e.getMessage());
            }
            
            output.add("accommodation_planning", hotelResults);
            
            // Step 3: Get directions from airport to French Quarter with food market stops
            maps_google_com maps = new maps_google_com(context);
            JsonObject directionsResults = new JsonObject();
            
            try {
                maps_google_com.DirectionResult airportToQuarter = maps.get_direction("Louis Armstrong New Orleans International Airport", "French Quarter New Orleans");
                
                if (airportToQuarter != null) {
                    JsonObject routeInfo = new JsonObject();
                    routeInfo.addProperty("travel_time", airportToQuarter.travelTime);
                    routeInfo.addProperty("distance", airportToQuarter.distance);
                    routeInfo.addProperty("route_description", airportToQuarter.route);
                    routeInfo.addProperty("origin", "Louis Armstrong New Orleans International Airport (MSY)");
                    routeInfo.addProperty("destination", "French Quarter Hotels");
                    
                    // Food-focused arrival strategy
                    JsonObject arrivalStrategy = new JsonObject();
                    arrivalStrategy.addProperty("immediate_food_stop", "French Market for first taste of local flavors");
                    arrivalStrategy.addProperty("arrival_timing", "Plan 45-60 minutes airport to hotel including food stop");
                    arrivalStrategy.addProperty("transportation_recommendation", "Taxi or rideshare for convenience with luggage");
                    arrivalStrategy.addProperty("food_market_timing", "French Market open daily - perfect for arrival day introduction");
                    
                    // Create food-focused arrival itinerary
                    JsonArray arrivalItinerary = new JsonArray();
                    arrivalItinerary.add("Land at MSY and collect luggage (20-30 minutes)");
                    arrivalItinerary.add("Taxi/rideshare to French Market (25-30 minutes)");
                    arrivalItinerary.add("Quick stop at French Market for local snacks and cafe au lait (15-20 minutes)");
                    arrivalItinerary.add("Continue to French Quarter hotel (5-10 minutes)");
                    arrivalItinerary.add("Check in and begin culinary adventure immediately");
                    
                    arrivalStrategy.add("suggested_arrival_itinerary", arrivalItinerary);
                    
                    // Alternative routes with food considerations
                    JsonArray routeOptions = new JsonArray();
                    routeOptions.add("Direct route: Fastest to hotel, then walk to nearby restaurants");
                    routeOptions.add("French Market route: Immediate food introduction, slight detour");
                    routeOptions.add("Magazine Street route: Preview upscale dining area, longer drive");
                    routeOptions.add("Streetcar route: Cultural experience but longer with luggage");
                    
                    arrivalStrategy.add("route_options_with_food_focus", routeOptions);
                    
                    routeInfo.add("culinary_arrival_strategy", arrivalStrategy);
                    directionsResults.add("airport_to_french_quarter", routeInfo);
                }
                
                // Departure strategy for final food purchases
                JsonObject departureStrategy = new JsonObject();
                departureStrategy.addProperty("final_food_shopping", "French Market and specialty shops for take-home items");
                departureStrategy.addProperty("departure_timing", "Allow 90 minutes for final meal and airport travel");
                departureStrategy.addProperty("last_meal_recommendation", "Classic New Orleans brunch before departure");
                departureStrategy.addProperty("souvenir_foods", "Beignet mix, coffee beans, hot sauce, and pralines");
                
                directionsResults.add("departure_planning", departureStrategy);
                directionsResults.addProperty("transportation_focus", "Minimize travel time to maximize eating time");
                
            } catch (Exception e) {
                directionsResults.addProperty("error", "Failed to get directions: " + e.getMessage());
            }
            
            output.add("transportation_and_logistics", directionsResults);
            
            // Step 4: Find authentic Creole and Cajun restaurants near French Quarter
            JsonObject restaurantResults = new JsonObject();
            
            try {
                maps_google_com.NearestBusinessesResult restaurants = maps.get_nearestBusinesses("French Quarter New Orleans", "authentic Creole Cajun restaurants", 12);
                
                if (restaurants != null) {
                    JsonObject diningGuide = new JsonObject();
                    diningGuide.addProperty("search_area", restaurants.referencePoint);
                    diningGuide.addProperty("cuisine_focus", restaurants.businessDescription);
                    
                    JsonArray authenticRestaurants = new JsonArray();
                    JsonArray signatureDishes = new JsonArray();
                    JsonArray mustTryExperiences = new JsonArray();
                    JsonArray casualDining = new JsonArray();
                    JsonArray fineDining = new JsonArray();
                    
                    if (restaurants.businesses != null) {
                        for (maps_google_com.BusinessInfo restaurant : restaurants.businesses) {
                            JsonObject restaurantObj = new JsonObject();
                            restaurantObj.addProperty("restaurant_name", restaurant.name);
                            restaurantObj.addProperty("address", restaurant.address);
                            
                            // Categorize restaurants by name and likely offerings
                            String restaurantName = restaurant.name.toLowerCase();
                            
                            // Identify signature dish specialties
                            if (restaurantName.contains("gumbo") || restaurantName.contains("creole")) {
                                restaurantObj.addProperty("signature_dish", "Gumbo - traditional Creole stew");
                                restaurantObj.addProperty("must_try", "Seafood gumbo or chicken and andouille");
                                signatureDishes.add("Creole Gumbo at " + restaurant.name);
                            } else if (restaurantName.contains("jambalaya") || restaurantName.contains("cajun")) {
                                restaurantObj.addProperty("signature_dish", "Jambalaya - rice dish with seafood/meat");
                                restaurantObj.addProperty("must_try", "Shrimp and andouille jambalaya");
                                signatureDishes.add("Authentic Jambalaya at " + restaurant.name);
                            } else if (restaurantName.contains("po'boy") || restaurantName.contains("sandwich")) {
                                restaurantObj.addProperty("signature_dish", "Po'boys - traditional New Orleans sandwiches");
                                restaurantObj.addProperty("must_try", "Fried shrimp or roast beef debris po'boy");
                                signatureDishes.add("Classic Po'boys at " + restaurant.name);
                            } else if (restaurantName.contains("beignet") || restaurantName.contains("cafe")) {
                                restaurantObj.addProperty("signature_dish", "Beignets and cafe au lait");
                                restaurantObj.addProperty("must_try", "Fresh hot beignets with powdered sugar");
                                signatureDishes.add("Traditional Beignets at " + restaurant.name);
                            } else {
                                restaurantObj.addProperty("signature_dish", "Mixed Creole and Cajun specialties");
                                restaurantObj.addProperty("must_try", "Chef's seasonal recommendations");
                            }
                            
                            // Categorize by dining style and price point
                            if (restaurantName.contains("commander") || restaurantName.contains("galatoire") || 
                                restaurantName.contains("antoine") || restaurantName.contains("fine")) {
                                restaurantObj.addProperty("dining_category", "Fine Dining");
                                restaurantObj.addProperty("experience_level", "Special occasion, upscale atmosphere");
                                restaurantObj.addProperty("price_range", "$$$$ - Premium pricing for exceptional cuisine");
                                restaurantObj.addProperty("reservation_needed", "Highly recommended - book in advance");
                                fineDining.add(restaurantObj);
                            } else if (restaurantName.contains("mother") || restaurantName.contains("acme") || 
                                      restaurantName.contains("cafe") || restaurantName.contains("corner")) {
                                restaurantObj.addProperty("dining_category", "Casual Local Favorite");
                                restaurantObj.addProperty("experience_level", "Authentic local experience, relaxed atmosphere");
                                restaurantObj.addProperty("price_range", "$$ - Moderate pricing for quality food");
                                restaurantObj.addProperty("reservation_needed", "Walk-ins usually welcome");
                                casualDining.add(restaurantObj);
                            } else {
                                restaurantObj.addProperty("dining_category", "Traditional Restaurant");
                                restaurantObj.addProperty("experience_level", "Classic New Orleans dining");
                                restaurantObj.addProperty("price_range", "$$$ - Standard pricing for tourist area");
                                restaurantObj.addProperty("reservation_needed", "Recommended for dinner");
                            }
                            
                            // Add cultural and culinary context
                            JsonObject culturalContext = new JsonObject();
                            culturalContext.addProperty("culinary_tradition", "Blend of French, African, Spanish, and Native American influences");
                            culturalContext.addProperty("local_ingredients", "Gulf seafood, andouille sausage, okra, rice, and local spices");
                            culturalContext.addProperty("cooking_methods", "Traditional roux-based sauces and slow-simmered dishes");
                            culturalContext.addProperty("cultural_significance", "Represents unique New Orleans food heritage");
                            
                            restaurantObj.add("cultural_context", culturalContext);
                            authenticRestaurants.add(restaurantObj);
                            
                            // Create must-try experiences
                            String experienceDesc = "Experience authentic " + restaurant.name + " for traditional flavors";
                            mustTryExperiences.add(experienceDesc);
                        }
                    }
                    
                    diningGuide.add("all_authentic_restaurants", authenticRestaurants);
                    diningGuide.add("fine_dining_options", fineDining);
                    diningGuide.add("casual_local_favorites", casualDining);
                    diningGuide.add("signature_dishes_to_try", signatureDishes);
                    diningGuide.add("must_try_experiences", mustTryExperiences);
                    diningGuide.addProperty("total_restaurants_found", authenticRestaurants.size());
                    
                    // Create comprehensive dining itinerary
                    JsonObject diningItinerary = new JsonObject();
                    
                    JsonArray dayByDayPlan = new JsonArray();
                    dayByDayPlan.add("Day 1 Evening: Arrival dinner at casual local favorite for first authentic taste");
                    dayByDayPlan.add("Day 2: Breakfast beignets + lunch po'boys + dinner at fine dining establishment");
                    dayByDayPlan.add("Day 3: Food tour with multiple tastings + evening at traditional Creole restaurant");
                    dayByDayPlan.add("Day 4: Final brunch with gumbo and jambalaya before departure");
                    
                    JsonArray essentialDishes = new JsonArray();
                    essentialDishes.add("Gumbo (seafood or chicken and andouille) - lunch or dinner");
                    essentialDishes.add("Jambalaya (shrimp and andouille) - lunch or dinner");
                    essentialDishes.add("Po'boys (fried shrimp or roast beef debris) - lunch");
                    essentialDishes.add("Beignets and cafe au lait - breakfast or afternoon snack");
                    essentialDishes.add("Bananas Foster or bread pudding - dessert");
                    essentialDishes.add("Chargrilled oysters - appetizer");
                    essentialDishes.add("Red beans and rice - Monday traditional dish");
                    essentialDishes.add("Muffuletta sandwich - lunch option");
                    
                    diningItinerary.add("day_by_day_dining_plan", dayByDayPlan);
                    diningItinerary.add("essential_dishes_checklist", essentialDishes);
                    
                    // Budget and logistics
                    JsonObject diningLogistics = new JsonObject();
                    diningLogistics.addProperty("budget_per_person_per_day", "$75-150 depending on restaurant choices");
                    diningLogistics.addProperty("total_food_budget_estimate", "$225-450 per person for 3 days");
                    diningLogistics.addProperty("walking_accessibility", "All restaurants within 10-minute walk from French Quarter hotels");
                    diningLogistics.addProperty("reservation_strategy", "Book fine dining in advance, casual spots allow walk-ins");
                    
                    diningItinerary.add("dining_logistics", diningLogistics);
                    diningGuide.add("comprehensive_dining_itinerary", diningItinerary);
                    
                    restaurantResults.add("french_quarter_dining_guide", diningGuide);
                }
                
                restaurantResults.addProperty("culinary_focus", "Authentic Creole and Cajun cuisine in historic French Quarter");
                restaurantResults.addProperty("cultural_immersion", "Experience traditional New Orleans food culture and heritage");
                
            } catch (Exception e) {
                restaurantResults.addProperty("error", "Failed to find restaurants: " + e.getMessage());
            }
            
            output.add("restaurant_research", restaurantResults);
            
            // Step 5: Create comprehensive culinary tourism plan
            JsonObject culinaryPlan = new JsonObject();
            culinaryPlan.addProperty("trip_title", "New Orleans Culinary Tourism Experience");
            culinaryPlan.addProperty("dates", "August 18-21, 2025");
            culinaryPlan.addProperty("duration", "4 days, 3 nights");
            culinaryPlan.addProperty("location", "New Orleans, Louisiana - French Quarter");
            culinaryPlan.addProperty("focus", "Immersive food and culture experience showcasing New Orleans gastronomy");
            
            // Trip overview and objectives
            JsonObject tripObjectives = new JsonObject();
            tripObjectives.addProperty("culinary_education", "Learn about Creole and Cajun cooking traditions and history");
            tripObjectives.addProperty("authentic_experiences", "Dine where locals eat and discover traditional recipes");
            tripObjectives.addProperty("cultural_immersion", "Understand food's role in New Orleans culture and community");
            tripObjectives.addProperty("gastronomic_adventure", "Taste signature dishes and unique local specialties");
            
            JsonArray culturalLearning = new JsonArray();
            culturalLearning.add("French colonial culinary influences and techniques");
            culturalLearning.add("African contributions to New Orleans cuisine");
            culturalLearning.add("Spanish and Caribbean flavors in local dishes");
            culturalLearning.add("Native American ingredients and cooking methods");
            culturalLearning.add("Modern chef innovations on traditional recipes");
            
            tripObjectives.add("cultural_learning_goals", culturalLearning);
            culinaryPlan.add("trip_objectives", tripObjectives);
            
            // Comprehensive itinerary
            JsonObject detailedItinerary = new JsonObject();
            
            JsonArray day1 = new JsonArray();
            day1.add("Morning: Arrive MSY airport, taxi to French Market for first local flavors");
            day1.add("Afternoon: Check into French Quarter hotel, explore neighborhood food shops");
            day1.add("Evening: Dinner at classic Creole restaurant - first authentic gumbo experience");
            day1.add("Night: Evening stroll through French Quarter, dessert at local cafe");
            
            JsonArray day2 = new JsonArray();
            day2.add("Morning: Breakfast beignets and cafe au lait at traditional cafe");
            day2.add("Afternoon: Po'boy lunch crawl - try multiple sandwich varieties");
            day2.add("Evening: Fine dining experience at historic restaurant - jambalaya and seafood");
            day2.add("Night: Jazz club with small plates and local cocktails");
            
            JsonArray day3 = new JsonArray();
            day3.add("Morning: Food market tour and cooking class with local chef");
            day3.add("Afternoon: Guided food tour with multiple restaurant tastings");
            day3.add("Evening: Traditional Creole family-style dinner with local food stories");
            day3.add("Night: Late-night food spots - chargrilled oysters and local specialties");
            
            JsonArray day4 = new JsonArray();
            day4.add("Morning: Final New Orleans brunch - red beans and rice tradition");
            day4.add("Afternoon: Food souvenir shopping - local spices, coffee, hot sauce");
            day4.add("Evening: Departure from MSY with culinary memories and local ingredients");
            
            detailedItinerary.add("day_1_arrival", day1);
            detailedItinerary.add("day_2_exploration", day2);
            detailedItinerary.add("day_3_immersion", day3);
            detailedItinerary.add("day_4_departure", day4);
            
            culinaryPlan.add("detailed_daily_itinerary", detailedItinerary);
            
            // Budget breakdown and recommendations
            JsonObject budgetPlanning = new JsonObject();
            budgetPlanning.addProperty("flights_chicago_to_new_orleans", "$300-600 per person");
            budgetPlanning.addProperty("accommodation_french_quarter", "$150-300 per night");
            budgetPlanning.addProperty("dining_experiences", "$225-450 per person total");
            budgetPlanning.addProperty("transportation_local", "$50-100 for airport transfers and local transport");
            budgetPlanning.addProperty("food_souvenirs", "$50-150 for take-home items");
            budgetPlanning.addProperty("total_estimated_cost", "$925-1850 per person for complete experience");
            
            JsonObject budgetTips = new JsonObject();
            budgetTips.addProperty("money_saving", "Mix fine dining with casual local spots for authentic variety");
            budgetTips.addProperty("value_maximizing", "Stay in French Quarter to minimize transportation costs");
            budgetTips.addProperty("experience_optimization", "Book one special dinner, explore lunch spots for variety");
            budgetTips.addProperty("local_wisdom", "Ask locals and hotel staff for hidden gem recommendations");
            
            budgetPlanning.add("budget_optimization_tips", budgetTips);
            culinaryPlan.add("budget_planning", budgetPlanning);
            
            // Success metrics and memories
            JsonArray successIndicators = new JsonArray();
            successIndicators.add("Taste all essential New Orleans dishes: gumbo, jambalaya, po'boys, beignets");
            successIndicators.add("Experience both casual local favorites and fine dining establishments");
            successIndicators.add("Learn about culinary history and cultural significance of foods");
            successIndicators.add("Discover new flavors and cooking techniques to recreate at home");
            successIndicators.add("Create lasting memories of authentic New Orleans food culture");
            
            JsonArray takeHomeMemories = new JsonArray();
            takeHomeMemories.add("Local spice blends and seasonings for home cooking");
            takeHomeMemories.add("Coffee beans from traditional New Orleans roasters");
            takeHomeMemories.add("Hot sauce varieties unique to Louisiana");
            takeHomeMemories.add("Recipe cards and cooking tips from local chefs");
            takeHomeMemories.add("Photos and stories of authentic dining experiences");
            
            culinaryPlan.add("trip_success_indicators", successIndicators);
            culinaryPlan.add("culinary_memories_to_take_home", takeHomeMemories);
            
            output.add("comprehensive_culinary_plan", culinaryPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning culinary tourism: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
