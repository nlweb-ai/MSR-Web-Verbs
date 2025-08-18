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


public class Task0034 {
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
            // Step 1: Search for latest technology news from the past week
            News news = new News();
            LocalDate fromDate = LocalDate.of(2025, 7, 29); // Past week from August 5, 2025
            LocalDate toDate = LocalDate.of(2025, 8, 5);
            
            JsonArray newsArray = new JsonArray();
            try {
                // Search for technology news
                News.NewsResponse techNews = news.searchEverything("technology AI artificial intelligence tech", 
                                                                null, null, null, null, 
                                                                fromDate, toDate, "en", 
                                                                "publishedAt", 20, 1);
                
                if (techNews != null && techNews.articles != null) {
                    for (News.NewsArticle article : techNews.articles) {
                        // Filter for relevant tech articles
                        if (article.title != null && 
                            (article.title.toLowerCase().contains("tech") ||
                             article.title.toLowerCase().contains("ai") ||
                             article.title.toLowerCase().contains("artificial intelligence") ||
                             article.title.toLowerCase().contains("software") ||
                             article.title.toLowerCase().contains("data") ||
                             article.title.toLowerCase().contains("cybersecurity") ||
                             article.title.toLowerCase().contains("innovation"))) {
                            
                            JsonObject articleObj = new JsonObject();
                            articleObj.addProperty("title", article.title);
                            articleObj.addProperty("description", article.description);
                            articleObj.addProperty("url", article.url);
                            articleObj.addProperty("source", article.source);
                            articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                            articleObj.addProperty("category", "Technology");
                            newsArray.add(articleObj);
                        }
                    }
                }
                
                // Search for additional tech news categories
                if (newsArray.size() < 10) {
                    News.NewsResponse startupNews = news.searchEverything("startup venture capital tech industry", 
                                                                        null, null, null, null, 
                                                                        fromDate, toDate, "en", 
                                                                        "publishedAt", 10, 1);
                    
                    if (startupNews != null && startupNews.articles != null) {
                        for (News.NewsArticle article : startupNews.articles) {
                            if (newsArray.size() >= 15) break;
                            
                            JsonObject articleObj = new JsonObject();
                            articleObj.addProperty("title", article.title);
                            articleObj.addProperty("description", article.description);
                            articleObj.addProperty("url", article.url);
                            articleObj.addProperty("source", article.source);
                            articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                            articleObj.addProperty("category", "Startup/Business");
                            newsArray.add(articleObj);
                        }
                    }
                }
                
            } catch (Exception e) {
                JsonObject newsError = new JsonObject();
                newsError.addProperty("error", "Failed to get tech news: " + e.getMessage());
                newsArray.add(newsError);
            }
            
            output.add("tech_news", newsArray);
            
            // Step 2: Find background information on trending tech topics using Wikimedia
            Wikimedia wikimedia = new Wikimedia();
            JsonArray techTopicFacts = new JsonArray();
            
            try {
                // Search for trending tech topics
                String[] techTopics = {
                    "Artificial Intelligence", "Machine Learning", "Blockchain", "Cloud Computing", 
                    "Cybersecurity", "Internet of Things", "5G Technology", "Quantum Computing"
                };
                
                for (String topic : techTopics) {
                    try {
                        Wikimedia.SearchResult searchResult = wikimedia.search(topic, "en", 2);
                        if (searchResult != null && searchResult.titles != null && !searchResult.titles.isEmpty()) {
                            for (String title : searchResult.titles) {
                                Wikimedia.PageInfo pageInfo = wikimedia.getPage(title);
                                if (pageInfo != null) {
                                    JsonObject topicObj = new JsonObject();
                                    topicObj.addProperty("topic", topic);
                                    topicObj.addProperty("title", pageInfo.title);
                                    topicObj.addProperty("url", pageInfo.htmlUrl);
                                    topicObj.addProperty("lastModified", pageInfo.lastModified != null ? pageInfo.lastModified.toString() : null);
                                    techTopicFacts.add(topicObj);
                                    break; // Only take first result for each topic
                                }
                            }
                        }
                    } catch (Exception e) {
                        System.err.println("Failed to get info for topic: " + topic + " - " + e.getMessage());
                    }
                }
                
            } catch (Exception e) {
                JsonObject factsError = new JsonObject();
                factsError.addProperty("error", "Failed to get tech topic background: " + e.getMessage());
                techTopicFacts.add(factsError);
            }
            
            output.add("tech_background", techTopicFacts);
            
            // Step 3: Check weather forecast for New York on August 5, 2025
            OpenWeather weather = new OpenWeather();
            JsonObject weatherInfo = new JsonObject();
            
