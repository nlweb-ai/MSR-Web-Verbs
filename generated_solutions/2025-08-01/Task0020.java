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


public class Task0020 {
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
        
        // 1. Search for presentation equipment and audio-visual supplies at Costco
        costco_com costco = new costco_com(context);
        costco_com.ProductListResult equipmentResults = costco.searchProducts("presentation equipment");
        
        JsonObject conferenceEquipmentInfo = new JsonObject();
        conferenceEquipmentInfo.addProperty("searchTerm", "presentation equipment");
        conferenceEquipmentInfo.addProperty("purpose", "Professional audio-visual setup for scientific conference in Boston");
        conferenceEquipmentInfo.addProperty("targetAudience", "200 scientific conference attendees");
        
        if (equipmentResults.error != null) {
            conferenceEquipmentInfo.addProperty("error", equipmentResults.error);
        }
        
        JsonArray equipmentArray = new JsonArray();
        double totalEquipmentCost = 0.0;
        
        for (costco_com.ProductInfo product : equipmentResults.products) {
            JsonObject productObj = new JsonObject();
            productObj.addProperty("productName", product.productName);
            
            if (product.productPrice != null) {
                productObj.addProperty("priceAmount", product.productPrice.amount);
                productObj.addProperty("priceCurrency", product.productPrice.currency);
                
                // Assess equipment suitability for conference
                String conferenceSuitability = assessConferenceEquipment(product.productName, product.productPrice.amount);
                productObj.addProperty("conferenceSuitability", conferenceSuitability);
                
                // Determine session type compatibility
                String sessionCompatibility = determineSessionType(product.productName);
                productObj.addProperty("sessionTypeCompatibility", sessionCompatibility);
                
                totalEquipmentCost += product.productPrice.amount;
            }
            
            if (product.error != null) {
                productObj.addProperty("error", product.error);
            }
            
            equipmentArray.add(productObj);
        }
        
        conferenceEquipmentInfo.add("equipment", equipmentArray);
        
        // Conference equipment setup packages
        JsonObject setupPackages = new JsonObject();
        setupPackages.addProperty("totalEquipmentBudget", Math.round(totalEquipmentCost * 100.0) / 100.0);
        
        JsonObject keynotePackage = new JsonObject();
        keynotePackage.addProperty("packageType", "Keynote Presentation Setup");
        keynotePackage.addProperty("description", "Large auditorium setup for 200+ attendees");
        keynotePackage.addProperty("requirements", "High-resolution projector, wireless microphone system, confidence monitor");
        keynotePackage.addProperty("estimatedCost", Math.round(totalEquipmentCost * 0.6 * 100.0) / 100.0);
        
        JsonObject breakoutPackage = new JsonObject();
        breakoutPackage.addProperty("packageType", "Breakout Session Setup");
        breakoutPackage.addProperty("description", "Smaller rooms for 30-50 attendees each");
        breakoutPackage.addProperty("requirements", "Portable projectors, lapel microphones, flip charts");
        breakoutPackage.addProperty("estimatedCost", Math.round(totalEquipmentCost * 0.3 * 100.0) / 100.0);
        
        JsonObject workshopPackage = new JsonObject();
        workshopPackage.addProperty("packageType", "Interactive Workshop Setup");
        workshopPackage.addProperty("description", "Hands-on learning environments with collaboration tools");
        workshopPackage.addProperty("requirements", "Interactive whiteboards, tablet stands, group audio systems");
        workshopPackage.addProperty("estimatedCost", Math.round(totalEquipmentCost * 0.4 * 100.0) / 100.0);
        
        setupPackages.add("keynoteSetup", keynotePackage);
        setupPackages.add("breakoutSetup", breakoutPackage);
        setupPackages.add("workshopSetup", workshopPackage);
        
        conferenceEquipmentInfo.add("setupPackages", setupPackages);
        result.add("conferenceEquipment", conferenceEquipmentInfo);
        
        // 2. Search for scientific presentation skills videos on YouTube
        youtube_com youtube = new youtube_com(context);
        List<youtube_com.YouTubeVideoInfo> presentationVideos = youtube.searchVideos("scientific presentation skills");
        
        JsonObject speakerResourcesInfo = new JsonObject();
        speakerResourcesInfo.addProperty("searchTerm", "scientific presentation skills");
        speakerResourcesInfo.addProperty("purpose", "Create resource guide for conference speakers to improve presentation quality");
        speakerResourcesInfo.addProperty("targetUsers", "PhD researchers, professors, and industry scientists");
        
