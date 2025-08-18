import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0013 {
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
        
        // 1. Get NASA's Astronomy Picture of the Day for August 10th, 2025
        try {
            Nasa nasa = new Nasa();
            Nasa.ApodResult apod = nasa.getApod("2025-07-31", true);
            
            JsonObject apodInfo = new JsonObject();
            apodInfo.addProperty("requestedDate", "2025-07-31");
            apodInfo.addProperty("title", apod.title);
            apodInfo.addProperty("url", apod.url);
            apodInfo.addProperty("explanation", apod.explanation);
            apodInfo.addProperty("actualDate", apod.date.toString());
            
            // Analyze the explanation to create discussion topics
            JsonArray discussionTopics = new JsonArray();
            String explanation = apod.explanation.toLowerCase();
            
            if (explanation.contains("galaxy") || explanation.contains("galaxies")) {
                discussionTopics.add("Galaxy formation and evolution");
                discussionTopics.add("Different types of galaxies and their characteristics");
            }
            if (explanation.contains("nebula") || explanation.contains("nebulae")) {
                discussionTopics.add("Stellar nurseries and star formation");
                discussionTopics.add("Types of nebulae and their role in the cosmos");
            }
            if (explanation.contains("planet") || explanation.contains("planets")) {
                discussionTopics.add("Planetary science and exploration");
                discussionTopics.add("Comparative planetology in our solar system");
            }
            if (explanation.contains("star") || explanation.contains("stellar")) {
                discussionTopics.add("Stellar lifecycle and evolution");
                discussionTopics.add("How stars influence their cosmic neighborhoods");
            }
            if (explanation.contains("comet") || explanation.contains("asteroid")) {
                discussionTopics.add("Small bodies in the solar system");
                discussionTopics.add("Impact events and planetary defense");
            }
            if (explanation.contains("cluster")) {
                discussionTopics.add("Star clusters and their significance");
                discussionTopics.add("How clusters help us understand stellar evolution");
            }
            
            // Add some general topics if none were detected
            if (discussionTopics.size() == 0) {
                discussionTopics.add("The scale and structure of the universe");
                discussionTopics.add("How modern astronomy captures such images");
                discussionTopics.add("The role of space telescopes in discovery");
            }
            
            apodInfo.add("suggestedDiscussionTopics", discussionTopics);
            result.add("nasaApod", apodInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject apodError = new JsonObject();
            apodError.addProperty("error", "Failed to get NASA APOD: " + e.getMessage());
            apodError.addProperty("requestedDate", "2025-08-10");
            result.add("nasaApod", apodError);
        }
        
        // 2. Check current weather in Denver, Colorado
        try {
            OpenWeather weather = new OpenWeather();
            // Denver, Colorado coordinates
            double denverLat = 39.7392;
            double denverLon = -104.9903;
            
            OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(denverLat, denverLon);
            
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
            
            // Assess outdoor stargazing conditions
            String stargizingAssessment;
            if (currentWeather.getCloudiness() <= 10 && currentWeather.getVisibility() >= 10) {
                stargizingAssessment = "Excellent conditions for outdoor stargazing - clear skies and good visibility";
            } else if (currentWeather.getCloudiness() <= 30 && currentWeather.getVisibility() >= 8) {
                stargizingAssessment = "Good conditions for outdoor stargazing - mostly clear with decent visibility";
            } else if (currentWeather.getCloudiness() <= 60) {
                stargizingAssessment = "Fair conditions - some clouds present, consider backup indoor activities";
            } else {
                stargizingAssessment = "Poor conditions for stargazing - mostly cloudy, recommend indoor activities only";
            }
            
            // Temperature comfort assessment
            String temperatureAssessment;
            double temp = currentWeather.getTemperature();
            if (temp >= 15 && temp <= 25) {
                temperatureAssessment = "Comfortable temperature for outdoor activities";
            } else if (temp >= 10 && temp <= 30) {
                temperatureAssessment = "Acceptable temperature - dress appropriately for outdoor activities";
            } else if (temp < 10) {
                temperatureAssessment = "Cold conditions - ensure warm clothing for outdoor stargazing";
            } else {
                temperatureAssessment = "Hot conditions - consider evening timing for outdoor activities";
            }
            
            weatherInfo.addProperty("stargizingConditions", stargizingAssessment);
            weatherInfo.addProperty("temperatureComfort", temperatureAssessment);
            
            result.add("denverWeather", weatherInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject weatherError = new JsonObject();
            weatherError.addProperty("error", "Failed to get weather data: " + e.getMessage());
            result.add("denverWeather", weatherError);
        }
        
        // 3. Find conference centers and meeting spaces near downtown Denver
        maps_google_com maps = new maps_google_com(context);
        
        maps_google_com.NearestBusinessesResult conferenceVenues = maps.get_nearestBusinesses(
            "downtown Denver, Colorado", "conference center", 8);
        
        JsonObject venueInfo = new JsonObject();
        venueInfo.addProperty("searchArea", "downtown Denver, Colorado");
        venueInfo.addProperty("venueType", "conference center");
        
        JsonArray conferenceCentersArray = new JsonArray();
        for (maps_google_com.BusinessInfo venue : conferenceVenues.businesses) {
            JsonObject venueObj = new JsonObject();
            venueObj.addProperty("name", venue.name);
            venueObj.addProperty("address", venue.address);
            venueObj.addProperty("suitability", "Large group events and presentations");
            conferenceCentersArray.add(venueObj);
        }
        venueInfo.add("conferenceVenues", conferenceCentersArray);
        
        // Also search for meeting rooms/spaces
        maps_google_com.NearestBusinessesResult meetingSpaces = maps.get_nearestBusinesses(
            "downtown Denver, Colorado", "meeting room", 8);
        
        JsonArray meetingRoomsArray = new JsonArray();
        for (maps_google_com.BusinessInfo space : meetingSpaces.businesses) {
            JsonObject spaceObj = new JsonObject();
            spaceObj.addProperty("name", space.name);
            spaceObj.addProperty("address", space.address);
            spaceObj.addProperty("suitability", "Intimate group discussions and workshops");
            meetingRoomsArray.add(spaceObj);
        }
        venueInfo.add("meetingSpaces", meetingRoomsArray);
        
        // Add venue recommendations
        JsonObject venueRecommendations = new JsonObject();
        venueRecommendations.addProperty("groupSize", "Consider venue capacity for your expected attendance");
        venueRecommendations.addProperty("equipment", "Ensure venue has projection equipment for NASA imagery");
        venueRecommendations.addProperty("accessibility", "Check for ADA compliance and parking availability");
        venueRecommendations.addProperty("backup", "Have indoor options ready in case of poor weather");
        venueInfo.add("bookingConsiderations", venueRecommendations);
        
        result.add("venueOptions", venueInfo);
        
        // 4. Search YouTube for "astronomy for beginners" videos
        youtube_com youtube = new youtube_com(context);
        java.util.List<youtube_com.YouTubeVideoInfo> youtubeResults = youtube.searchVideos("astronomy for beginners");
        
        JsonObject playlistInfo = new JsonObject();
        playlistInfo.addProperty("searchQuery", "astronomy for beginners");
        playlistInfo.addProperty("purpose", "Educational playlist for newcomers to astronomy meetup");
        
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
            
            // Categorize by length for meetup planning
            String usageRecommendation;
            if (s <= 300) { // 5 minutes or less
                usageRecommendation = "Perfect for quick introductions or ice breakers";
            } else if (s <= 900) { // 15 minutes or less
                usageRecommendation = "Good for focused topic discussions";
            } else if (s <= 1800) { // 30 minutes or less
                usageRecommendation = "Suitable for main presentation content";
            } else {
                usageRecommendation = "Best for homework or extended viewing between meetups";
            }
            videoObj.addProperty("meetupUsage", usageRecommendation);
            
            videosArray.add(videoObj);
        }
        playlistInfo.add("videos", videosArray);
        
        // Add playlist organization suggestions
        JsonObject playlistStructure = new JsonObject();
        playlistStructure.addProperty("opening", "Start with short, engaging videos to capture interest");
        playlistStructure.addProperty("core", "Use medium-length videos for main educational content");
        playlistStructure.addProperty("resources", "Provide longer videos as take-home resources");
        playlistStructure.addProperty("interaction", "Pause videos for questions and group discussions");
        playlistInfo.add("organizationTips", playlistStructure);
        
        result.add("educationalPlaylist", playlistInfo);
        
        // Add meetup planning summary
        JsonObject meetupSummary = new JsonObject();
        meetupSummary.addProperty("event", "Space Enthusiast Meetup - Denver, Colorado");
        meetupSummary.addProperty("featuredDate", "August 10th, 2025 (NASA APOD)");
        meetupSummary.addProperty("focus", "Astronomy education for beginners with featured NASA content");
        
        JsonArray preparationSteps = new JsonArray();
        preparationSteps.add("Book appropriate venue based on weather and group size");
        preparationSteps.add("Prepare NASA APOD presentation with discussion topics");
        preparationSteps.add("Curate beginner-friendly video playlist");
        preparationSteps.add("Plan indoor/outdoor activities based on weather conditions");
        preparationSteps.add("Ensure venue has necessary AV equipment for presentations");
        
        meetupSummary.add("nextSteps", preparationSteps);
        result.add("meetupPlanning", meetupSummary);
        
        return result;
    }
}
