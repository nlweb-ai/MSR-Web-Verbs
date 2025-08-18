import java.io.IOException;
import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0019 {
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
        
        // 1. Clear the shopping cart on Amazon to start fresh
        amazon_com amazon = new amazon_com(context);
        amazon.clearCart();
        
        JsonObject cartStatusInfo = new JsonObject();
        cartStatusInfo.addProperty("purpose", "Clear previous items to start fresh fitness business equipment selection");
        cartStatusInfo.addProperty("clearingStatus", "Successfully cleared");
        cartStatusInfo.addProperty("businessPreparation", "Cart ready for professional fitness equipment procurement");
        
        result.add("cartPreparation", cartStatusInfo);
        
        // 2. Search for fitness training videos on YouTube
        youtube_com youtube = new youtube_com(context);
        List<youtube_com.YouTubeVideoInfo> fitnessVideos = youtube.searchVideos("fitness training videos");
        
        JsonObject trainingContentInfo = new JsonObject();
        trainingContentInfo.addProperty("searchTerm", "fitness training videos");
        trainingContentInfo.addProperty("purpose", "Research professional content for fitness coaching business development");
        trainingContentInfo.addProperty("businessApplication", "Study successful training methodologies and video production techniques");
        
        JsonArray videosArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : fitnessVideos) {
            JsonObject videoObj = new JsonObject();
            videoObj.addProperty("title", video.title);
            videoObj.addProperty("duration", video.length.toString());
            videoObj.addProperty("url", video.url);
            
            // Business analysis of video content
            String contentAnalysis = analyzeVideoContent(video.title);
            videoObj.addProperty("businessValue", contentAnalysis);
            
            videosArray.add(videoObj);
        }
        
        trainingContentInfo.add("videos", videosArray);
        
        // Content analysis for business development
        JsonObject contentStrategy = new JsonObject();
        contentStrategy.addProperty("marketResearch", "Analyze popular fitness content to identify trends and gaps");
        contentStrategy.addProperty("competitorAnalysis", "Study successful fitness channels for business insights");
        contentStrategy.addProperty("contentIdeas", "Gather inspiration for original training video concepts");
        contentStrategy.addProperty("productionQuality", "Observe professional video production standards and equipment needs");
        
        JsonArray businessInsights = new JsonArray();
        businessInsights.add("Identify most popular training styles and methodologies");
        businessInsights.add("Analyze video engagement metrics and successful formats");
        businessInsights.add("Study equipment usage patterns in professional videos");
        businessInsights.add("Research target audience preferences and demographics");
        businessInsights.add("Evaluate presentation styles and coaching techniques");
        
        contentStrategy.add("keyResearchFocus", businessInsights);
        trainingContentInfo.add("businessDevelopmentStrategy", contentStrategy);
        
        result.add("trainingContentResearch", trainingContentInfo);
        
        // 3. Check weather conditions in Atlanta, Georgia (using coordinates)
        try {
            OpenWeather weather = new OpenWeather();
            // Atlanta coordinates: 33.7490, -84.3880
            OpenWeather.CurrentWeatherData atlantaWeather = weather.getCurrentWeather(33.7490, -84.3880);
            
            JsonObject weatherInfo = new JsonObject();
            weatherInfo.addProperty("city", atlantaWeather.getCityName());
            weatherInfo.addProperty("country", atlantaWeather.getCountry());
            weatherInfo.addProperty("temperature", atlantaWeather.getTemperature());
            weatherInfo.addProperty("feelsLike", atlantaWeather.getFeelsLike());
            weatherInfo.addProperty("humidity", atlantaWeather.getHumidity());
            weatherInfo.addProperty("description", atlantaWeather.getDescription());
            weatherInfo.addProperty("purpose", "Assess outdoor training conditions for fitness coaching business");
            
            // Business weather impact analysis
            JsonObject businessWeatherImpact = new JsonObject();
            
            // Temperature analysis for fitness business
            String temperatureRecommendation;
            if (atlantaWeather.getTemperature() <= 0) {
                temperatureRecommendation = "Freezing weather - Focus on indoor training programs, heated studio space essential";
            } else if (atlantaWeather.getTemperature() <= 15) {
                temperatureRecommendation = "Cold weather - Indoor training preferred, minimal outdoor activities";
            } else if (atlantaWeather.getTemperature() <= 25) {
                temperatureRecommendation = "Perfect training weather - Optimal for both indoor and outdoor fitness programs";
            } else if (atlantaWeather.getTemperature() <= 32) {
                temperatureRecommendation = "Warm weather - Early morning/evening outdoor sessions, AC costs for indoor space";
            } else {
                temperatureRecommendation = "Hot weather - Prioritize indoor climate-controlled environment, hydration focus";
            }
            
            businessWeatherImpact.addProperty("temperatureAnalysis", temperatureRecommendation);
            
            // Humidity impact on fitness business
            String humidityImpact;
            if (atlantaWeather.getHumidity() >= 70) {
                humidityImpact = "High humidity - Enhanced ventilation needed, dehydration risk management critical";
            } else if (atlantaWeather.getHumidity() >= 50) {
                humidityImpact = "Moderate humidity - Standard ventilation adequate, comfortable training conditions";
            } else {
                humidityImpact = "Low humidity - Minimal ventilation needs, hydration still important";
            }
            
            businessWeatherImpact.addProperty("humidityConsiderations", humidityImpact);
            
            // Seasonal business planning
            JsonArray seasonalRecommendations = new JsonArray();
            seasonalRecommendations.add("Winter: Focus on indoor strength training and heated studio classes");
            seasonalRecommendations.add("Spring: Transition to outdoor boot camps and group fitness");
            seasonalRecommendations.add("Summer: Early morning outdoor sessions, indoor evening classes");
            seasonalRecommendations.add("Fall: Peak outdoor training season, moderate temperature ideal");
            
            businessWeatherImpact.add("seasonalBusinessStrategy", seasonalRecommendations);
            
            weatherInfo.add("fitnessBusinessImpact", businessWeatherImpact);
            
            result.add("atlantaWeather", weatherInfo);
        } catch (IOException | InterruptedException e) {
            JsonObject weatherError = new JsonObject();
            weatherError.addProperty("error", "Unable to retrieve weather data: " + e.getMessage());
            weatherError.addProperty("businessImpact", "Plan for variable weather conditions in Atlanta fitness market");
            result.add("atlantaWeather", weatherError);
        }
        
        // 4. Find gyms and fitness centers near Atlanta
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult gyms = maps.get_nearestBusinesses(
            "Atlanta, Georgia", "gym fitness center", 15);
        
        JsonObject fitnessMarketInfo = new JsonObject();
        fitnessMarketInfo.addProperty("searchArea", "Atlanta, Georgia");
        fitnessMarketInfo.addProperty("purpose", "Market research for fitness coaching business location and competition analysis");
        
        JsonArray competitorAnalysis = new JsonArray();
        int corporateChains = 0;
        int boutiqueStudios = 0;
        int independentGyms = 0;
        
        for (maps_google_com.BusinessInfo gym : gyms.businesses) {
            JsonObject gymObj = new JsonObject();
            gymObj.addProperty("name", gym.name);
            gymObj.addProperty("address", gym.address);
            
            // Categorize competition
            String competitorType = categorizeCompetitor(gym.name);
            gymObj.addProperty("competitorType", competitorType);
            
            // Business opportunity analysis
            String businessOpportunity = analyzeBusinessOpportunity(gym.name, gym.address);
            gymObj.addProperty("businessOpportunity", businessOpportunity);
            
            // Market positioning insights
            String marketPosition = determineMarketPosition(gym.name);
            gymObj.addProperty("marketPositioning", marketPosition);
            
            // Count competitor types
            if (competitorType.contains("Corporate")) corporateChains++;
            else if (competitorType.contains("Boutique")) boutiqueStudios++;
            else independentGyms++;
            
            competitorAnalysis.add(gymObj);
        }
        
        fitnessMarketInfo.add("competitors", competitorAnalysis);
        
        // Market analysis summary
        JsonObject marketAnalysis = new JsonObject();
        marketAnalysis.addProperty("totalCompetitors", gyms.businesses.size());
        marketAnalysis.addProperty("corporateChains", corporateChains);
        marketAnalysis.addProperty("boutiqueStudios", boutiqueStudios);
        marketAnalysis.addProperty("independentGyms", independentGyms);
        
        // Market opportunity assessment
        JsonObject opportunityAssessment = new JsonObject();
        
        if (boutiqueStudios >= corporateChains) {
            opportunityAssessment.addProperty("marketTrend", "High demand for specialized boutique fitness experiences");
            opportunityAssessment.addProperty("businessStrategy", "Focus on niche training specialties and personalized coaching");
        } else {
            opportunityAssessment.addProperty("marketTrend", "Traditional gym market with opportunity for differentiation");
            opportunityAssessment.addProperty("businessStrategy", "Emphasize personal training and customized programs");
        }
        
        // Competitive advantages to develop
        JsonArray competitiveAdvantages = new JsonArray();
        competitiveAdvantages.add("Personalized one-on-one coaching vs. group class model");
        competitiveAdvantages.add("Flexible location options - client homes, parks, mobile training");
        competitiveAdvantages.add("Customized nutrition and lifestyle coaching integration");
        competitiveAdvantages.add("Technology integration - apps, wearables, virtual sessions");
        competitiveAdvantages.add("Specialized programs - injury recovery, senior fitness, athletic performance");
        
        opportunityAssessment.add("differentiationStrategies", competitiveAdvantages);
        
        // Location strategy recommendations
        JsonArray locationStrategy = new JsonArray();
        locationStrategy.add("Consider areas with limited boutique fitness options");
        locationStrategy.add("Target residential neighborhoods with high disposable income");
        locationStrategy.add("Explore partnerships with existing gyms for specialized programs");
        locationStrategy.add("Evaluate mobile training service to reduce overhead costs");
        
        opportunityAssessment.add("locationRecommendations", locationStrategy);
        
        marketAnalysis.add("opportunityAssessment", opportunityAssessment);
        fitnessMarketInfo.add("marketAnalysis", marketAnalysis);
        
        result.add("atlantaFitnessMarket", fitnessMarketInfo);
        
        // 5. Fitness coaching business development summary
        JsonObject businessPlan = new JsonObject();
        businessPlan.addProperty("businessConcept", "Personal Fitness Coaching Service - Atlanta, Georgia");
        businessPlan.addProperty("targetMarket", "Health-conscious individuals seeking personalized training solutions");
        
        // Business development strategy
        JsonObject developmentStrategy = new JsonObject();
        developmentStrategy.addProperty("contentStrategy", "Leverage YouTube research to create professional training content");
        developmentStrategy.addProperty("weatherAdaptation", "Design programs that work year-round in Atlanta climate");
        developmentStrategy.addProperty("marketDifferentiation", "Position against existing gym competition with personalized approach");
        developmentStrategy.addProperty("equipmentStrategy", "Use cleared Amazon cart for professional equipment procurement");
        
        // Key business milestones
        JsonArray businessMilestones = new JsonArray();
        businessMilestones.add("Complete market research and competitor analysis");
        businessMilestones.add("Develop signature training programs and methodologies");
        businessMilestones.add("Create professional content library for marketing");
        businessMilestones.add("Establish equipment and technology infrastructure");
        businessMilestones.add("Build client base through referrals and social media");
        businessMilestones.add("Scale with additional trainers and expanded services");
        
        developmentStrategy.add("implementationMilestones", businessMilestones);
        
        // Revenue streams identification
        JsonObject revenueStreams = new JsonObject();
        revenueStreams.addProperty("personalTraining", "One-on-one coaching sessions - premium pricing");
        revenueStreams.addProperty("groupClasses", "Small group training - cost-effective for clients");
        revenueStreams.addProperty("onlineCoaching", "Virtual training sessions - scalable service delivery");
        revenueStreams.addProperty("nutritionConsulting", "Meal planning and dietary guidance - complementary service");
        revenueStreams.addProperty("corporateWellness", "Business fitness programs - B2B opportunity");
        
        developmentStrategy.add("revenueOpportunities", revenueStreams);
        
        // Success metrics tracking
        JsonArray successMetrics = new JsonArray();
        successMetrics.add("Client retention rate and satisfaction scores");
        successMetrics.add("Revenue per client and monthly recurring revenue");
        successMetrics.add("Market share growth in target demographics");
        successMetrics.add("Social media engagement and referral rates");
        successMetrics.add("Professional certification achievements and continuing education");
        
        developmentStrategy.add("performanceMetrics", successMetrics);
        
        businessPlan.add("developmentStrategy", developmentStrategy);
        result.add("fitnessBusinessPlan", businessPlan);
        
        return result;
    }
    
    // Helper method to analyze video content for business value
    private static String analyzeVideoContent(String title) {
        String titleLower = title.toLowerCase();
        
        if (titleLower.contains("beginner") || titleLower.contains("basic")) {
            return "Beginner-friendly content - Great for understanding foundational teaching approaches";
        } else if (titleLower.contains("advanced") || titleLower.contains("expert")) {
            return "Advanced content - Study specialized techniques and progression methods";
        } else if (titleLower.contains("hiit") || titleLower.contains("cardio")) {
            return "High-intensity training - Popular format with strong market demand";
        } else if (titleLower.contains("strength") || titleLower.contains("weight")) {
            return "Strength training focus - Equipment-based programs with recurring revenue potential";
        } else if (titleLower.contains("yoga") || titleLower.contains("pilates")) {
            return "Mind-body fitness - Growing market segment with wellness integration";
        } else if (titleLower.contains("home") || titleLower.contains("bodyweight")) {
            return "Home fitness content - Scalable model for remote coaching services";
        } else {
            return "General fitness content - Study presentation style and engagement techniques";
        }
    }
    
    // Helper method to categorize competitors
    private static String categorizeCompetitor(String gymName) {
        String nameLower = gymName.toLowerCase();
        
        if (nameLower.contains("planet fitness") || nameLower.contains("la fitness") || 
            nameLower.contains("24 hour") || nameLower.contains("gold's gym")) {
            return "Corporate Chain - Large membership base, standardized programs, competitive pricing";
        } else if (nameLower.contains("crossfit") || nameLower.contains("yoga") || 
                   nameLower.contains("pilates") || nameLower.contains("barre")) {
            return "Boutique Studio - Specialized programs, premium pricing, community focus";
        } else if (nameLower.contains("martial arts") || nameLower.contains("boxing") || 
                   nameLower.contains("dance")) {
            return "Specialty Training - Niche market, unique programs, loyal customer base";
        } else {
            return "Independent Gym - Local ownership, flexible programs, community connections";
        }
    }
    
    // Helper method to analyze business opportunities
    private static String analyzeBusinessOpportunity(String gymName, String address) {
        String nameLower = gymName.toLowerCase();
        String addressLower = address.toLowerCase();
        
        if (nameLower.contains("planet fitness") || nameLower.contains("la fitness")) {
            return "High-volume competitor - Opportunity for premium personalized services";
        } else if (nameLower.contains("crossfit") || nameLower.contains("boutique")) {
            return "Specialized competitor - Focus on different niche or complementary services";
        } else if (addressLower.contains("downtown") || addressLower.contains("midtown")) {
            return "Urban location - Target busy professionals with convenient training options";
        } else if (addressLower.contains("suburban") || addressLower.contains("residential")) {
            return "Suburban market - Family-focused programs and flexible scheduling opportunities";
        } else {
            return "Market gap analysis needed - Research specific demographic and service offerings";
        }
    }
    
    // Helper method to determine market positioning
    private static String determineMarketPosition(String gymName) {
        String nameLower = gymName.toLowerCase();
        
        if (nameLower.contains("anytime") || nameLower.contains("24") || nameLower.contains("hour")) {
            return "Convenience positioning - Compete with flexible scheduling and location options";
        } else if (nameLower.contains("women") || nameLower.contains("ladies")) {
            return "Gender-specific market - Consider specialized programs for underserved demographics";
        } else if (nameLower.contains("elite") || nameLower.contains("premium") || nameLower.contains("luxury")) {
            return "Premium market - Match or exceed service quality with personalized approach";
        } else if (nameLower.contains("community") || nameLower.contains("neighborhood")) {
            return "Community focus - Leverage local connections and personalized relationships";
        } else {
            return "General market position - Differentiate through specialization and service quality";
        }
    }
}
