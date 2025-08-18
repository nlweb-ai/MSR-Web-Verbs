import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0017 {
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
        
        // 1. Search for apartments in Phoenix, Arizona with rent between $1500-$2500
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult apartmentResults = redfin.searchApartments("Phoenix, Arizona", 1500, 2500);
        
        JsonObject realEstateInfo = new JsonObject();
        realEstateInfo.addProperty("location", "Phoenix, Arizona");
        realEstateInfo.addProperty("minRent", 1500);
        realEstateInfo.addProperty("maxRent", 2500);
        realEstateInfo.addProperty("purpose", "Investment opportunity analysis for local rental market");
        
        if (apartmentResults.error != null) {
            realEstateInfo.addProperty("error", apartmentResults.error);
        }
        
        JsonArray apartmentsArray = new JsonArray();
        double totalRent = 0.0;
        double minRent = Double.MAX_VALUE;
        double maxRent = 0.0;
        int validRentPrices = 0;
        
        for (redfin_com.ApartmentInfo apartment : apartmentResults.apartments) {
            JsonObject apartmentObj = new JsonObject();
            apartmentObj.addProperty("address", apartment.address);
            apartmentObj.addProperty("url", apartment.url);
            
            if (apartment.price != null) {
                apartmentObj.addProperty("monthlyRent", apartment.price.amount);
                apartmentObj.addProperty("currency", apartment.price.currency);
                
                // Estimate cost per square foot (assuming average 1000 sq ft)
                double estimatedCostPerSqFt = apartment.price.amount / 1000.0;
                apartmentObj.addProperty("estimatedCostPerSqFt", Math.round(estimatedCostPerSqFt * 100.0) / 100.0);
                
                // Investment potential assessment
                String investmentPotential;
                if (apartment.price.amount <= 1700) {
                    investmentPotential = "High ROI potential - Below market average, good for cash flow";
                } else if (apartment.price.amount <= 2200) {
                    investmentPotential = "Moderate ROI - Market rate pricing, stable investment";
                } else {
                    investmentPotential = "Premium market - High-end properties, appreciation focus";
                }
                apartmentObj.addProperty("investmentAssessment", investmentPotential);
                
                // Neighborhood analysis based on address
                String neighborhood = analyzeNeighborhood(apartment.address);
                apartmentObj.addProperty("neighborhoodPotential", neighborhood);
                
                totalRent += apartment.price.amount;
                validRentPrices++;
                minRent = Math.min(minRent, apartment.price.amount);
                maxRent = Math.max(maxRent, apartment.price.amount);
            } else {
                apartmentObj.addProperty("monthlyRent", (String) null);
                apartmentObj.addProperty("currency", (String) null);
                apartmentObj.addProperty("investmentAssessment", "Pricing data not available");
            }
            
            apartmentsArray.add(apartmentObj);
        }
        
        realEstateInfo.add("apartments", apartmentsArray);
        
        // Market analysis
        JsonObject marketAnalysis = new JsonObject();
        marketAnalysis.addProperty("totalPropertiesAnalyzed", apartmentResults.apartments.size());
        if (validRentPrices > 0) {
            double avgRent = totalRent / validRentPrices;
            double avgCostPerSqFt = avgRent / 1000.0; // Assuming 1000 sq ft average
            
            marketAnalysis.addProperty("averageMonthlyRent", Math.round(avgRent * 100.0) / 100.0);
            marketAnalysis.addProperty("minRentFound", Math.round(minRent * 100.0) / 100.0);
            marketAnalysis.addProperty("maxRentFound", Math.round(maxRent * 100.0) / 100.0);
            marketAnalysis.addProperty("averageCostPerSqFt", Math.round(avgCostPerSqFt * 100.0) / 100.0);
            marketAnalysis.addProperty("annualRentRevenue", Math.round(avgRent * 12 * 100.0) / 100.0);
            
            // Investment recommendations
            JsonArray investmentTips = new JsonArray();
            investmentTips.add("Focus on properties below $" + Math.round(avgRent) + " for better cash flow");
            investmentTips.add("Consider neighborhoods with growing tech employment");
            investmentTips.add("Factor in Phoenix's population growth and business expansion");
            investmentTips.add("Account for seasonal demand fluctuations due to climate");
            
            marketAnalysis.add("investmentRecommendations", investmentTips);
        }
        
        realEstateInfo.add("marketAnalysis", marketAnalysis);
        result.add("realEstateInvestment", realEstateInfo);
        
        // 2. Get NASA's Near Earth Object data for August 8th, 2025
        try {
            Nasa nasa = new Nasa();
            java.util.List<Nasa.NeoResult> neoData = nasa.getNeoFeed("2025-08-08", "2025-08-08");
            
            JsonObject spaceIndustryInfo = new JsonObject();
            spaceIndustryInfo.addProperty("date", "2025-08-08");
            spaceIndustryInfo.addProperty("purpose", "Space industry monitoring for Phoenix aerospace sector investment");
            spaceIndustryInfo.addProperty("significance", "Phoenix has growing aerospace and defense industry presence");
            
            JsonArray neoArray = new JsonArray();
            for (Nasa.NeoResult neo : neoData) {
                JsonObject neoObj = new JsonObject();
                neoObj.addProperty("name", neo.name);
                neoObj.addProperty("id", neo.id);
                if (neo.closeApproachDate != null) {
                    neoObj.addProperty("closeApproachDate", neo.closeApproachDate.toString());
                }
                if (neo.estimatedDiameterKm != null) {
                    neoObj.addProperty("estimatedDiameterKm", neo.estimatedDiameterKm);
                }
                if (neo.missDistance != null) {
                    neoObj.addProperty("missDistanceKm", neo.missDistance.amount);
                }
                neoArray.add(neoObj);
            }
            
            spaceIndustryInfo.add("nearEarthObjects", neoArray);
            spaceIndustryInfo.addProperty("totalObjects", neoData.size());
            
            // Phoenix aerospace sector context
            JsonObject aerospaceContext = new JsonObject();
            aerospaceContext.addProperty("industryPresence", "Major aerospace companies including Boeing, Lockheed Martin, and Honeywell");
            aerospaceContext.addProperty("investmentImplication", "Growing space industry supports high-tech job market and property demand");
            aerospaceContext.addProperty("economicImpact", "Aerospace sector contributes significantly to Phoenix metro area employment");
            
            spaceIndustryInfo.add("phoenixAerospaceContext", aerospaceContext);
            result.add("spaceIndustryData", spaceIndustryInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject spaceError = new JsonObject();
            spaceError.addProperty("error", "Failed to get NEO data: " + e.getMessage());
            spaceError.addProperty("date", "2025-08-08");
            result.add("spaceIndustryData", spaceError);
        }
        
        // 3. Check current weather in Phoenix
        try {
            OpenWeather weather = new OpenWeather();
            // Phoenix, Arizona coordinates
            double phoenixLat = 33.4484;
            double phoenixLon = -112.0740;
            
            OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(phoenixLat, phoenixLon);
            
            JsonObject weatherInfo = new JsonObject();
            weatherInfo.addProperty("cityName", currentWeather.getCityName());
            weatherInfo.addProperty("country", currentWeather.getCountry());
            weatherInfo.addProperty("date", currentWeather.getDate().toString());
            weatherInfo.addProperty("condition", currentWeather.getCondition());
            weatherInfo.addProperty("description", currentWeather.getDescription());
            weatherInfo.addProperty("temperature", Math.round(currentWeather.getTemperature() * 100.0) / 100.0);
            weatherInfo.addProperty("feelsLike", Math.round(currentWeather.getFeelsLike() * 100.0) / 100.0);
            weatherInfo.addProperty("humidity", currentWeather.getHumidity());
            weatherInfo.addProperty("windSpeed", Math.round(currentWeather.getWindSpeed() * 100.0) / 100.0);
            
            // Investment-focused climate analysis
            String climateImpact;
            double temp = currentWeather.getTemperature();
            if (temp > 40) {
                climateImpact = "Extreme heat - High AC costs, impacts property maintenance and resident comfort";
            } else if (temp > 35) {
                climateImpact = "Very hot - Significant cooling costs, desert climate attracts winter residents";
            } else if (temp > 25) {
                climateImpact = "Warm and pleasant - Attractive to residents, moderate utility costs";
            } else {
                climateImpact = "Mild temperatures - Peak season for Phoenix, high rental demand";
            }
            
            // Property maintenance implications
            JsonObject maintenanceImplications = new JsonObject();
            maintenanceImplications.addProperty("coolingCosts", temp > 35 ? "High" : temp > 25 ? "Moderate" : "Low");
            maintenanceImplications.addProperty("climateWear", "Desert conditions require UV-resistant materials and regular maintenance");
            maintenanceImplications.addProperty("seasonalDemand", "Peak rental season October-April due to pleasant winter weather");
            maintenanceImplications.addProperty("utilityConsiderations", "High summer electricity costs affect tenant satisfaction");
            
            weatherInfo.addProperty("investmentClimateImpact", climateImpact);
            weatherInfo.add("propertyMaintenanceFactors", maintenanceImplications);
            
            result.add("phoenixClimate", weatherInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject weatherError = new JsonObject();
            weatherError.addProperty("error", "Failed to get weather data: " + e.getMessage());
            result.add("phoenixClimate", weatherError);
        }
        
        // 4. Find technology companies near downtown Phoenix
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult techCompanies = maps.get_nearestBusinesses(
            "downtown Phoenix, Arizona", "technology company", 12);
        
        JsonObject economicAnalysisInfo = new JsonObject();
        economicAnalysisInfo.addProperty("searchArea", "downtown Phoenix, Arizona");
        economicAnalysisInfo.addProperty("businessType", "Technology companies");
        economicAnalysisInfo.addProperty("purpose", "Assess local job market and economic growth potential");
        
        JsonArray techCompaniesArray = new JsonArray();
        for (maps_google_com.BusinessInfo company : techCompanies.businesses) {
            JsonObject companyObj = new JsonObject();
            companyObj.addProperty("name", company.name);
            companyObj.addProperty("address", company.address);
            
            // Assess economic impact based on company type
            String economicImpact = assessTechCompanyImpact(company.name);
            companyObj.addProperty("economicImpact", economicImpact);
            
            techCompaniesArray.add(companyObj);
        }
        
        economicAnalysisInfo.add("technologyCompanies", techCompaniesArray);
        economicAnalysisInfo.addProperty("totalCompaniesFound", techCompanies.businesses.size());
        
        // Economic growth assessment
        JsonObject growthAssessment = new JsonObject();
        growthAssessment.addProperty("techSectorPresence", techCompanies.businesses.size() > 8 ? "Strong" : 
                                   techCompanies.businesses.size() > 4 ? "Moderate" : "Developing");
        growthAssessment.addProperty("employmentPotential", "Tech sector growth supports high-income rental demand");
        growthAssessment.addProperty("propertyValueImpact", "Technology companies drive gentrification and property appreciation");
        
        JsonArray economicIndicators = new JsonArray();
        economicIndicators.add("Phoenix is a major tech hub with growing startup ecosystem");
        economicIndicators.add("Major corporations relocating operations to Phoenix metro area");
        economicIndicators.add("Lower cost of living attracts tech workers from California");
        economicIndicators.add("State government incentives support technology sector growth");
        
        growthAssessment.add("keyEconomicIndicators", economicIndicators);
        
        economicAnalysisInfo.add("economicGrowthAssessment", growthAssessment);
        result.add("economicAnalysis", economicAnalysisInfo);
        
        // 5. Investment opportunity summary
        JsonObject investmentSummary = new JsonObject();
        investmentSummary.addProperty("location", "Phoenix, Arizona");
        investmentSummary.addProperty("investmentFocus", "Rental real estate in growing tech market");
        investmentSummary.addProperty("targetRentRange", "$1500-$2500");
        
        JsonArray opportunityFactors = new JsonArray();
        opportunityFactors.add("Growing aerospace and technology sectors provide stable employment");
        opportunityFactors.add("Population growth and business relocations increase housing demand");
        opportunityFactors.add("Favorable climate attracts seasonal residents and retirees");
        opportunityFactors.add("Lower property costs compared to California markets");
        opportunityFactors.add("Strong rental yields in desirable neighborhoods");
        
        JsonArray riskFactors = new JsonArray();
        riskFactors.add("Extreme summer heat increases utility costs and maintenance needs");
        riskFactors.add("Seasonal demand fluctuations affect rental stability");
        riskFactors.add("Competition from new construction developments");
        riskFactors.add("Water rights and drought concerns for long-term sustainability");
        
        investmentSummary.add("opportunityFactors", opportunityFactors);
        investmentSummary.add("riskFactors", riskFactors);
        
        JsonArray nextSteps = new JsonArray();
        nextSteps.add("Focus on properties in tech-corridor neighborhoods");
        nextSteps.add("Research specific school districts and amenities");
        nextSteps.add("Analyze seasonal rental patterns and pricing strategies");
        nextSteps.add("Consider partnerships with local property management companies");
        nextSteps.add("Evaluate financing options and cash flow projections");
        
        investmentSummary.add("recommendedNextSteps", nextSteps);
        result.add("investmentSummary", investmentSummary);
        
        return result;
    }
    
    // Helper method to analyze neighborhood potential
    private static String analyzeNeighborhood(String address) {
        String addressLower = address.toLowerCase();
        
        if (addressLower.contains("scottsdale") || addressLower.contains("tempe")) {
            return "Premium area - High appreciation potential, affluent demographics";
        } else if (addressLower.contains("downtown") || addressLower.contains("central")) {
            return "Urban core - Gentrification area, good for young professionals";
        } else if (addressLower.contains("north") || addressLower.contains("carefree")) {
            return "Upscale suburban - Family-oriented, stable rental demand";
        } else if (addressLower.contains("mesa") || addressLower.contains("chandler")) {
            return "Growing suburbs - Tech corridor, good employment access";
        } else {
            return "Developing area - Research local amenities and growth plans";
        }
    }
    
    // Helper method to assess tech company economic impact
    private static String assessTechCompanyImpact(String companyName) {
        String nameLower = companyName.toLowerCase();
        
        if (nameLower.contains("software") || nameLower.contains("tech") || nameLower.contains("data")) {
            return "High-paying tech jobs - Drives demand for quality rental properties";
        } else if (nameLower.contains("startup") || nameLower.contains("innovation")) {
            return "Emerging growth potential - Early-stage but promising for future development";
        } else if (nameLower.contains("consulting") || nameLower.contains("services")) {
            return "Professional services - Stable employment base for rental market";
        } else {
            return "General business sector - Contributes to local economic diversity";
        }
    }
}
