import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0042 {
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
            // Step 1: Search YouTube for sustainable living educational content
            youtube_com youtube = new youtube_com(context);
            JsonObject youtubeResults = new JsonObject();
            
            try {
                List<youtube_com.YouTubeVideoInfo> sustainableVideos = youtube.searchVideos("sustainable living tips zero waste");
                
                JsonArray videosArray = new JsonArray();
                JsonArray beginnerModules = new JsonArray();
                JsonArray advancedModules = new JsonArray();
                long totalDuration = 0;
                
                if (sustainableVideos != null) {
                    for (youtube_com.YouTubeVideoInfo video : sustainableVideos) {
                        JsonObject videoObj = new JsonObject();
                        videoObj.addProperty("title", video.title);
                        videoObj.addProperty("url", video.url);
                        
                        // Format duration
                        long seconds = video.length.getSeconds();
                        long hours = seconds / 3600;
                        long minutes = (seconds % 3600) / 60;
                        long secs = seconds % 60;
                        String durationStr = hours > 0 ? 
                            String.format("%d:%02d:%02d", hours, minutes, secs) : 
                            String.format("%d:%02d", minutes, secs);
                        videoObj.addProperty("duration", durationStr);
                        videoObj.addProperty("duration_seconds", seconds);
                        
                        totalDuration += seconds;
                        
                        // Categorize videos by length and content for curriculum organization
                        String title = video.title.toLowerCase();
                        if (seconds <= 600) { // 10 minutes or less
                            videoObj.addProperty("curriculum_level", "Beginner");
                            videoObj.addProperty("topic_category", "Quick Tips");
                            beginnerModules.add(videoObj);
                        } else if (seconds <= 1800) { // 30 minutes or less
                            videoObj.addProperty("curriculum_level", "Intermediate");
                            if (title.contains("waste") || title.contains("zero waste")) {
                                videoObj.addProperty("topic_category", "Waste Reduction");
                            } else if (title.contains("energy") || title.contains("conservation")) {
                                videoObj.addProperty("topic_category", "Energy Conservation");
                            } else if (title.contains("shopping") || title.contains("products")) {
                                videoObj.addProperty("topic_category", "Sustainable Shopping");
                            } else {
                                videoObj.addProperty("topic_category", "General Sustainability");
                            }
                        } else {
                            videoObj.addProperty("curriculum_level", "Advanced");
                            videoObj.addProperty("topic_category", "Comprehensive Guide");
                            advancedModules.add(videoObj);
                        }
                        
                        videosArray.add(videoObj);
                    }
                }
                
                youtubeResults.add("educational_videos", videosArray);
                youtubeResults.add("beginner_modules", beginnerModules);
                youtubeResults.add("advanced_modules", advancedModules);
                youtubeResults.addProperty("total_videos", videosArray.size());
                youtubeResults.addProperty("total_duration_minutes", totalDuration / 60);
                youtubeResults.addProperty("curriculum_structure", "Organized by skill level and topic category");
                
                // Create structured learning recommendations
                JsonObject curriculumPlanning = new JsonObject();
                curriculumPlanning.addProperty("beginner_session_length", "30-45 minutes");
                curriculumPlanning.addProperty("advanced_session_length", "60-90 minutes");
                curriculumPlanning.addProperty("recommended_topics", "Waste reduction, energy conservation, sustainable shopping");
                curriculumPlanning.addProperty("workshop_format", "Mix of short demonstrations and longer educational content");
                
                youtubeResults.add("curriculum_planning", curriculumPlanning);
                
            } catch (Exception e) {
                youtubeResults.addProperty("error", "Failed to search YouTube videos: " + e.getMessage());
            }
            
            output.add("educational_content_research", youtubeResults);
            
            // Step 2: Search for eco-friendly products at Costco
            costco_com costco = new costco_com(context);
            JsonObject costcoResults = new JsonObject();
            
            try {
                costco_com.ProductListResult ecoProducts = costco.searchProducts("eco-friendly household products organic foods");
                
                JsonArray householdProducts = new JsonArray();
                JsonArray organicFoods = new JsonArray();
                JsonArray demonstrationItems = new JsonArray();
                double totalSustainableShoppingCost = 0.0;
                
                if (ecoProducts != null && ecoProducts.products != null) {
                    for (costco_com.ProductInfo product : ecoProducts.products) {
                        JsonObject productObj = new JsonObject();
                        productObj.addProperty("name", product.productName);
                        
                        if (product.productPrice != null) {
                            productObj.addProperty("price", product.productPrice.amount);
                            productObj.addProperty("currency", product.productPrice.currency);
                            totalSustainableShoppingCost += product.productPrice.amount;
                            
                            // Calculate environmental impact and value assessment
                            double price = product.productPrice.amount;
                            if (price <= 20) {
                                productObj.addProperty("workshop_suitability", "Excellent - affordable for demonstrations");
                                productObj.addProperty("bulk_advantage", "Great value for multiple participants");
                            } else if (price <= 50) {
                                productObj.addProperty("workshop_suitability", "Good - suitable for small group demos");
                                productObj.addProperty("bulk_advantage", "Reasonable cost for workshop materials");
                            } else {
                                productObj.addProperty("workshop_suitability", "Premium - best for comparison demonstrations");
                                productObj.addProperty("bulk_advantage", "High-quality example for sustainability education");
                            }
                        }
                        
                        // Categorize products for different workshop demonstrations
                        String productName = product.productName.toLowerCase();
                        if (productName.contains("cleaning") || productName.contains("detergent") || 
                            productName.contains("soap") || productName.contains("household")) {
                            productObj.addProperty("category", "Eco-Friendly Household Products");
                            productObj.addProperty("demonstration_focus", "Sustainable cleaning and home care");
                            householdProducts.add(productObj);
                        } else if (productName.contains("organic") || productName.contains("food") || 
                                  productName.contains("snack") || productName.contains("produce")) {
                            productObj.addProperty("category", "Organic Foods");
                            productObj.addProperty("demonstration_focus", "Sustainable food choices and packaging");
                            organicFoods.add(productObj);
                        } else {
                            productObj.addProperty("category", "General Eco-Products");
                            productObj.addProperty("demonstration_focus", "Sustainable lifestyle choices");
                        }
                        
                        // Select items suitable for hands-on demonstrations
                        if (product.productPrice != null && product.productPrice.amount <= 30) {
                            JsonObject demoItem = new JsonObject();
                            demoItem.addProperty("product", product.productName);
                            demoItem.addProperty("demo_activity", "Hands-on product comparison and labeling exercise");
                            demoItem.addProperty("learning_objective", "Identify sustainable product features");
                            demonstrationItems.add(demoItem);
                        }
                        
                        if (product.error != null) {
                            productObj.addProperty("error", product.error);
                        }
                    }
                }
                
                costcoResults.add("household_products", householdProducts);
                costcoResults.add("organic_foods", organicFoods);
                costcoResults.add("demonstration_items", demonstrationItems);
                costcoResults.addProperty("total_products_found", ecoProducts != null && ecoProducts.products != null ? ecoProducts.products.size() : 0);
                costcoResults.addProperty("estimated_demo_budget", totalSustainableShoppingCost);
                costcoResults.addProperty("bulk_shopping_advantage", "Costco bulk sizes perfect for demonstrating long-term sustainability savings");
                
                // Sustainable shopping education plan
                JsonArray shoppingTips = new JsonArray();
                shoppingTips.add("Compare cost-per-unit for bulk eco-friendly products vs conventional alternatives");
                shoppingTips.add("Examine packaging materials and recyclability of different product options");
                shoppingTips.add("Demonstrate reading ingredient lists for environmental impact assessment");
                shoppingTips.add("Calculate long-term savings from sustainable product choices");
                shoppingTips.add("Practice identifying greenwashing vs genuine eco-friendly products");
                
                costcoResults.add("sustainable_shopping_curriculum", shoppingTips);
                
            } catch (Exception e) {
                costcoResults.addProperty("error", "Failed to search Costco products: " + e.getMessage());
            }
            
            output.add("eco_friendly_products_research", costcoResults);
            
            // Step 3: Gather environmental and climate change news
            News news = new News();
            JsonObject newsResults = new JsonObject();
            
            try {
                News.NewsResponse environmentalNews = news.searchEverything("environmental climate change sustainability");
                
                JsonArray newsArticles = new JsonArray();
                JsonArray challengesArray = new JsonArray();
                JsonArray successStoriesArray = new JsonArray();
                
                if (environmentalNews != null && environmentalNews.articles != null) {
                    for (News.NewsArticle article : environmentalNews.articles) {
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("headline", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("source", article.source);
                        articleObj.addProperty("url", article.url);
                        
                        // Categorize articles for workshop discussion
                        String title = article.title.toLowerCase();
                        String description = article.description != null ? article.description.toLowerCase() : "";
                        
                        if (title.contains("success") || title.contains("achievement") || title.contains("progress") ||
                            description.contains("success") || description.contains("achievement")) {
                            articleObj.addProperty("category", "Environmental Success Stories");
                            articleObj.addProperty("workshop_relevance", "Motivational content showing positive impact");
                            successStoriesArray.add(articleObj);
                        } else if (title.contains("challenge") || title.contains("crisis") || title.contains("problem") ||
                                  description.contains("challenge") || description.contains("crisis")) {
                            articleObj.addProperty("category", "Environmental Challenges");
                            articleObj.addProperty("workshop_relevance", "Context for understanding urgency of action");
                            challengesArray.add(articleObj);
                        } else {
                            articleObj.addProperty("category", "General Environmental News");
                            articleObj.addProperty("workshop_relevance", "Current events and trends in sustainability");
                        }
                        
                        // Assess relevance to individual action
                        if (title.contains("individual") || title.contains("personal") || title.contains("household") ||
                            description.contains("individual") || description.contains("personal")) {
                            articleObj.addProperty("individual_action_relevance", "High");
                            articleObj.addProperty("discussion_focus", "How participants can apply these insights personally");
                        } else {
                            articleObj.addProperty("individual_action_relevance", "Medium");
                            articleObj.addProperty("discussion_focus", "Broader context for personal sustainability choices");
                        }
                        
                        newsArticles.add(articleObj);
                    }
                }
                
                newsResults.add("all_environmental_news", newsArticles);
                newsResults.add("success_stories", successStoriesArray);
                newsResults.add("current_challenges", challengesArray);
                newsResults.addProperty("total_articles", newsArticles.size());
                newsResults.addProperty("success_stories_count", successStoriesArray.size());
                newsResults.addProperty("challenges_count", challengesArray.size());
                
                // Create discussion framework for workshop
                JsonObject discussionFramework = new JsonObject();
                discussionFramework.addProperty("opening_topic", "Recent environmental success stories to inspire action");
                discussionFramework.addProperty("main_discussion", "Current challenges and how individual actions contribute to solutions");
                discussionFramework.addProperty("action_planning", "Connecting global context to personal sustainability goals");
                discussionFramework.addProperty("closing_motivation", "Examples of positive change happening worldwide");
                
                newsResults.add("workshop_discussion_framework", discussionFramework);
                
            } catch (Exception e) {
                newsResults.addProperty("error", "Failed to fetch environmental news: " + e.getMessage());
            }
            
            output.add("environmental_news_research", newsResults);
            
            // Step 4: Check weather conditions in Portland, Oregon
            OpenWeather weather = new OpenWeather();
            JsonObject weatherResults = new JsonObject();
            
            try {
                // Portland, Oregon coordinates: 45.5152, -122.6784
                double lat = 45.5152;
                double lon = -122.6784;
                
                OpenWeather.CurrentWeatherData portlandWeather = weather.getCurrentWeather(lat, lon);
                
                JsonObject weatherInfo = new JsonObject();
                if (portlandWeather != null) {
                    weatherInfo.addProperty("temperature", portlandWeather.getTemperature());
                    weatherInfo.addProperty("feels_like", portlandWeather.getFeelsLike());
                    weatherInfo.addProperty("humidity", portlandWeather.getHumidity());
                    weatherInfo.addProperty("weather_condition", portlandWeather.getCondition());
                    weatherInfo.addProperty("weather_description", portlandWeather.getDescription());
                    weatherInfo.addProperty("wind_speed", portlandWeather.getWindSpeed());
                    weatherInfo.addProperty("cloudiness", portlandWeather.getCloudiness());
                    weatherInfo.addProperty("visibility", portlandWeather.getVisibility());
                    
                    // Create outdoor activity planning based on weather
                    JsonObject outdoorPlanning = new JsonObject();
                    double temp = portlandWeather.getTemperature();
                    int humidity = portlandWeather.getHumidity();
                    String condition = portlandWeather.getCondition();
                    
                    JsonArray outdoorActivities = new JsonArray();
                    JsonArray indoorBackups = new JsonArray();
                    
                    if (temp >= 65 && temp <= 80 && !condition.toLowerCase().contains("rain")) {
                        outdoorActivities.add("Composting demonstration in outdoor workshop area");
                        outdoorActivities.add("Urban gardening hands-on activity with container plants");
                        outdoorActivities.add("Rainwater collection system setup demonstration");
                        outdoorActivities.add("Solar cooking demonstration with portable solar cookers");
                        outdoorPlanning.addProperty("outdoor_suitability", "Excellent - perfect for all planned outdoor activities");
                    } else if (temp >= 50 && temp <= 85 && !condition.toLowerCase().contains("rain")) {
                        outdoorActivities.add("Composting demonstration (participants should dress warmly)");
                        outdoorActivities.add("Quick urban gardening demo with cold-weather considerations");
                        outdoorPlanning.addProperty("outdoor_suitability", "Good - outdoor activities possible with weather considerations");
                    } else {
                        outdoorPlanning.addProperty("outdoor_suitability", "Limited - focus on indoor alternatives");
                    }
                    
                    // Always plan indoor backups
                    indoorBackups.add("Indoor composting bin setup and maintenance demonstration");
                    indoorBackups.add("Seed starting and microgreens growing workshop");
                    indoorBackups.add("DIY natural cleaning products mixing session");
                    indoorBackups.add("Energy audit simulation using sample home data");
                    indoorBackups.add("Waste sorting and recycling education with sample materials");
                    
                    outdoorPlanning.add("recommended_outdoor_activities", outdoorActivities);
                    outdoorPlanning.add("indoor_backup_activities", indoorBackups);
                    
                    // Weather-specific recommendations
                    JsonArray weatherRecommendations = new JsonArray();
                    if (condition.toLowerCase().contains("rain")) {
                        weatherRecommendations.add("Perfect opportunity to discuss rainwater harvesting benefits");
                        weatherRecommendations.add("Indoor focus on water conservation and management topics");
                        weatherRecommendations.add("Use covered outdoor areas for brief composting demonstrations");
                    } else if (temp > 80) {
                        weatherRecommendations.add("Schedule outdoor activities for early morning (9-11 AM)");
                        weatherRecommendations.add("Provide shade and hydration stations for comfort");
                        weatherRecommendations.add("Perfect weather for solar energy demonstrations");
                    } else if (temp < 60) {
                        weatherRecommendations.add("Focus on cold-weather gardening and preservation techniques");
                        weatherRecommendations.add("Demonstrate energy conservation methods for cooler weather");
                        weatherRecommendations.add("Shorter outdoor sessions with warm-up breaks indoors");
                    } else {
                        weatherRecommendations.add("Ideal conditions for full outdoor sustainability demonstrations");
                        weatherRecommendations.add("Perfect for extended gardening and composting activities");
                    }
                    
                    if (humidity > 70) {
                        weatherRecommendations.add("High humidity ideal for discussing mold prevention in compost");
                        weatherRecommendations.add("Good conditions for demonstrating natural dehumidification methods");
                    }
                    
                    outdoorPlanning.add("weather_specific_recommendations", weatherRecommendations);
                    weatherInfo.add("activity_planning", outdoorPlanning);
                }
                
                weatherResults.add("portland_weather", weatherInfo);
                weatherResults.addProperty("location", "Portland, Oregon");
                weatherResults.addProperty("workshop_date", "August 15, 2025");
                weatherResults.addProperty("coordinates", "(" + lat + ", " + lon + ")");
                
            } catch (Exception e) {
                weatherResults.addProperty("error", "Failed to get weather data: " + e.getMessage());
            }
            
            output.add("weather_planning", weatherResults);
            
            // Step 5: Create comprehensive workshop planning summary
            JsonObject workshopSummary = new JsonObject();
            workshopSummary.addProperty("workshop_title", "Sustainable Living Workshop - Portland");
            workshopSummary.addProperty("date", "August 15, 2025");
            workshopSummary.addProperty("location", "Portland, Oregon");
            workshopSummary.addProperty("focus", "Environmental awareness through practical demonstrations");
            
            // Educational content organization
            JsonObject contentOrganization = new JsonObject();
            contentOrganization.addProperty("video_resources", "Structured curriculum from beginner to advanced levels");
            contentOrganization.addProperty("hands_on_demonstrations", "Eco-friendly product comparison and evaluation");
            contentOrganization.addProperty("current_events_discussion", "Environmental news for broader context");
            contentOrganization.addProperty("practical_activities", "Weather-dependent outdoor and indoor options");
            
            workshopSummary.add("content_structure", contentOrganization);
            
            // Workshop agenda recommendations
            JsonArray agendaRecommendations = new JsonArray();
            agendaRecommendations.add("9:00-9:30 AM: Welcome and environmental news discussion");
            agendaRecommendations.add("9:30-10:30 AM: Video presentations on sustainable living basics");
            agendaRecommendations.add("10:30-11:30 AM: Hands-on eco-product evaluation with Costco samples");
            agendaRecommendations.add("11:30 AM-12:30 PM: Outdoor composting/gardening OR indoor alternatives");
            agendaRecommendations.add("12:30-1:30 PM: Lunch break with sustainable meal discussion");
            agendaRecommendations.add("1:30-2:30 PM: Advanced sustainability videos and group discussion");
            agendaRecommendations.add("2:30-3:30 PM: Action planning and resource sharing");
            agendaRecommendations.add("3:30-4:00 PM: Wrap-up and take-home materials");
            
            workshopSummary.add("recommended_agenda", agendaRecommendations);
            
            // Success metrics and learning objectives
            JsonObject learningObjectives = new JsonObject();
            learningObjectives.addProperty("knowledge_gained", "Understanding of practical sustainability techniques");
            learningObjectives.addProperty("hands_on_skills", "Product evaluation and eco-friendly practices");
            learningObjectives.addProperty("awareness_building", "Connection between individual actions and global impact");
            learningObjectives.addProperty("practical_application", "Take-home strategies for sustainable living");
            
            workshopSummary.add("learning_objectives", learningObjectives);
            
            // Resource requirements
            JsonObject resourceNeeds = new JsonObject();
            resourceNeeds.addProperty("video_equipment", "Projector and speakers for educational content");
            resourceNeeds.addProperty("demonstration_materials", "Eco-friendly products from Costco for comparison");
            resourceNeeds.addProperty("outdoor_space", "Area for composting and gardening demonstrations");
            resourceNeeds.addProperty("indoor_backup", "Covered space for weather-dependent activities");
            resourceNeeds.addProperty("take_home_materials", "Resource guides and action planning templates");
            
            workshopSummary.add("resource_requirements", resourceNeeds);
            
            // Impact assessment framework
            JsonArray impactMetrics = new JsonArray();
            impactMetrics.add("Participant knowledge assessment before and after workshop");
            impactMetrics.add("Commitment to specific sustainable practices");
            impactMetrics.add("Resource sharing and community building among participants");
            impactMetrics.add("Follow-up survey on implementation of learned practices");
            impactMetrics.add("Environmental awareness and motivation level improvements");
            
            workshopSummary.add("impact_assessment_framework", impactMetrics);
            
            output.add("workshop_planning_summary", workshopSummary);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning sustainable living workshop: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
