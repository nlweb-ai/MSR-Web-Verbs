import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0015 {
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
        
        // 1. Search for camera equipment at Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult cameraResults = costco.searchProducts("camera");
        
        JsonObject cameraEquipmentInfo = new JsonObject();
        cameraEquipmentInfo.addProperty("searchTerm", "camera");
        cameraEquipmentInfo.addProperty("purpose", "Photography workshop equipment for participants");
        
        if (cameraResults.error != null) {
            cameraEquipmentInfo.addProperty("error", cameraResults.error);
        }
        
        JsonArray cameraProductsArray = new JsonArray();
        double totalCameraCost = 0.0;
        double minCameraPrice = Double.MAX_VALUE;
        double maxCameraPrice = 0.0;
        int validCameraPrices = 0;
        
        for (costco_com.ProductInfo product : cameraResults.products) {
            JsonObject productObj = new JsonObject();
            productObj.addProperty("productName", product.productName);
            
            if (product.productPrice != null) {
                productObj.addProperty("priceAmount", product.productPrice.amount);
                productObj.addProperty("priceCurrency", product.productPrice.currency);
                
                totalCameraCost += product.productPrice.amount;
                validCameraPrices++;
                minCameraPrice = Math.min(minCameraPrice, product.productPrice.amount);
                maxCameraPrice = Math.max(maxCameraPrice, product.productPrice.amount);
                
                // Categorize equipment by price range for different packages
                String packageLevel;
                if (product.productPrice.amount <= 200) {
                    packageLevel = "Basic Package - Entry-level equipment for beginners";
                } else if (product.productPrice.amount <= 600) {
                    packageLevel = "Intermediate Package - Mid-range equipment for enthusiasts";
                } else {
                    packageLevel = "Advanced Package - Professional-grade equipment";
                }
                productObj.addProperty("recommendedPackage", packageLevel);
            } else {
                productObj.addProperty("priceAmount", (String) null);
                productObj.addProperty("priceCurrency", (String) null);
                productObj.addProperty("recommendedPackage", "Price not available");
            }
            
            if (product.error != null) {
                productObj.addProperty("error", product.error);
            }
            
            cameraProductsArray.add(productObj);
        }
        
        cameraEquipmentInfo.add("equipment", cameraProductsArray);
        
        // Calculate package pricing
        JsonObject packagePricing = new JsonObject();
        if (validCameraPrices > 0) {
            double avgPrice = totalCameraCost / validCameraPrices;
            
            JsonObject basicPackage = new JsonObject();
            basicPackage.addProperty("priceRange", "Under $200");
            basicPackage.addProperty("targetAudience", "Complete beginners");
            basicPackage.addProperty("includes", "Basic camera, memory card, simple accessories");
            
            JsonObject intermediatePackage = new JsonObject();
            intermediatePackage.addProperty("priceRange", "$200 - $600");
            intermediatePackage.addProperty("targetAudience", "Photography enthusiasts");
            intermediatePackage.addProperty("includes", "Mid-range camera, multiple lenses, professional accessories");
            
            JsonObject advancedPackage = new JsonObject();
            advancedPackage.addProperty("priceRange", "Over $600");
            advancedPackage.addProperty("targetAudience", "Serious photographers and professionals");
            advancedPackage.addProperty("includes", "Professional camera, premium lenses, advanced accessories");
            
            packagePricing.add("basic", basicPackage);
            packagePricing.add("intermediate", intermediatePackage);
            packagePricing.add("advanced", advancedPackage);
            
            packagePricing.addProperty("averageEquipmentPrice", Math.round(avgPrice * 100.0) / 100.0);
            packagePricing.addProperty("minPrice", Math.round(minCameraPrice * 100.0) / 100.0);
            packagePricing.addProperty("maxPrice", Math.round(maxCameraPrice * 100.0) / 100.0);
        }
        
        cameraEquipmentInfo.add("packageOptions", packagePricing);
        result.add("photographyEquipment", cameraEquipmentInfo);
        
        // 2. Check current weather in Miami, Florida
        try {
            OpenWeather weather = new OpenWeather();
            // Miami, Florida coordinates
            double miamiLat = 25.7617;
            double miamiLon = -80.1918;
            
            OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(miamiLat, miamiLon);
            
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
            weatherInfo.addProperty("cloudiness", currentWeather.getCloudiness());
            weatherInfo.addProperty("visibility", Math.round(currentWeather.getVisibility() * 100.0) / 100.0);
            
            // Photography-specific weather assessment
            String photographyConditions;
            if (currentWeather.getCloudiness() <= 20) {
                photographyConditions = "Excellent - Clear skies perfect for outdoor photography with good natural lighting";
            } else if (currentWeather.getCloudiness() <= 50) {
                photographyConditions = "Good - Partly cloudy skies provide interesting textures and diffused lighting";
            } else if (currentWeather.getCloudiness() <= 80) {
                photographyConditions = "Fair - Overcast conditions good for portrait photography but may need flash for landscapes";
            } else {
                photographyConditions = "Challenging - Heavy cloud cover, recommend indoor sessions or creative storm photography";
            }
            
            // Lighting conditions assessment
            String lightingAssessment;
            if (currentWeather.getCloudiness() <= 30) {
                lightingAssessment = "Bright natural light - Great for landscape and architectural photography";
            } else if (currentWeather.getCloudiness() <= 70) {
                lightingAssessment = "Diffused natural light - Perfect for portrait and macro photography";
            } else {
                lightingAssessment = "Low natural light - Ideal for learning artificial lighting techniques";
            }
            
            // Weather-based activity recommendations
            JsonArray weatherRecommendations = new JsonArray();
            if (currentWeather.getTemperature() > 25 && currentWeather.getCloudiness() <= 50) {
                weatherRecommendations.add("Outdoor portrait sessions with natural lighting");
                weatherRecommendations.add("Beach and waterfront photography");
                weatherRecommendations.add("Street photography in Miami's colorful neighborhoods");
            }
            if (currentWeather.getCloudiness() > 70) {
                weatherRecommendations.add("Indoor studio lighting workshops");
                weatherRecommendations.add("Low-light photography techniques");
                weatherRecommendations.add("Creative indoor composition exercises");
            }
            if (currentWeather.getWindSpeed() < 5) {
                weatherRecommendations.add("Macro photography sessions (minimal wind interference)");
                weatherRecommendations.add("Long exposure techniques");
            }
            
            weatherInfo.addProperty("photographyConditions", photographyConditions);
            weatherInfo.addProperty("lightingAssessment", lightingAssessment);
            weatherInfo.add("recommendedActivities", weatherRecommendations);
            
            result.add("miamiWeather", weatherInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject weatherError = new JsonObject();
            weatherError.addProperty("error", "Failed to get weather data: " + e.getMessage());
            result.add("miamiWeather", weatherError);
        }
        
        // 3. Find parks and scenic locations near Miami Beach
        maps_google_com maps = new maps_google_com(context);
        
        maps_google_com.NearestBusinessesResult parks = maps.get_nearestBusinesses(
            "Miami Beach, Florida", "park", 10);
        
        JsonObject photographyLocationsInfo = new JsonObject();
        photographyLocationsInfo.addProperty("searchArea", "Miami Beach, Florida");
        photographyLocationsInfo.addProperty("locationType", "Parks and scenic areas");
        photographyLocationsInfo.addProperty("purpose", "Photography practice session locations");
        
        JsonArray parksArray = new JsonArray();
        for (maps_google_com.BusinessInfo park : parks.businesses) {
            JsonObject parkObj = new JsonObject();
            parkObj.addProperty("name", park.name);
            parkObj.addProperty("address", park.address);
            
            // Add photography-specific recommendations based on location name
            String photographyValue = getPhotographyRecommendation(park.name);
            parkObj.addProperty("photographyOpportunities", photographyValue);
            
            parksArray.add(parkObj);
        }
        photographyLocationsInfo.add("parks", parksArray);
        
        // Also search for scenic locations
        maps_google_com.NearestBusinessesResult scenicSpots = maps.get_nearestBusinesses(
            "Miami Beach, Florida", "scenic viewpoint", 8);
        
        JsonArray scenicSpotsArray = new JsonArray();
        for (maps_google_com.BusinessInfo spot : scenicSpots.businesses) {
            JsonObject spotObj = new JsonObject();
            spotObj.addProperty("name", spot.name);
            spotObj.addProperty("address", spot.address);
            spotObj.addProperty("photographyOpportunities", "Scenic vistas, landscape photography, golden hour shots");
            scenicSpotsArray.add(spotObj);
        }
        photographyLocationsInfo.add("scenicLocations", scenicSpotsArray);
        
        // Add location shooting tips
        JsonObject locationTips = new JsonObject();
        locationTips.addProperty("bestTimes", "Golden hour (1 hour before sunset) and blue hour (30 min after sunset)");
        locationTips.addProperty("equipment", "Bring tripods for low-light conditions and polarizing filters for water shots");
        locationTips.addProperty("permissions", "Check if permits are required for professional shoots in public parks");
        locationTips.addProperty("safety", "Stay hydrated, use sunscreen, and be aware of tides when shooting near water");
        photographyLocationsInfo.add("shootingTips", locationTips);
        
        result.add("photographyLocations", photographyLocationsInfo);
        
        // 4. Search YouTube for "photography lighting techniques" videos
        youtube_com youtube = new youtube_com(context);
        java.util.List<youtube_com.YouTubeVideoInfo> youtubeResults = youtube.searchVideos("photography lighting techniques");
        
        JsonObject educationalContentInfo = new JsonObject();
        educationalContentInfo.addProperty("searchQuery", "photography lighting techniques");
        educationalContentInfo.addProperty("purpose", "Comprehensive learning resource for workshop attendees");
        
        JsonArray videosArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : youtubeResults) {
            JsonObject videoObj = new JsonObject();
            videoObj.addProperty("title", video.title);
            videoObj.addProperty("url", video.url);
            
            // Format Duration as hh:mm:ss or mm:ss
            long s = video.length.getSeconds();
            long h = s / 3600;
            long m = (s % 3600) / 60;
            long sec = s % 60;
            String lenStr = h > 0 ? String.format("%d:%02d:%02d", h, m, sec) : String.format("%d:%02d", m, sec);
            videoObj.addProperty("length", lenStr);
            
            // Categorize videos by content and duration for workshop use
            String workshopApplication = categorizeVideForWorkshop(video.title, s);
            videoObj.addProperty("workshopApplication", workshopApplication);
            
            // Determine skill level based on title
            String skillLevel = determineSkillLevel(video.title);
            videoObj.addProperty("skillLevel", skillLevel);
            
            videosArray.add(videoObj);
        }
        educationalContentInfo.add("videos", videosArray);
        
        // Add curriculum organization suggestions
        JsonObject curriculumStructure = new JsonObject();
        curriculumStructure.addProperty("beginnerModule", "Start with basic natural lighting and camera exposure");
        curriculumStructure.addProperty("intermediateModule", "Progress to artificial lighting setups and flash techniques");
        curriculumStructure.addProperty("advancedModule", "Cover creative lighting effects and professional studio techniques");
        curriculumStructure.addProperty("practicalSession", "Hands-on practice applying techniques learned from videos");
        educationalContentInfo.add("curriculumRecommendations", curriculumStructure);
        
        result.add("educationalContent", educationalContentInfo);
        
        // Add comprehensive workshop planning summary
        JsonObject workshopSummary = new JsonObject();
        workshopSummary.addProperty("workshop", "Photography Workshop - Miami, Florida");
        workshopSummary.addProperty("focus", "Camera equipment, outdoor shooting, and lighting techniques");
        workshopSummary.addProperty("venue", "Miami Beach area with park and scenic locations");
        
        JsonArray preparationSteps = new JsonArray();
        preparationSteps.add("Finalize equipment packages based on participant skill levels and budget");
        preparationSteps.add("Monitor weather conditions and prepare backup indoor locations");
        preparationSteps.add("Scout photography locations and obtain necessary permits");
        preparationSteps.add("Create structured video playlist for different skill levels");
        preparationSteps.add("Prepare practical exercises combining theory with hands-on practice");
        preparationSteps.add("Set up equipment stations for different package levels");
        
        workshopSummary.add("preparationChecklist", preparationSteps);
        
        // Budget estimation
        if (validCameraPrices > 0) {
            double avgEquipmentCost = totalCameraCost / validCameraPrices;
            JsonObject budgetEstimate = new JsonObject();
            budgetEstimate.addProperty("basicPackagePerParticipant", Math.round(minCameraPrice * 100.0) / 100.0);
            budgetEstimate.addProperty("intermediatePackagePerParticipant", Math.round(avgEquipmentCost * 100.0) / 100.0);
            budgetEstimate.addProperty("advancedPackagePerParticipant", Math.round(maxCameraPrice * 100.0) / 100.0);
            workshopSummary.add("budgetEstimates", budgetEstimate);
        }
        
        result.add("workshopPlanning", workshopSummary);
        
        return result;
    }
    
    // Helper method to determine photography value of a location
    private static String getPhotographyRecommendation(String locationName) {
        String name = locationName.toLowerCase();
        if (name.contains("beach") || name.contains("ocean") || name.contains("water")) {
            return "Seascape photography, sunrise/sunset shots, water reflections, beach portraits";
        } else if (name.contains("garden") || name.contains("botanical")) {
            return "Macro photography, flower close-ups, nature compositions, soft natural lighting";
        } else if (name.contains("historic") || name.contains("art") || name.contains("museum")) {
            return "Architectural photography, cultural documentation, indoor lighting practice";
        } else if (name.contains("downtown") || name.contains("city")) {
            return "Urban photography, street scenes, architectural details, night photography";
        } else {
            return "General outdoor photography, landscape compositions, natural lighting practice";
        }
    }
    
    // Helper method to categorize videos for workshop use
    private static String categorizeVideForWorkshop(String title, long durationSeconds) {
        String titleLower = title.toLowerCase();
        
        if (durationSeconds <= 300) { // 5 minutes or less
            return "Quick technique demonstration - perfect for workshop segments";
        } else if (durationSeconds <= 900) { // 15 minutes or less
            if (titleLower.contains("beginner") || titleLower.contains("basics")) {
                return "Foundational lesson - ideal for workshop introduction";
            } else {
                return "Focused skill building - good for specific technique sessions";
            }
        } else if (durationSeconds <= 1800) { // 30 minutes or less
            return "Comprehensive tutorial - suitable for dedicated learning blocks";
        } else {
            return "Extended learning resource - best for homework or self-study";
        }
    }
    
    // Helper method to determine skill level from video title
    private static String determineSkillLevel(String title) {
        String titleLower = title.toLowerCase();
        
        if (titleLower.contains("beginner") || titleLower.contains("basics") || titleLower.contains("introduction")) {
            return "Beginner";
        } else if (titleLower.contains("advanced") || titleLower.contains("professional") || titleLower.contains("expert")) {
            return "Advanced";
        } else if (titleLower.contains("intermediate") || titleLower.contains("next level")) {
            return "Intermediate";
        } else {
            return "All Levels";
        }
    }
}