        JsonArray videosArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : presentationVideos) {
            JsonObject videoObj = new JsonObject();
            videoObj.addProperty("title", video.title);
            videoObj.addProperty("duration", video.length.toString());
            videoObj.addProperty("url", video.url);
            
            // Analyze presentation skill focus
            String skillFocus = analyzePresentationSkillContent(video.title);
            videoObj.addProperty("skillFocus", skillFocus);
            
            // Determine speaker level appropriateness
            String audienceLevel = determineSpeakerLevel(video.title);
            videoObj.addProperty("appropriateFor", audienceLevel);
            
            videosArray.add(videoObj);
        }
        
        speakerResourcesInfo.add("presentationVideos", videosArray);
        
        // Speaker development program
        JsonObject speakerDevelopment = new JsonObject();
        speakerDevelopment.addProperty("programName", "Scientific Conference Speaker Excellence Program");
        speakerDevelopment.addProperty("objective", "Enhance presentation quality and audience engagement for conference speakers");
        
        JsonArray trainingModules = new JsonArray();
        trainingModules.add("Module 1: Structuring Scientific Presentations for Maximum Impact");
        trainingModules.add("Module 2: Visual Design and Data Visualization Best Practices");
        trainingModules.add("Module 3: Audience Engagement and Q&A Management");
        trainingModules.add("Module 4: Managing Presentation Anxiety and Building Confidence");
        trainingModules.add("Module 5: Technology Integration and Multimedia Presentations");
        
        speakerDevelopment.add("trainingModules", trainingModules);
        
        JsonArray deliveryMethods = new JsonArray();
        deliveryMethods.add("Pre-conference online video modules for self-paced learning");
        deliveryMethods.add("Interactive workshop sessions during conference registration");
        deliveryMethods.add("One-on-one coaching sessions for keynote speakers");
        deliveryMethods.add("Peer feedback sessions with experienced presenters");
        
        speakerDevelopment.add("deliveryMethods", deliveryMethods);
        speakerResourcesInfo.add("speakerDevelopmentProgram", speakerDevelopment);
        
        result.add("speakerResources", speakerResourcesInfo);
        
        // 3. Get NASA's Astronomy Picture of the Day for August 5th, 2025
        try {
            Nasa nasa = new Nasa();
            String apodDateString = "2025-08-05";
            Nasa.ApodResult apodResult = nasa.getApod(apodDateString, true);
            
            JsonObject astronomyContentInfo = new JsonObject();
            astronomyContentInfo.addProperty("date", apodResult.date.toString());
            astronomyContentInfo.addProperty("title", apodResult.title);
            astronomyContentInfo.addProperty("explanation", apodResult.explanation);
            astronomyContentInfo.addProperty("imageUrl", apodResult.url);
            astronomyContentInfo.addProperty("purpose", "Feature inspiring space content in conference materials and opening ceremony");
            
            // Conference integration planning
            JsonObject conferenceIntegration = new JsonObject();
            conferenceIntegration.addProperty("openingCeremony", "Display APOD image as backdrop during welcome address");
            conferenceIntegration.addProperty("programCover", "Feature space imagery on conference program and materials");
            conferenceIntegration.addProperty("digitalDisplays", "Showcase throughout venue on screens during breaks");
            conferenceIntegration.addProperty("socialMedia", "Use as featured content for conference social media promotion");
            
            // Educational value assessment
            String educationalValue = assessEducationalValue(apodResult.title, apodResult.explanation);
            conferenceIntegration.addProperty("educationalImpact", educationalValue);
            
            // Inspiration themes for conference
            JsonArray inspirationThemes = new JsonArray();
            inspirationThemes.add("Scientific Discovery and Exploration");
            inspirationThemes.add("Interdisciplinary Research Collaboration");
            inspirationThemes.add("Technology Innovation and Space Science");
            inspirationThemes.add("Wonder and Curiosity in Scientific Inquiry");
            
            conferenceIntegration.add("inspirationalThemes", inspirationThemes);
            
            astronomyContentInfo.add("conferenceIntegration", conferenceIntegration);
            result.add("astronomyContent", astronomyContentInfo);
            
        } catch (IOException | InterruptedException e) {
            JsonObject nasaError = new JsonObject();
            nasaError.addProperty("error", "Unable to retrieve NASA APOD: " + e.getMessage());
            nasaError.addProperty("fallbackPlan", "Use archived space imagery from NASA public gallery for conference materials");
            result.add("astronomyContent", nasaError);
        }
        
        // 4. Find conference centers and meeting facilities near downtown Boston
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.NearestBusinessesResult conferenceCenters = maps.get_nearestBusinesses(
            "downtown Boston, Massachusetts", "conference center meeting facility", 12);
        
        JsonObject venueResearchInfo = new JsonObject();
        venueResearchInfo.addProperty("searchArea", "downtown Boston, Massachusetts");
        venueResearchInfo.addProperty("purpose", "Secure appropriate venue for 200-person scientific conference");
        venueResearchInfo.addProperty("conferenceRequirements", "Multiple session rooms, exhibition space, catering facilities");
        
        JsonArray venuesArray = new JsonArray();
        int conventionCenters = 0;
        int hotels = 0;
        int universities = 0;
        int corporateFacilities = 0;
        
        for (maps_google_com.BusinessInfo venue : conferenceCenters.businesses) {
            JsonObject venueObj = new JsonObject();
            venueObj.addProperty("name", venue.name);
            venueObj.addProperty("address", venue.address);
            
            // Categorize venue type
            String venueType = categorizeVenueType(venue.name);
            venueObj.addProperty("venueType", venueType);
            
            // Assess capacity and suitability
            String capacityAssessment = assessVenueCapacity(venue.name, venue.address);
            venueObj.addProperty("capacityAssessment", capacityAssessment);
            
            // Evaluate amenities and services
            String amenitiesEvaluation = evaluateConferenceAmenities(venue.name);
            venueObj.addProperty("amenitiesEvaluation", amenitiesEvaluation);
            
            // Count venue types
            if (venueType.contains("Convention")) conventionCenters++;
            else if (venueType.contains("Hotel")) hotels++;
            else if (venueType.contains("University")) universities++;
            else corporateFacilities++;
            
            venuesArray.add(venueObj);
        }
        
        venueResearchInfo.add("venues", venuesArray);
        
        // Venue selection analysis
        JsonObject venueAnalysis = new JsonObject();
        venueAnalysis.addProperty("totalVenuesFound", conferenceCenters.businesses.size());
        venueAnalysis.addProperty("conventionCenters", conventionCenters);
        venueAnalysis.addProperty("hotelFacilities", hotels);
        venueAnalysis.addProperty("universityVenues", universities);
        venueAnalysis.addProperty("corporateFacilities", corporateFacilities);
        
        // Venue recommendation strategy
        JsonObject recommendationStrategy = new JsonObject();
        
        if (conventionCenters >= 2) {
            recommendationStrategy.addProperty("primaryRecommendation", "Convention centers offer best capacity and specialized conference facilities");
            recommendationStrategy.addProperty("advantages", "Professional AV setup, multiple breakout rooms, exhibition space");
        } else if (hotels >= 3) {
            recommendationStrategy.addProperty("primaryRecommendation", "Hotel conference facilities provide integrated accommodation and catering");
            recommendationStrategy.addProperty("advantages", "One-stop solution for attendee lodging, meals, and meeting spaces");
        } else {
            recommendationStrategy.addProperty("primaryRecommendation", "Mixed venue strategy combining different facility types");
            recommendationStrategy.addProperty("advantages", "Flexibility in space allocation and cost optimization");
        }
        
        // Conference logistics planning
        JsonArray logisticsConsiderations = new JsonArray();
        logisticsConsiderations.add("Verify capacity for 200 attendees in main auditorium");
        logisticsConsiderations.add("Ensure minimum 4-6 breakout rooms for concurrent sessions");
        logisticsConsiderations.add("Confirm catering facilities for breakfast, lunch, and coffee breaks");
        logisticsConsiderations.add("Evaluate parking availability and public transportation access");
        logisticsConsiderations.add("Assess technology infrastructure and AV support services");
        logisticsConsiderations.add("Review accessibility compliance for attendees with disabilities");
        
        recommendationStrategy.add("logisticsChecklist", logisticsConsiderations);
        
        venueAnalysis.add("recommendationStrategy", recommendationStrategy);
        venueResearchInfo.add("venueSelectionAnalysis", venueAnalysis);
        
        result.add("venueResearch", venueResearchInfo);
        
        // 5. Scientific conference planning summary
        JsonObject conferenceSummary = new JsonObject();
        conferenceSummary.addProperty("event", "Scientific Conference - Boston, Massachusetts");
        conferenceSummary.addProperty("date", "August 5, 2025");
        conferenceSummary.addProperty("expectedAttendees", "200 scientists, researchers, and industry professionals");
        conferenceSummary.addProperty("focus", "Interdisciplinary scientific research and collaboration");
        
        // Budget planning
        JsonObject budgetPlanning = new JsonObject();
        budgetPlanning.addProperty("equipmentBudget", Math.round(totalEquipmentCost * 100.0) / 100.0);
        budgetPlanning.addProperty("venueEstimate", 15000.0); // Estimated venue cost
        budgetPlanning.addProperty("speakerDevelopment", 2500.0); // Speaker training program
        budgetPlanning.addProperty("materialProduction", 1500.0); // Programs, signage, materials
        
        double totalBudget = totalEquipmentCost + 15000 + 2500 + 1500;
        budgetPlanning.addProperty("totalEstimatedBudget", Math.round(totalBudget * 100.0) / 100.0);
        budgetPlanning.addProperty("perAttendeeBreakdown", Math.round((totalBudget / 200) * 100.0) / 100.0);
        
        conferenceSummary.add("budgetPlanning", budgetPlanning);
        
        // Implementation timeline
        JsonArray implementationTimeline = new JsonArray();
        implementationTimeline.add("6 months before: Secure venue and finalize speaker lineup");
        implementationTimeline.add("4 months before: Order equipment and launch speaker development program");
        implementationTimeline.add("3 months before: Open registration and begin marketing campaign");
        implementationTimeline.add("2 months before: Finalize catering and accommodation partnerships");
        implementationTimeline.add("1 month before: Equipment setup and final venue preparations");
        implementationTimeline.add("1 week before: Speaker rehearsals and final logistics coordination");
        
        conferenceSummary.add("implementationTimeline", implementationTimeline);
        
        // Success metrics
        JsonArray successMetrics = new JsonArray();
        successMetrics.add("Attendee satisfaction scores and feedback ratings");
        successMetrics.add("Speaker presentation quality assessments");
        successMetrics.add("Network connections and collaboration opportunities created");
        successMetrics.add("Media coverage and social media engagement");
        successMetrics.add("Future conference interest and commitment");
        
        conferenceSummary.add("successMetrics", successMetrics);
        
        result.add("scientificConferenceSummary", conferenceSummary);
        
        return result;
    }
    
    // Helper method to assess conference equipment suitability
    private static String assessConferenceEquipment(String productName, double price) {
        String nameLower = productName.toLowerCase();
        
        if (nameLower.contains("projector") || nameLower.contains("display")) {
            if (price > 1000) {
                return "Professional-grade presentation equipment - Perfect for keynote sessions";
            }
            return "Standard presentation equipment - Suitable for breakout rooms";
        } else if (nameLower.contains("microphone") || nameLower.contains("audio")) {
            return "Audio equipment - Essential for clear communication with 200 attendees";
        } else if (nameLower.contains("speaker") || nameLower.contains("sound")) {
            return "Sound system - Critical for auditorium and large room presentations";
        } else if (nameLower.contains("screen") || nameLower.contains("whiteboard")) {
            return "Visual display tools - Important for interactive sessions and workshops";
        } else {
            return "General conference equipment - Evaluate specific conference needs";
        }
    }
    
    // Helper method to determine session type compatibility
    private static String determineSessionType(String productName) {
        String nameLower = productName.toLowerCase();
        
        if (nameLower.contains("wireless") || nameLower.contains("portable")) {
            return "All session types - Flexible equipment suitable for keynote, breakout, and workshop formats";
        } else if (nameLower.contains("large") || nameLower.contains("high resolution")) {
            return "Keynote sessions - Best suited for main auditorium presentations";
        } else if (nameLower.contains("interactive") || nameLower.contains("touch")) {
            return "Workshop sessions - Interactive tools for hands-on learning environments";
        } else {
            return "Breakout sessions - Appropriate for smaller group presentations";
        }
    }
    
    // Helper method to analyze presentation skill content
    private static String analyzePresentationSkillContent(String title) {
        String titleLower = title.toLowerCase();
        
        if (titleLower.contains("structure") || titleLower.contains("organize")) {
            return "Content organization and structure - Helps speakers create logical flow";
        } else if (titleLower.contains("visual") || titleLower.contains("slide")) {
            return "Visual design and slide creation - Improves presentation aesthetics and clarity";
        } else if (titleLower.contains("anxiety") || titleLower.contains("confidence")) {
            return "Presentation confidence - Addresses speaker nervousness and stage presence";
        } else if (titleLower.contains("audience") || titleLower.contains("engagement")) {
            return "Audience engagement - Techniques for interactive and compelling presentations";
        } else if (titleLower.contains("scientific") || titleLower.contains("research")) {
            return "Scientific communication - Specialized skills for research presentation";
        } else if (titleLower.contains("data") || titleLower.contains("chart")) {
            return "Data visualization - Essential for scientific data presentation";
        } else {
            return "General presentation skills - Broad communication improvement techniques";
        }
    }
    
    // Helper method to determine speaker level appropriateness
    private static String determineSpeakerLevel(String title) {
        String titleLower = title.toLowerCase();
        
        if (titleLower.contains("beginner") || titleLower.contains("basic")) {
            return "Early-career researchers and graduate students";
        } else if (titleLower.contains("advanced") || titleLower.contains("expert")) {
            return "Senior researchers and experienced conference speakers";
        } else if (titleLower.contains("academic") || titleLower.contains("professor")) {
            return "Academic faculty and research professionals";
        } else if (titleLower.contains("ted") || titleLower.contains("keynote")) {
            return "Keynote speakers and high-profile presenters";
        } else {
            return "All conference speakers - Broadly applicable presentation skills";
        }
    }
    
    // Helper method to assess educational value of NASA content
    private static String assessEducationalValue(String title, String explanation) {
        String combinedText = (title + " " + explanation).toLowerCase();
        
        if (combinedText.contains("galaxy") || combinedText.contains("cosmic")) {
            return "High educational value - Cosmic perspective inspires big-picture scientific thinking";
        } else if (combinedText.contains("technology") || combinedText.contains("instrument")) {
            return "Technology focus - Demonstrates cutting-edge scientific instrumentation and methods";
        } else if (combinedText.contains("discovery") || combinedText.contains("breakthrough")) {
            return "Discovery narrative - Showcases scientific process and breakthrough moments";
        } else if (combinedText.contains("collaboration") || combinedText.contains("international")) {
            return "Collaboration theme - Highlights importance of scientific partnerships";
        } else {
            return "Inspirational content - Motivates scientific curiosity and wonder";
        }
    }
    
    // Helper method to categorize venue types
    private static String categorizeVenueType(String venueName) {
        String nameLower = venueName.toLowerCase();
        
        if (nameLower.contains("convention") || nameLower.contains("expo")) {
            return "Convention Center - Purpose-built for large conferences and exhibitions";
        } else if (nameLower.contains("hotel") || nameLower.contains("marriott") || 
                   nameLower.contains("hilton") || nameLower.contains("hyatt")) {
            return "Hotel Conference Facility - Integrated lodging and meeting spaces";
        } else if (nameLower.contains("university") || nameLower.contains("college") || 
                   nameLower.contains("harvard") || nameLower.contains("mit")) {
            return "University Venue - Academic setting with specialized research facilities";
        } else if (nameLower.contains("center") || nameLower.contains("hall")) {
            return "Community/Cultural Center - Flexible space for various event types";
        } else {
            return "Corporate Facility - Business venue with professional meeting capabilities";
        }
    }
    
    // Helper method to assess venue capacity
    private static String assessVenueCapacity(String venueName, String address) {
        String nameLower = venueName.toLowerCase();
        String addressLower = address.toLowerCase();
        
        if (nameLower.contains("convention") || nameLower.contains("expo")) {
            return "High capacity - Likely suitable for 200+ attendees with multiple concurrent sessions";
        } else if (nameLower.contains("grand") || nameLower.contains("international")) {
            return "Large capacity - Professional venue equipped for major conferences";
        } else if (addressLower.contains("downtown") || addressLower.contains("back bay")) {
            return "Prime location capacity - Central Boston venue with good accessibility";
        } else if (nameLower.contains("hotel")) {
            return "Moderate capacity - Hotel conference facilities typically accommodate 100-300 guests";
        } else {
            return "Variable capacity - Requires specific inquiry for 200-person conference needs";
        }
    }
    
    // Helper method to evaluate conference amenities
    private static String evaluateConferenceAmenities(String venueName) {
        String nameLower = venueName.toLowerCase();
        
        if (nameLower.contains("convention")) {
            return "Full conference amenities - Professional AV, exhibition space, catering, parking";
        } else if (nameLower.contains("hotel")) {
            return "Integrated amenities - Meeting rooms, catering, accommodation, concierge services";
        } else if (nameLower.contains("university")) {
            return "Academic amenities - Lecture halls, research facilities, student dining options";
        } else if (nameLower.contains("center")) {
            return "Community amenities - Flexible spaces, basic AV, local catering partnerships";
        } else {
            return "Standard amenities - Basic meeting facilities, requires additional service coordination";
        }
    }
}
