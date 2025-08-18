import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0003 {
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
        
        // Step 1: Check the latest technology news to stay informed about industry trends
        News news = new News();
        JsonObject newsInfo = new JsonObject();
        
        try {
            News.NewsResponse techNews = news.getTopHeadlines("us", "technology");
            
            newsInfo.addProperty("status", techNews.status);
            newsInfo.addProperty("total_results", techNews.totalResults);
            
            JsonArray articlesArray = new JsonArray();
            for (News.NewsArticle article : techNews.articles) {
                JsonObject articleObj = new JsonObject();
                articleObj.addProperty("title", article.title);
                articleObj.addProperty("description", article.description);
                articleObj.addProperty("url", article.url);
                articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : null);
                articleObj.addProperty("source", article.source);
                articlesArray.add(articleObj);
            }
            newsInfo.add("articles", articlesArray);
        } catch (Exception e) {
            newsInfo.addProperty("error", "Failed to get tech news: " + e.getMessage());
        }
        result.add("tech_news", newsInfo);
        
        // Step 2: Check current weather in San Francisco for the interview day (August 5, 2025)
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // First get the location coordinates for San Francisco
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("San Francisco, CA");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData location = locations.get(0);
                double lat = location.getLatitude();
                double lon = location.getLongitude();
                
                // Get current weather for interview preparation
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(lat, lon);
                
                weatherInfo.addProperty("city", currentWeather.getCityName());
                weatherInfo.addProperty("country", currentWeather.getCountry());
                weatherInfo.addProperty("date", currentWeather.getDate().toString());
                weatherInfo.addProperty("condition", currentWeather.getCondition());
                weatherInfo.addProperty("description", currentWeather.getDescription());
                weatherInfo.addProperty("temperature", currentWeather.getTemperature());
                weatherInfo.addProperty("feels_like", currentWeather.getFeelsLike());
                weatherInfo.addProperty("humidity", currentWeather.getHumidity());
                weatherInfo.addProperty("wind_speed", currentWeather.getWindSpeed());
                weatherInfo.addProperty("cloudiness", currentWeather.getCloudiness());
                
                // Also get forecast to check weather for August 5, 2025
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                JsonArray forecastArray = new JsonArray();
                for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                    JsonObject forecastObj = new JsonObject();
                    forecastObj.addProperty("date_time", entry.getDateTime().toString());
                    forecastObj.addProperty("condition", entry.getCondition());
                    forecastObj.addProperty("description", entry.getDescription());
                    forecastObj.addProperty("temperature", entry.getTemperature());
                    forecastObj.addProperty("humidity", entry.getHumidity());
                    forecastArray.add(forecastObj);
                }
                weatherInfo.add("forecast", forecastArray);
            } else {
                weatherInfo.addProperty("error", "Could not find location data for San Francisco, CA");
            }
        } catch (Exception e) {
            weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
        }
        result.add("weather_info", weatherInfo);
        
        // Step 3: Get directions from Union Square hotel to Google headquarters
        maps_google_com maps = new maps_google_com(context);
        maps_google_com.DirectionResult directions = maps.get_direction("Union Square, San Francisco, CA", "Google headquarters, Mountain View, CA");
        
        JsonObject directionsInfo = new JsonObject();
        directionsInfo.addProperty("travel_time", directions.travelTime);
        directionsInfo.addProperty("distance", directions.distance);
        directionsInfo.addProperty("route", directions.route);
        result.add("directions", directionsInfo);
        
        // Step 4: Search for educational videos about cloud computing
        youtube_com youtube = new youtube_com(context);
        List<youtube_com.YouTubeVideoInfo> cloudVideos = youtube.searchVideos("cloud computing tutorial");
        
        JsonArray videosArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : cloudVideos) {
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
            videosArray.add(videoObj);
        }
        
        JsonObject educationInfo = new JsonObject();
        educationInfo.add("cloud_computing_videos", videosArray);
        result.add("educational_content", educationInfo);
        
        return result;
    }
}
