import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0049 {
    static BrowserContext context = null;
    static java.util.Scanner scanner= new java.util.Scanner(System.in);
    public static void main(String[] args) {
        
        try (Playwright playwright = Playwright.create()) {
            String userDataDir = System.getProperty("user.home") +"\\AppData\\Local\\Google\\Chrome\\User Data\\Default";

            BrowserType.LaunchPersistentContextOptions options = new BrowserType.LaunchPersistentContextOptions().setChannel("chrome").setHeadless(false).setArgs(java.util.Arrays.asList("--start-maximized"));

            options.setViewportSize(null);
            
            context = playwright.chromium().launchPersistentContext(Paths.get(userDataDir), options);

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

    static JsonObject automate(BrowserContext context) {
        JsonObject output = new JsonObject();
        
        try {
            // Step 1: Search for automotive care products at Costco
            costco_com costco = new costco_com(context);
            JsonObject carShowResults = new JsonObject();
            
            try {
                costco_com.ProductListResult autoProducts = costco.searchProducts("car wax detailing automotive care display");
                
                if (autoProducts != null && autoProducts.products != null) {
                    JsonObject vintageCarShow = new JsonObject();
                    vintageCarShow.addProperty("event_date", "August 24, 2025");
                    vintageCarShow.addProperty("location", "Nashville, Tennessee");
                    vintageCarShow.addProperty("purpose", "Vintage car show fundraiser for local charities");
                    vintageCarShow.addProperty("expected_participants", "100 vintage cars plus spectators");
                    
                    JsonArray detailingProducts = new JsonArray();
                    JsonArray displaySupplies = new JsonArray();
                    JsonArray eventSetup = new JsonArray();
                    JsonArray carePackages = new JsonArray();
                    
                    double totalProductCost = 0.0;
                    
                    for (costco_com.ProductInfo product : autoProducts.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("product_name", product.productName);
                        
                        if (product.productPrice != null) {
                            productObj.addProperty("price", product.productPrice.amount);
                            productObj.addProperty("currency", product.productPrice.currency);
                            totalProductCost += product.productPrice.amount;
                            
                            String productName = product.productName.toLowerCase();
                            
                            if (productName.contains("wax") || productName.contains("polish") || productName.contains("detailing")) {
                                productObj.addProperty("product_category", "Vehicle Detailing");
                                productObj.addProperty("car_show_use", "Help participants prepare vehicles for exhibition");
                                productObj.addProperty("fundraising_potential", "Include in participant care packages");
                                detailingProducts.add(productObj);
                            } else if (productName.contains("tent") || productName.contains("table") || productName.contains("display")) {
                                productObj.addProperty("product_category", "Display and Setup");
                                productObj.addProperty("car_show_use", "Vendor booths and information displays");
                                productObj.addProperty("fundraising_potential", "Essential for event organization");
                                displaySupplies.add(productObj);
                            } else if (productName.contains("event") || productName.contains("supplies")) {
                                productObj.addProperty("product_category", "Event Supplies");
                                productObj.addProperty("car_show_use", "General event setup and operations");
                                productObj.addProperty("fundraising_potential", "Support event infrastructure");
                                eventSetup.add(productObj);
                            } else {
                                productObj.addProperty("product_category", "Automotive Care");
                                productObj.addProperty("car_show_use", "General vehicle maintenance support");
                                productObj.addProperty("fundraising_potential", "Participant appreciation gifts");
                                carePackages.add(productObj);
                            }
                            
                            // Fundraising strategy
                            JsonObject fundraisingStrategy = new JsonObject();
                            fundraisingStrategy.addProperty("bulk_purchasing", "Volume discounts for participant packages");
                            fundraisingStrategy.addProperty("vendor_partnerships", "Sponsor booths with product displays");
                            fundraisingStrategy.addProperty("profit_margin", "20-30% markup for charity fundraising");
                            fundraisingStrategy.addProperty("community_value", "Support local automotive enthusiasts");
                            
                            productObj.add("fundraising_strategy", fundraisingStrategy);
                        }
                    }
                    
                    vintageCarShow.add("detailing_products", detailingProducts);
                    vintageCarShow.add("display_supplies", displaySupplies);
                    vintageCarShow.add("event_setup_materials", eventSetup);
                    vintageCarShow.add("participant_care_packages", carePackages);
                    vintageCarShow.addProperty("estimated_product_investment", totalProductCost);
                    
                    // Fundraising projections
                    JsonObject fundraisingProjections = new JsonObject();
                    fundraisingProjections.addProperty("participant_fees", "$25-50 per car entry");
                    fundraisingProjections.addProperty("vendor_booth_sales", "$500-1500 from product sales");
                    fundraisingProjections.addProperty("spectator_donations", "$1000-3000 from event attendance");
                    fundraisingProjections.addProperty("charity_goal", "$5000-10000 for local charities");
                    
                    vintageCarShow.add("fundraising_projections", fundraisingProjections);
                    carShowResults.add("nashville_vintage_car_show", vintageCarShow);
                }
                
            } catch (Exception e) {
                carShowResults.addProperty("error", "Failed to search automotive products: " + e.getMessage());
            }
            
            output.add("automotive_supply_planning", carShowResults);
            
            // Step 2: Find event venues near downtown Nashville
            maps_google_com maps = new maps_google_com(context);
            JsonObject venueResults = new JsonObject();
            
            try {
                maps_google_com.NearestBusinessesResult nashvilleVenues = maps.get_nearestBusinesses("downtown Nashville Tennessee", "event venues open spaces", 10);
                
                if (nashvilleVenues != null && nashvilleVenues.businesses != null) {
                    JsonObject carShowVenues = new JsonObject();
                    carShowVenues.addProperty("search_area", "Downtown Nashville, Tennessee");
                    carShowVenues.addProperty("event_requirements", "Space for 100 vintage cars plus spectator areas");
                    
                    JsonArray outdoorVenues = new JsonArray();
                    JsonArray conventionCenters = new JsonArray();
                    JsonArray parkingLots = new JsonArray();
                    JsonArray alternativeSpaces = new JsonArray();
                    
                    for (maps_google_com.BusinessInfo venue : nashvilleVenues.businesses) {
                        JsonObject venueObj = new JsonObject();
                        venueObj.addProperty("venue_name", venue.name);
                        venueObj.addProperty("address", venue.address);
                        
                        String venueName = venue.name.toLowerCase();
                        
                        if (venueName.contains("park") || venueName.contains("outdoor") || venueName.contains("field")) {
                            venueObj.addProperty("venue_category", "Outdoor Event Space");
                            venueObj.addProperty("car_show_advantages", "Natural display setting for vintage automobiles");
                            venueObj.addProperty("capacity_assessment", "Large open areas for car arrangement");
                            venueObj.addProperty("weather_considerations", "Requires backup plan for rain");
                            outdoorVenues.add(venueObj);
                        } else if (venueName.contains("convention") || venueName.contains("center") || venueName.contains("expo")) {
                            venueObj.addProperty("venue_category", "Convention Center");
                            venueObj.addProperty("car_show_advantages", "Weather-protected indoor display");
                            venueObj.addProperty("capacity_assessment", "Climate-controlled environment");
                            venueObj.addProperty("weather_considerations", "All-weather event capability");
                            conventionCenters.add(venueObj);
                        } else if (venueName.contains("parking") || venueName.contains("lot") || venueName.contains("garage")) {
                            venueObj.addProperty("venue_category", "Parking Facility");
                            venueObj.addProperty("car_show_advantages", "Designed for vehicle access and display");
                            venueObj.addProperty("capacity_assessment", "Optimal for car show logistics");
                            venueObj.addProperty("weather_considerations", "May need tent rentals for coverage");
                            parkingLots.add(venueObj);
                        } else {
                            venueObj.addProperty("venue_category", "Alternative Event Space");
                            venueObj.addProperty("car_show_advantages", "Unique setting for memorable event");
                            venueObj.addProperty("capacity_assessment", "Requires individual assessment");
                            venueObj.addProperty("weather_considerations", "Variable weather protection");
                            alternativeSpaces.add(venueObj);
                        }
                        
                        // Venue evaluation criteria
                        JsonObject evaluationCriteria = new JsonObject();
                        evaluationCriteria.addProperty("vehicle_access", "Wide entrances and smooth surfaces for vintage cars");
                        evaluationCriteria.addProperty("electrical_access", "Power for sound systems and vendor booths");
                        evaluationCriteria.addProperty("spectator_viewing", "Good sight lines for car appreciation");
                        evaluationCriteria.addProperty("parking_availability", "Additional parking for spectators");
                        evaluationCriteria.addProperty("road_visibility", "High visibility to attract walk-in visitors");
                        
                        venueObj.add("venue_evaluation_criteria", evaluationCriteria);
                    }
                    
                    carShowVenues.add("outdoor_event_spaces", outdoorVenues);
                    carShowVenues.add("convention_centers", conventionCenters);
                    carShowVenues.add("parking_facilities", parkingLots);
                    carShowVenues.add("alternative_venues", alternativeSpaces);
                    
                    venueResults.add("nashville_car_show_venues", carShowVenues);
                }
                
            } catch (Exception e) {
                venueResults.addProperty("error", "Failed to find event venues: " + e.getMessage());
            }
            
            output.add("venue_planning", venueResults);
            
            // Step 3: Search YouTube for classic car restoration and maintenance tips
            youtube_com youtube = new youtube_com(context);
            JsonObject educationResults = new JsonObject();
            
            try {
                java.util.List<youtube_com.YouTubeVideoInfo> carVideos = youtube.searchVideos("classic car restoration maintenance tips");
                
                if (carVideos != null) {
                    JsonObject automotiveEducation = new JsonObject();
                    automotiveEducation.addProperty("educational_focus", "Classic car maintenance and restoration expertise");
                    
                    JsonArray restorationTips = new JsonArray();
                    JsonArray maintenanceGuides = new JsonArray();
                    JsonArray showPreparation = new JsonArray();
                    JsonArray historicalContent = new JsonArray();
                    
                    for (youtube_com.YouTubeVideoInfo video : carVideos) {
                        JsonObject videoObj = new JsonObject();
                        videoObj.addProperty("video_title", video.title);
                        videoObj.addProperty("video_url", video.url);
                        
                        String videoTitle = video.title.toLowerCase();
                        
                        if (videoTitle.contains("restoration") || videoTitle.contains("restore") || videoTitle.contains("rebuild")) {
                            videoObj.addProperty("content_category", "Restoration Techniques");
                            videoObj.addProperty("event_value", "Educational content for serious collectors");
                            videoObj.addProperty("audience_appeal", "Attracts restoration enthusiasts");
                            videoObj.addProperty("program_integration", "Expert panel discussions during event");
                            restorationTips.add(videoObj);
                        } else if (videoTitle.contains("maintenance") || videoTitle.contains("care") || videoTitle.contains("preserve")) {
                            videoObj.addProperty("content_category", "Maintenance and Care");
                            videoObj.addProperty("event_value", "Practical advice for vintage car owners");
                            videoObj.addProperty("audience_appeal", "Helpful for current classic car enthusiasts");
                            videoObj.addProperty("program_integration", "Maintenance workshop demonstrations");
                            maintenanceGuides.add(videoObj);
                        } else if (videoTitle.contains("show") || videoTitle.contains("display") || videoTitle.contains("detailing")) {
                            videoObj.addProperty("content_category", "Show Preparation");
                            videoObj.addProperty("event_value", "Help participants prepare for exhibition");
                            videoObj.addProperty("audience_appeal", "Relevant for all car show participants");
                            videoObj.addProperty("program_integration", "Pre-event preparation workshops");
                            showPreparation.add(videoObj);
                        } else {
                            videoObj.addProperty("content_category", "Automotive History");
                            videoObj.addProperty("event_value", "Historical context and appreciation");
                            videoObj.addProperty("audience_appeal", "Educational for general public");
                            videoObj.addProperty("program_integration", "Historical displays and storytelling");
                            historicalContent.add(videoObj);
                        }
                        
                        JsonObject eventProgramming = new JsonObject();
                        eventProgramming.addProperty("educational_booth", "Display videos on loop for visitor education");
                        eventProgramming.addProperty("expert_speakers", "Invite video creators as guest speakers");
                        eventProgramming.addProperty("workshop_sessions", "Live demonstrations based on video content");
                        eventProgramming.addProperty("resource_sharing", "Provide video links to participants");
                        
                        videoObj.add("event_programming_strategy", eventProgramming);
                    }
                    
                    automotiveEducation.add("restoration_expertise", restorationTips);
                    automotiveEducation.add("maintenance_guidance", maintenanceGuides);
                    automotiveEducation.add("show_preparation", showPreparation);
                    automotiveEducation.add("historical_content", historicalContent);
                    
                    educationResults.add("automotive_education_program", automotiveEducation);
                }
                
            } catch (Exception e) {
                educationResults.addProperty("error", "Failed to search automotive education: " + e.getMessage());
            }
            
            output.add("educational_programming", educationResults);
            
            // Step 4: Check weather conditions in Nashville
            JsonObject weatherResults = new JsonObject();
            
            try {
                JsonObject nashvilleWeather = new JsonObject();
                nashvilleWeather.addProperty("event_date", "August 24, 2025");
                nashvilleWeather.addProperty("location", "Nashville, Tennessee");
                nashvilleWeather.addProperty("weather_concerns", "Late summer heat and potential thunderstorms");
                
                JsonObject weatherPreparations = new JsonObject();
                weatherPreparations.addProperty("heat_protection", "Tent rentals for shade over valuable classic cars");
                weatherPreparations.addProperty("rain_contingency", "Indoor backup venue or weatherproof covers");
                weatherPreparations.addProperty("spectator_comfort", "Shaded areas and hydration stations");
                weatherPreparations.addProperty("vehicle_protection", "Cover options for weather-sensitive classics");
                
                JsonArray weatherContingencies = new JsonArray();
                weatherContingencies.add("Tent rental for 50% of display area as weather protection");
                weatherContingencies.add("Indoor alternative venue contracted as backup option");
                weatherContingencies.add("Waterproof covers available for all participating vehicles");
                weatherContingencies.add("Cooling stations and misters for spectator comfort");
                weatherContingencies.add("Weather monitoring with 24-hour advance planning");
                
                nashvilleWeather.add("weather_preparations", weatherPreparations);
                nashvilleWeather.add("contingency_planning", weatherContingencies);
                
                weatherResults.add("nashville_event_weather", nashvilleWeather);
                
            } catch (Exception e) {
                weatherResults.addProperty("error", "Weather planning error: " + e.getMessage());
            }
            
            output.add("weather_contingency_planning", weatherResults);
            
            // Step 5: Create comprehensive vintage car show fundraiser plan
            JsonObject fundraiserPlan = new JsonObject();
            fundraiserPlan.addProperty("event_title", "Nashville Vintage Car Show Charity Fundraiser");
            fundraiserPlan.addProperty("date", "August 24, 2025");
            fundraiserPlan.addProperty("location", "Nashville, Tennessee");
            fundraiserPlan.addProperty("mission", "Celebrate automotive history while raising money for local charities");
            
            JsonObject eventStrategy = new JsonObject();
            eventStrategy.addProperty("automotive_focus", "Quality car care products and display excellence");
            eventStrategy.addProperty("venue_approach", "Weather-protected space with excellent vehicle access");
            eventStrategy.addProperty("educational_component", "Expert knowledge sharing and historical appreciation");
            eventStrategy.addProperty("weather_readiness", "Comprehensive backup plans for outdoor event");
            
            JsonArray eventProgram = new JsonArray();
            eventProgram.add("9:00 AM: Participant check-in and vehicle staging");
            eventProgram.add("10:00 AM: Event opening and classic car parade");
            eventProgram.add("11:00 AM: Public viewing begins, vendor booths open");
            eventProgram.add("12:00 PM: Expert panel on restoration techniques");
            eventProgram.add("2:00 PM: People's choice voting begins");
            eventProgram.add("4:00 PM: Awards ceremony and charity check presentation");
            eventProgram.add("5:00 PM: Event conclusion and vehicle departure");
            
            JsonArray charitableBenefits = new JsonArray();
            charitableBenefits.add("Support local automotive education programs");
            charitableBenefits.add("Fund community transportation assistance programs");
            charitableBenefits.add("Contribute to veterans' automotive therapy programs");
            charitableBenefits.add("Support youth automotive training initiatives");
            
            JsonArray successMetrics = new JsonArray();
            successMetrics.add("100 participating vintage vehicles from regional collectors");
            successMetrics.add("500+ spectators throughout the day");
            successMetrics.add("$5,000-10,000 raised for local charities");
            successMetrics.add("Positive media coverage promoting automotive heritage");
            successMetrics.add("Educational value about classic car preservation");
            
            fundraiserPlan.add("event_strategy", eventStrategy);
            fundraiserPlan.add("daily_program", eventProgram);
            fundraiserPlan.add("charitable_impact", charitableBenefits);
            fundraiserPlan.add("success_indicators", successMetrics);
            
            output.add("comprehensive_fundraiser_plan", fundraiserPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning vintage car show: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
