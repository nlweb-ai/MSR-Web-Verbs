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


public class Task0097 {
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
        
        // Food truck business details
        LocalDate startDate = LocalDate.of(2025, 8, 24);
        String businessLocation = "Austin, Texas";
        double housingBudgetMin = 1000.0;
        double housingBudgetMax = 1800.0;
        
        // Step 1: Search for commercial kitchen equipment and food service supplies at Costco
        costco_com costco = new costco_com(context);
        String[] kitchenEquipment = {"commercial grill", "food truck equipment", "refrigeration", "food service supplies"};
        
        JsonObject equipmentInfo = new JsonObject();
        JsonArray equipmentArray = new JsonArray();
        double totalStartupCost = 0.0;
        
        for (String equipment : kitchenEquipment) {
            costco_com.ProductInfo productResult = costco.searchProduct(equipment);
            JsonObject equipmentObj = new JsonObject();
            equipmentObj.addProperty("equipment_type", equipment);
            
            if (productResult.error != null) {
                equipmentObj.addProperty("error", productResult.error);
                double estimatedCost = getEstimatedEquipmentCost(equipment);
                equipmentObj.addProperty("estimated_cost", estimatedCost);
                totalStartupCost += estimatedCost;
            } else {
                equipmentObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    equipmentObj.addProperty("cost", productResult.productPrice.amount);
                    equipmentObj.addProperty("currency", productResult.productPrice.currency);
                    totalStartupCost += productResult.productPrice.amount;
                } else {
                    double estimatedCost = getEstimatedEquipmentCost(equipment);
                    equipmentObj.addProperty("estimated_cost", estimatedCost);
                    totalStartupCost += estimatedCost;
                }
            }
            equipmentArray.add(equipmentObj);
        }
        
        // Add additional startup costs (truck, permits, insurance, initial inventory)
        double additionalCosts = 45000.0; // Estimated for truck purchase, permits, insurance, initial inventory
        double totalInitialInvestment = totalStartupCost + additionalCosts;
        
        equipmentInfo.add("kitchen_equipment", equipmentArray);
        equipmentInfo.addProperty("equipment_costs", totalStartupCost);
        equipmentInfo.addProperty("additional_startup_costs", additionalCosts);
        equipmentInfo.addProperty("total_initial_investment", totalInitialInvestment);
        equipmentInfo.addProperty("additional_costs_breakdown", "Food truck purchase/lease, permits, insurance, initial inventory");
        result.add("startup_cost_analysis", equipmentInfo);
        
        // Step 2: Find food truck parking areas and busy commercial districts near downtown Austin
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "downtown Austin, Texas";
        String businessDescription = "food truck parking commercial districts busy areas";
        int maxLocations = 15;
        
        maps_google_com.NearestBusinessesResult locationsResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxLocations);
        
        JsonObject businessLocationsInfo = new JsonObject();
        businessLocationsInfo.addProperty("reference_point", locationsResult.referencePoint);
        businessLocationsInfo.addProperty("search_type", locationsResult.businessDescription);
        businessLocationsInfo.addProperty("purpose", "Identify high-traffic areas for food truck positioning");
        
        JsonArray locationsArray = new JsonArray();
        for (maps_google_com.BusinessInfo location : locationsResult.businesses) {
            JsonObject locationObj = new JsonObject();
            locationObj.addProperty("name", location.name);
            locationObj.addProperty("address", location.address);
            
            // Categorize location type based on name
            String locationName = location.name.toLowerCase();
            String locationType = "other";
            if (locationName.contains("food truck") || locationName.contains("parking")) {
                locationType = "food_truck_area";
            } else if (locationName.contains("district") || locationName.contains("plaza") || locationName.contains("market")) {
                locationType = "commercial_district";
            } else if (locationName.contains("office") || locationName.contains("business")) {
                locationType = "business_area";
            } else if (locationName.contains("park") || locationName.contains("festival")) {
                locationType = "event_area";
            }
            
            locationObj.addProperty("location_type", locationType);
            locationObj.addProperty("traffic_potential", assessTrafficPotential(locationName));
            locationsArray.add(locationObj);
        }
        businessLocationsInfo.add("potential_locations", locationsArray);
        businessLocationsInfo.addProperty("total_locations_found", locationsArray.size());
        result.add("business_locations", businessLocationsInfo);
        
        // Step 3: Search for apartments in Austin between $1000-$1800
        booking_com booking = new booking_com(context);
        String housingSearch = "Austin apartments " + (int)housingBudgetMin + " " + (int)housingBudgetMax;
        booking_com.HotelSearchResult housingResult = booking.search_hotel(housingSearch, startDate, startDate.plusDays(30));
        
        JsonObject housingInfo = new JsonObject();
        housingInfo.addProperty("search_location", businessLocation);
        housingInfo.addProperty("budget_range_min", housingBudgetMin);
        housingInfo.addProperty("budget_range_max", housingBudgetMax);
        housingInfo.addProperty("purpose", "Find affordable housing near business areas");
        
        JsonArray housingArray = new JsonArray();
        double averageRent = 0.0;
        int validHousing = 0;
        
        for (booking_com.HotelInfo housing : housingResult.hotels) {
            JsonObject housingObj = new JsonObject();
            housingObj.addProperty("property_name", housing.hotelName);
            
            if (housing.price != null) {
                double monthlyRate = housing.price.amount * 30; // Convert daily to monthly estimate
                if (monthlyRate >= housingBudgetMin && monthlyRate <= housingBudgetMax) {
                    housingObj.addProperty("estimated_monthly_rent", monthlyRate);
                    housingObj.addProperty("currency", housing.price.currency);
                    housingObj.addProperty("within_budget", true);
                    averageRent += monthlyRate;
                    validHousing++;
                } else {
                    housingObj.addProperty("estimated_monthly_rent", monthlyRate);
                    housingObj.addProperty("within_budget", false);
                }
            } else {
                housingObj.addProperty("estimated_monthly_rent", "Price not available");
                housingObj.addProperty("within_budget", "Unknown");
            }
            housingArray.add(housingObj);
        }
        
        if (validHousing > 0) {
            averageRent = averageRent / validHousing;
        } else {
            averageRent = 1400.0; // Austin average within budget range
        }
        
        housingInfo.add("housing_options", housingArray);
        housingInfo.addProperty("average_rent_in_budget", averageRent);
        housingInfo.addProperty("affordable_options_found", validHousing);
        result.add("housing_information", housingInfo);
        
        // Step 4: Look up food truck and restaurant business books in OpenLibrary
        OpenLibrary openLibrary = new OpenLibrary();
        JsonObject businessEducationInfo = new JsonObject();
        
        try {
            String[] businessTopics = {"food truck business", "restaurant management", "small business regulations", "food service permits"};
            JsonArray booksArray = new JsonArray();
            
            for (String topic : businessTopics) {
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
            
            businessEducationInfo.addProperty("purpose", "Learn regulations, permits, and successful business strategies");
            businessEducationInfo.add("business_education_categories", booksArray);
            
            // Get additional food service subjects
            List<OpenLibrary.SubjectInfo> foodServiceSubjects = openLibrary.getSubject("food service", false, 5, 0);
            JsonArray subjectsArray = new JsonArray();
            for (OpenLibrary.SubjectInfo subject : foodServiceSubjects) {
                subjectsArray.add(subject.info);
            }
            businessEducationInfo.add("related_food_service_subjects", subjectsArray);
            
        } catch (IOException | InterruptedException e) {
            businessEducationInfo.addProperty("error", "Failed to fetch business education materials: " + e.getMessage());
            businessEducationInfo.addProperty("recommendation", "Research food truck regulations and business strategies manually");
        }
        
        result.add("business_education", businessEducationInfo);
        
        // Food truck business summary and recommendations
        JsonObject businessSummary = new JsonObject();
        businessSummary.addProperty("business_type", "Mobile Food Truck Business");
        businessSummary.addProperty("location", businessLocation);
        businessSummary.addProperty("launch_date", startDate.toString());
        businessSummary.addProperty("total_initial_investment", totalInitialInvestment);
        businessSummary.addProperty("potential_locations_identified", locationsArray.size());
        businessSummary.addProperty("average_housing_cost", averageRent);
        
        // Calculate monthly operating costs and break-even analysis
        double monthlyOperatingCosts = averageRent + 2000.0 + 1500.0 + 500.0; // Rent + insurance + supplies + fuel
        double averageSalePerCustomer = 12.0;
        int dailyCustomersNeeded = (int) Math.ceil(monthlyOperatingCosts / 30 / averageSalePerCustomer);
        
        businessSummary.addProperty("estimated_monthly_operating_costs", monthlyOperatingCosts);
        businessSummary.addProperty("daily_customers_needed_for_break_even", dailyCustomersNeeded);
        businessSummary.addProperty("average_sale_per_customer", averageSalePerCustomer);
        
        // Business recommendations
        StringBuilder recommendations = new StringBuilder();
        recommendations.append("Austin's vibrant food scene and food truck culture make it ideal for mobile food business. ");
        
        if (locationsArray.size() >= 12) {
            recommendations.append("Excellent variety of high-traffic locations available for rotation. ");
        } else {
            recommendations.append("Limited location options found - research additional food truck-friendly areas. ");
        }
        
        if (averageRent < 1500) {
            recommendations.append("Housing costs are reasonable, allowing more capital for business investment. ");
        } else {
            recommendations.append("Housing costs are higher - consider locations further from downtown to reduce overhead. ");
        }
        
        if (totalInitialInvestment > 60000) {
            recommendations.append("High startup costs - consider used equipment or leasing options to reduce initial investment. ");
        } else {
            recommendations.append("Reasonable startup costs - budget allows for quality equipment and proper setup. ");
        }
        
        recommendations.append("Focus on obtaining proper permits and building relationships with location managers. ");
        recommendations.append("Develop unique menu items that travel well and can be prepared quickly.");
        
        businessSummary.addProperty("business_recommendations", recommendations.toString());
        
        // Business strategy and planning
        JsonObject businessStrategy = new JsonObject();
        businessStrategy.addProperty("target_market", "Office workers, college students, festival-goers, late-night crowd");
        businessStrategy.addProperty("competitive_advantages", "Mobility, lower overhead than restaurants, direct customer interaction");
        businessStrategy.addProperty("revenue_streams", "Daily lunch service, catering events, festival participation");
        
        JsonArray permitRequirements = new JsonArray();
        permitRequirements.add("Mobile food vendor permit");
        permitRequirements.add("Health department food handler's license");
        permitRequirements.add("Business license and tax registration");
        permitRequirements.add("Fire department approval for equipment");
        businessStrategy.add("required_permits", permitRequirements);
        
        JsonArray successFactors = new JsonArray();
        successFactors.add("Consistent quality and fast service");
        successFactors.add("Strategic location rotation based on traffic patterns");
        successFactors.add("Strong social media presence for location updates");
        successFactors.add("Building regular customer base and repeat business");
        businessStrategy.add("success_factors", successFactors);
        
        businessSummary.add("business_strategy", businessStrategy);
        
        // Financial projections
        JsonObject financialProjections = new JsonObject();
        financialProjections.addProperty("startup_investment", totalInitialInvestment);
        financialProjections.addProperty("monthly_operating_costs", monthlyOperatingCosts);
        financialProjections.addProperty("break_even_daily_sales", dailyCustomersNeeded * averageSalePerCustomer);
        financialProjections.addProperty("projected_monthly_revenue_at_break_even", monthlyOperatingCosts);
        
        // Conservative profit projection (20% above break-even)
        double projectedMonthlyProfit = monthlyOperatingCosts * 0.2;
        financialProjections.addProperty("conservative_monthly_profit_projection", projectedMonthlyProfit);
        financialProjections.addProperty("roi_timeline_months", Math.ceil(totalInitialInvestment / projectedMonthlyProfit));
        
        businessSummary.add("financial_projections", financialProjections);
        
        result.add("food_truck_business_summary", businessSummary);
        
        return result;
    }
    
    // Helper method to estimate equipment costs when Costco search fails
    private static double getEstimatedEquipmentCost(String equipment) {
        switch (equipment.toLowerCase()) {
            case "commercial grill":
                return 2500.0;
            case "food truck equipment":
                return 8000.0;
            case "refrigeration":
                return 3000.0;
            case "food service supplies":
                return 1500.0;
            default:
                return 2000.0;
        }
    }
    
    // Helper method to assess traffic potential of locations
    private static String assessTrafficPotential(String locationName) {
        if (locationName.contains("downtown") || locationName.contains("office") || locationName.contains("business")) {
            return "high";
        } else if (locationName.contains("district") || locationName.contains("plaza") || locationName.contains("center")) {
            return "medium";
        } else {
            return "low";
        }
    }
}