            try {
                List<OpenWeather.LocationData> locations = weather.getLocationsByName("New York, NY");
                if (!locations.isEmpty()) {
                    OpenWeather.LocationData nyLocation = locations.get(0);
                    double lat = nyLocation.getLatitude();
                    double lon = nyLocation.getLongitude();
                    
                    OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(lat, lon);
                    
                    JsonObject currentWeatherObj = new JsonObject();
                    currentWeatherObj.addProperty("city", currentWeather.getCityName());
                    currentWeatherObj.addProperty("condition", currentWeather.getCondition());
                    currentWeatherObj.addProperty("description", currentWeather.getDescription());
                    currentWeatherObj.addProperty("temperature", currentWeather.getTemperature());
                    currentWeatherObj.addProperty("humidity", currentWeather.getHumidity());
                    currentWeatherObj.addProperty("windSpeed", currentWeather.getWindSpeed());
                    
                    OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                    
                    JsonArray forecastArray = new JsonArray();
                    if (forecast != null && forecast.getForecasts() != null) {
                        for (int i = 0; i < Math.min(8, forecast.getForecasts().size()); i++) {
                            OpenWeather.ForecastEntry entry = forecast.getForecasts().get(i);
                            JsonObject forecastEntry = new JsonObject();
                            forecastEntry.addProperty("dateTime", entry.getDateTime().toString());
                            forecastEntry.addProperty("condition", entry.getCondition());
                            forecastEntry.addProperty("temperature", entry.getTemperature());
                            forecastEntry.addProperty("description", entry.getDescription());
                            forecastArray.add(forecastEntry);
                        }
                    }
                    
                    weatherInfo.add("current_weather", currentWeatherObj);
                    weatherInfo.add("forecast", forecastArray);
                    
                } else {
                    weatherInfo.addProperty("error", "Could not find location data for New York, NY");
                }
            } catch (Exception e) {
                weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
            }
            
            output.add("weather_update", weatherInfo);
            
            // Step 4: Send summary message to team's group chat using Microsoft Teams
            teams_microsoft_com teams = new teams_microsoft_com(context);
            
            // Prepare team message content
            StringBuilder messageContent = new StringBuilder();
            messageContent.append("📰 TECH NEWS DIGEST - August 5, 2025\\n\\n");
            
            // Add top news headlines
            messageContent.append("🔥 TOP TECH NEWS:\\n");
            int newsCount = Math.min(5, newsArray.size());
            for (int i = 0; i < newsCount; i++) {
                JsonObject article = newsArray.get(i).getAsJsonObject();
                if (article.has("title")) {
                    messageContent.append("• ").append(article.get("title").getAsString()).append("\\n");
                }
            }
            
            // Add weather update
            if (weatherInfo.has("current_weather")) {
                JsonObject currentWeather = weatherInfo.get("current_weather").getAsJsonObject();
                messageContent.append("\\n🌤️ NYC WEATHER UPDATE:\\n");
                messageContent.append("• Current: ").append(currentWeather.get("condition").getAsString());
                messageContent.append(" (").append(Math.round(currentWeather.get("temperature").getAsDouble()));
                messageContent.append("°C)\\n");
            }
            
            // Add trending topics count
            messageContent.append("\\n📚 Background info available on ").append(techTopicFacts.size());
            messageContent.append(" trending tech topics\\n");
            messageContent.append("\\nFull digest attached. Have a great day team! 🚀");
            
            String teamEmail = "tech-team@company.com"; // Placeholder team email
            teams_microsoft_com.MessageStatus messageStatus = teams.sendToGroupChat(teamEmail, messageContent.toString());
            
            JsonObject teamsResult = new JsonObject();
            teamsResult.addProperty("recipient", messageStatus.recipientEmail);
            teamsResult.addProperty("message_preview", messageContent.toString().substring(0, Math.min(100, messageContent.length())) + "...");
            teamsResult.addProperty("status", messageStatus.status);
            
            output.add("teams_message", teamsResult);
            
            // Step 5: Create comprehensive digest summary
            JsonObject digestSummary = new JsonObject();
            digestSummary.addProperty("digest_date", "August 5, 2025");
            digestSummary.addProperty("location", "New York");
            digestSummary.addProperty("team_target", "Tech Team");
            digestSummary.addProperty("news_articles_found", newsArray.size());
            digestSummary.addProperty("background_topics_researched", techTopicFacts.size());
            digestSummary.addProperty("weather_included", weatherInfo.has("current_weather"));
            digestSummary.addProperty("message_sent", messageStatus.status.equals("success"));
            
            JsonObject contentSummary = new JsonObject();
            contentSummary.addProperty("top_categories", "AI, Startups, Cybersecurity, Innovation");
            contentSummary.addProperty("weather_condition", weatherInfo.has("current_weather") ? 
                weatherInfo.get("current_weather").getAsJsonObject().get("condition").getAsString() : "Unknown");
            contentSummary.addProperty("recommended_action", "Review full articles for team discussion topics");
            
            digestSummary.add("content_summary", contentSummary);
            output.add("digest_summary", digestSummary);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while preparing the tech digest: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
