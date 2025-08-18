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


public class Task0005 {
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
        
        // Step 1: Search for recent space exploration news to get current developments
        News news = new News();
        JsonObject newsInfo = new JsonObject();
        
        try {
            News.NewsResponse spaceNews = news.searchEverything("space exploration", "en", 10);
            
            newsInfo.addProperty("status", spaceNews.status);
            newsInfo.addProperty("total_results", spaceNews.totalResults);
            
            JsonArray articlesArray = new JsonArray();
            for (News.NewsArticle article : spaceNews.articles) {
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
            newsInfo.addProperty("error", "Failed to get space exploration news: " + e.getMessage());
        }
        result.add("space_news", newsInfo);
        
        // Step 2: Get NASA APOD and NEO data for research enhancement
        Nasa nasa = new Nasa();
        JsonObject nasaInfo = new JsonObject();
        
        try {
            // Get Astronomy Picture of the Day
            Nasa.ApodResult apod = nasa.getApod(null, true);
            JsonObject apodObj = new JsonObject();
            apodObj.addProperty("title", apod.title);
            apodObj.addProperty("url", apod.url);
            apodObj.addProperty("explanation", apod.explanation);
            apodObj.addProperty("date", apod.date != null ? apod.date.toString() : null);
            nasaInfo.add("astronomy_picture", apodObj);
            
            // Get Near Earth Objects data
            List<Nasa.NeoResult> neoData = nasa.getNeoBrowse();
            JsonArray neoArray = new JsonArray();
            for (Nasa.NeoResult neo : neoData) {
                JsonObject neoObj = new JsonObject();
                neoObj.addProperty("name", neo.name);
                neoObj.addProperty("id", neo.id);
                neoObj.addProperty("close_approach_date", neo.closeApproachDate != null ? neo.closeApproachDate.toString() : null);
                neoObj.addProperty("estimated_diameter_km", neo.estimatedDiameterKm);
                if (neo.missDistance != null) {
                    JsonObject distanceObj = new JsonObject();
                    distanceObj.addProperty("amount", neo.missDistance.amount);
                    distanceObj.addProperty("currency", neo.missDistance.currency);
                    neoObj.add("miss_distance", distanceObj);
                }
                neoArray.add(neoObj);
            }
            nasaInfo.add("near_earth_objects", neoArray);
        } catch (Exception e) {
            nasaInfo.addProperty("error", "Failed to get NASA data: " + e.getMessage());
        }
        result.add("nasa_data", nasaInfo);
        
        // Step 3: Search for educational videos about space missions
        youtube_com youtube = new youtube_com(context);
        List<youtube_com.YouTubeVideoInfo> spaceVideos = youtube.searchVideos("space missions NASA");
        
        JsonArray videosArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : spaceVideos) {
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
        educationInfo.add("space_mission_videos", videosArray);
        result.add("educational_content", educationInfo);
        
        // Step 4: Get weather forecast for Houston (NASA Johnson Space Center location)
        OpenWeather weather = new OpenWeather();
        JsonObject weatherInfo = new JsonObject();
        
        try {
            // First get the location coordinates for Houston
            List<OpenWeather.LocationData> locations = weather.getLocationsByName("Houston, TX");
            if (!locations.isEmpty()) {
                OpenWeather.LocationData location = locations.get(0);
                double lat = location.getLatitude();
                double lon = location.getLongitude();
                
                // Get weather forecast for the visit period
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(lat, lon);
                
                weatherInfo.addProperty("city", forecast.getCityName());
                weatherInfo.addProperty("country", forecast.getCountry());
                weatherInfo.addProperty("latitude", forecast.getLatitude());
                weatherInfo.addProperty("longitude", forecast.getLongitude());
                
                JsonArray forecastArray = new JsonArray();
                for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                    JsonObject forecastObj = new JsonObject();
                    forecastObj.addProperty("date_time", entry.getDateTime().toString());
                    forecastObj.addProperty("condition", entry.getCondition());
                    forecastObj.addProperty("description", entry.getDescription());
                    forecastObj.addProperty("temperature", entry.getTemperature());
                    forecastObj.addProperty("temp_min", entry.getTempMin());
                    forecastObj.addProperty("temp_max", entry.getTempMax());
                    forecastObj.addProperty("humidity", entry.getHumidity());
                    forecastObj.addProperty("wind_speed", entry.getWindSpeed());
                    forecastArray.add(forecastObj);
                }
                weatherInfo.add("forecast", forecastArray);
            } else {
                weatherInfo.addProperty("error", "Could not find location data for Houston, TX");
            }
        } catch (Exception e) {
            weatherInfo.addProperty("error", "Failed to get weather forecast: " + e.getMessage());
        }
        result.add("houston_weather", weatherInfo);
        
        // Step 5: Search for flights from LAX to Houston for field trip on August 5-8, 2025
        alaskaair_com flights = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 5);
        LocalDate returnDate = LocalDate.of(2025, 8, 8);
        
        alaskaair_com.SearchFlightsResult flightSearch = flights.searchFlights("LAX", "IAH", outboundDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        if (flightSearch.message != null) {
            flightInfo.addProperty("message", flightSearch.message);
        } else if (flightSearch.flightInfo != null) {
            JsonArray flightArray = new JsonArray();
            for (String flight : flightSearch.flightInfo.flights) {
                flightArray.add(flight);
            }
            flightInfo.add("flights", flightArray);
            if (flightSearch.flightInfo.price != null) {
                JsonObject priceObj = new JsonObject();
                priceObj.addProperty("amount", flightSearch.flightInfo.price.amount);
                priceObj.addProperty("currency", flightSearch.flightInfo.price.currency);
                flightInfo.add("price", priceObj);
            }
        }
        result.add("flight_search", flightInfo);
        
        return result;
    }
}
