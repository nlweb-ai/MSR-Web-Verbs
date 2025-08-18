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


public class Task0032 {
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
            // Step 1: Get the Astronomy Picture of the Day for August 15, 2025
            Nasa nasa = new Nasa();
            Nasa.ApodResult apod = nasa.getApod("2025-08-01", true); // Get HD version for printing
            
            JsonObject apodInfo = new JsonObject();
            if (apod != null) {
                apodInfo.addProperty("title", apod.title);
                apodInfo.addProperty("url", apod.url);
                apodInfo.addProperty("explanation", apod.explanation);
                apodInfo.addProperty("date", apod.date != null ? apod.date.toString() : null);
                apodInfo.addProperty("suitable_for_printing", true);
            } else {
                apodInfo.addProperty("error", "Could not retrieve Astronomy Picture of the Day");
            }
            output.add("astronomy_picture", apodInfo);
            
            // Step 2: Check weather forecast for San Francisco on August 15, 2025
            OpenWeather weather = new OpenWeather();
            JsonObject weatherInfo = new JsonObject();
            
            try {
                // Get San Francisco coordinates
                List<OpenWeather.LocationData> locations = weather.getLocationsByName("San Francisco, CA");
                if (!locations.isEmpty()) {
                    OpenWeather.LocationData sfLocation = locations.get(0);
                    double lat = sfLocation.getLatitude();
                    double lon = sfLocation.getLongitude();
                    
                    // Get current weather
                    OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(lat, lon);
                    
                    JsonObject currentWeatherObj = new JsonObject();
                    currentWeatherObj.addProperty("city", currentWeather.getCityName());
                    currentWeatherObj.addProperty("country", currentWeather.getCountry());
                    currentWeatherObj.addProperty("condition", currentWeather.getCondition());
                    currentWeatherObj.addProperty("description", currentWeather.getDescription());
                    currentWeatherObj.addProperty("temperature", currentWeather.getTemperature());
                    currentWeatherObj.addProperty("humidity", currentWeather.getHumidity());
                    currentWeatherObj.addProperty("windSpeed", currentWeather.getWindSpeed());
                    
                    // Get 5-day forecast to cover August 15, 2025
                    OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                    
                    JsonArray forecastArray = new JsonArray();
                    if (forecast != null && forecast.getForecasts() != null) {
                        for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                            JsonObject forecastEntry = new JsonObject();
                            forecastEntry.addProperty("dateTime", entry.getDateTime().toString());
                            forecastEntry.addProperty("condition", entry.getCondition());
                            forecastEntry.addProperty("description", entry.getDescription());
                            forecastEntry.addProperty("temperature", entry.getTemperature());
                            forecastEntry.addProperty("humidity", entry.getHumidity());
                            forecastEntry.addProperty("windSpeed", entry.getWindSpeed());
                            forecastArray.add(forecastEntry);
                        }
                    }
                    
                    weatherInfo.add("current_weather", currentWeatherObj);
                    weatherInfo.add("forecast", forecastArray);
                    
                    // Outdoor activity recommendation
                    String activityRecommendation;
                    if (currentWeather.getTemperature() > 20 && currentWeather.getWindSpeed() < 10) {
                        activityRecommendation = "Excellent conditions for outdoor science activities! Perfect temperature and low wind.";
                    } else if (currentWeather.getTemperature() > 15) {
                        activityRecommendation = "Good conditions for outdoor activities with light jackets or sweaters.";
                    } else {
                        activityRecommendation = "Consider indoor activities or covered outdoor spaces due to cooler temperatures.";
                    }
                    weatherInfo.addProperty("outdoor_activity_recommendation", activityRecommendation);
                    
                } else {
                    weatherInfo.addProperty("error", "Could not find location data for San Francisco, CA");
                }
            } catch (Exception e) {
                weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
            }
            output.add("weather_forecast", weatherInfo);
            
            // Step 3: Find recent science news articles suitable for children
            News news = new News();
            LocalDate fromDate = LocalDate.of(2025, 7, 1); // Recent articles from July 2025
            LocalDate toDate = LocalDate.of(2025, 8, 1);   // Up to current date
            
            JsonArray newsArray = new JsonArray();
            try {
                // Search for kid-friendly science topics
                News.NewsResponse scienceNews = news.searchEverything("science kids children space astronomy", 
                                                                    null, null, null, null, 
                                                                    fromDate, toDate, "en", 
                                                                    "publishedAt", 15, 1);
                
                if (scienceNews != null && scienceNews.articles != null) {
                    for (News.NewsArticle article : scienceNews.articles) {
                        // Filter for articles that seem appropriate for children
                        if (article.title != null && 
                            (article.title.toLowerCase().contains("space") ||
                             article.title.toLowerCase().contains("science") ||
                             article.title.toLowerCase().contains("discovery") ||
                             article.title.toLowerCase().contains("nasa") ||
                             article.title.toLowerCase().contains("planet") ||
                             article.title.toLowerCase().contains("star"))) {
                            
                            JsonObject articleObj = new JsonObject();
                            articleObj.addProperty("title", article.title);
                            articleObj.addProperty("description", article.description);
                            articleObj.addProperty("url", article.url);
                            articleObj.addProperty("source", article.source);
                            articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                            articleObj.addProperty("kid_friendly_topic", true);
                            newsArray.add(articleObj);
                        }
                    }
                }
                
                // If we don't have enough kid-friendly articles, search more broadly
                if (newsArray.size() < 5) {
                    News.NewsResponse generalScienceNews = news.searchEverything("NASA space discovery", 
                                                                               null, null, null, null, 
                                                                               fromDate, toDate, "en", 
                                                                               "publishedAt", 10, 1);
                    
                    if (generalScienceNews != null && generalScienceNews.articles != null) {
                        for (News.NewsArticle article : generalScienceNews.articles) {
                            if (newsArray.size() >= 10) break; // Limit total articles
                            
                            JsonObject articleObj = new JsonObject();
                            articleObj.addProperty("title", article.title);
                            articleObj.addProperty("description", article.description);
                            articleObj.addProperty("url", article.url);
                            articleObj.addProperty("source", article.source);
                            articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                            articleObj.addProperty("kid_friendly_topic", false);
                            newsArray.add(articleObj);
                        }
                    }
                }
                
            } catch (Exception e) {
                JsonObject newsError = new JsonObject();
                newsError.addProperty("error", "Failed to get science news: " + e.getMessage());
                newsArray.add(newsError);
            }
            
            output.add("science_news", newsArray);
            
            // Step 4: Find fun facts about the solar system using Wikimedia
            Wikimedia wikimedia = new Wikimedia();
            JsonArray solarSystemFacts = new JsonArray();
            
            try {
                // Search for solar system related articles
                String[] solarSystemTopics = {
                    "Solar System", "Jupiter", "Mars", "Saturn", "Moon", 
                    "International Space Station", "Asteroid", "Comet", "Galaxy", "Sun"
                };
                
                for (String topic : solarSystemTopics) {
                    try {
                        Wikimedia.SearchResult searchResult = wikimedia.search(topic, "en", 3);
                        if (searchResult != null && searchResult.titles != null && !searchResult.titles.isEmpty()) {
                            for (String title : searchResult.titles) {
                                Wikimedia.PageInfo pageInfo = wikimedia.getPage(title);
                                if (pageInfo != null) {
                                    JsonObject factObj = new JsonObject();
                                    factObj.addProperty("topic", topic);
                                    factObj.addProperty("title", pageInfo.title);
                                    factObj.addProperty("url", pageInfo.htmlUrl);
                                    factObj.addProperty("lastModified", pageInfo.lastModified != null ? pageInfo.lastModified.toString() : null);
                                    factObj.addProperty("suitable_for_kids", true);
                                    solarSystemFacts.add(factObj);
                                    break; // Only take the first result for each topic
                                }
                            }
                        }
                    } catch (Exception e) {
                        // Continue with other topics if one fails
                        System.err.println("Failed to get info for topic: " + topic + " - " + e.getMessage());
                    }
                }
                
            } catch (Exception e) {
                JsonObject factsError = new JsonObject();
                factsError.addProperty("error", "Failed to get solar system facts: " + e.getMessage());
                solarSystemFacts.add(factsError);
            }
            
            output.add("solar_system_facts", solarSystemFacts);
            
            // Step 5: Create event summary and handout content
            JsonObject eventSummary = new JsonObject();
            eventSummary.addProperty("event_name", "Science Outreach Event for Kids");
            eventSummary.addProperty("date", "August 15, 2025");
            eventSummary.addProperty("location", "San Francisco");
            eventSummary.addProperty("target_audience", "Children");
            eventSummary.addProperty("theme", "Space and Astronomy");
            
            JsonObject handoutContent = new JsonObject();
            
            // Handout sections
            if (apod != null) {
                JsonObject pictureSection = new JsonObject();
                pictureSection.addProperty("section_title", "Today's Amazing Space Picture");
                pictureSection.addProperty("picture_title", apod.title);
                pictureSection.addProperty("fun_explanation", "Look at this incredible picture from space! " + 
                    (apod.explanation != null ? apod.explanation.substring(0, Math.min(200, apod.explanation.length())) + "..." : ""));
                handoutContent.add("space_picture_section", pictureSection);
            }
            
            JsonObject weatherSection = new JsonObject();
            weatherSection.addProperty("section_title", "Weather for Our Science Adventure");
            weatherSection.addProperty("weather_summary", "Perfect day to explore science in San Francisco!");
            handoutContent.add("weather_section", weatherSection);
            
            JsonObject newsSection = new JsonObject();
            newsSection.addProperty("section_title", "Cool Science News This Month");
            newsSection.addProperty("news_count", newsArray.size());
            handoutContent.add("news_section", newsSection);
            
            JsonObject factsSection = new JsonObject();
            factsSection.addProperty("section_title", "Amazing Solar System Facts");
            factsSection.addProperty("facts_count", solarSystemFacts.size());
            handoutContent.add("facts_section", factsSection);
            
            eventSummary.add("handout_content", handoutContent);
            output.add("event_summary", eventSummary);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning the science event: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
