import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0057 {
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
        
        try {
            // Step 1: Search for children's science books and select 5 for camp library
            OpenLibrary library = new OpenLibrary();
            List<OpenLibrary.BookInfo> scienceBooks = library.search("children science", "title,author_name,subject", "new", "en", 20, 1);
            
            JsonObject campLibrary = new JsonObject();
            campLibrary.addProperty("library_theme", "Children's Science Education");
            campLibrary.addProperty("target_books", 5);
            campLibrary.addProperty("age_group", "Summer camp kids");
            
            JsonArray booksArray = new JsonArray();
            int bookCount = Math.min(5, scienceBooks.size());
            
            for (int i = 0; i < bookCount; i++) {
                OpenLibrary.BookInfo book = scienceBooks.get(i);
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                bookObj.addProperty("educational_value", "Science concepts for young learners");
                bookObj.addProperty("camp_activity_potential", "High - hands-on learning");
                booksArray.add(bookObj);
            }
            
            campLibrary.add("selected_books", booksArray);
            campLibrary.addProperty("books_acquired", bookCount);
            
            if (bookCount == 0) {
                campLibrary.addProperty("note", "No specific children's science books found, general science books may be available");
            }
            
            result.add("camp_library", campLibrary);
            
            // Step 2: Get weather forecast for Chicago for August 12-16, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> chicagoLocations = weather.getLocationsByName("Chicago, IL");
            
            JsonObject weatherForecast = new JsonObject();
            if (!chicagoLocations.isEmpty()) {
                OpenWeather.LocationData chicago = chicagoLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(chicago.getLatitude(), chicago.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("camp_dates", "August 12-16, 2025");
                
                JsonArray forecastArray = new JsonArray();
                int campDays = 0;
                
                for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                    JsonObject forecastEntry = new JsonObject();
                    forecastEntry.addProperty("date_time", entry.getDateTime().toString());
                    forecastEntry.addProperty("condition", entry.getCondition());
                    forecastEntry.addProperty("description", entry.getDescription());
                    forecastEntry.addProperty("temperature", entry.getTemperature());
                    forecastEntry.addProperty("temp_min", entry.getTempMin());
                    forecastEntry.addProperty("temp_max", entry.getTempMax());
                    forecastEntry.addProperty("humidity", entry.getHumidity());
                    forecastEntry.addProperty("wind_speed", entry.getWindSpeed());
                    
                    // Check if this is during camp week
                    String dateStr = entry.getDateTime().toString();
                    if (dateStr.contains("2025-08-12") || dateStr.contains("2025-08-13") || 
                        dateStr.contains("2025-08-14") || dateStr.contains("2025-08-15") || 
                        dateStr.contains("2025-08-16")) {
                        forecastEntry.addProperty("is_camp_day", true);
                        forecastEntry.addProperty("outdoor_experiment_suitability", "Check conditions for outdoor activities");
                        campDays++;
                    }
                    
                    forecastArray.add(forecastEntry);
                }
                
                weatherForecast.add("forecasts", forecastArray);
                weatherForecast.addProperty("camp_planning_note", "Weather conditions for outdoor science experiments");
                weatherForecast.addProperty("camp_days_covered", campDays);
            } else {
                weatherForecast.addProperty("error", "Could not find location data for Chicago, IL");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Find 3 nearest science museums to camp location
            maps_google_com maps = new maps_google_com(context);
            String campLocation = "Chicago, IL"; // Using city center as camp location reference
            maps_google_com.NearestBusinessesResult scienceMuseums = maps.get_nearestBusinesses(campLocation, "science museum", 3);
            
            JsonObject museumsInfo = new JsonObject();
            museumsInfo.addProperty("camp_location", campLocation);
            museumsInfo.addProperty("search_type", "science museums");
            museumsInfo.addProperty("requested_count", 3);
            
            JsonArray museumsArray = new JsonArray();
            for (maps_google_com.BusinessInfo museum : scienceMuseums.businesses) {
                JsonObject museumObj = new JsonObject();
                museumObj.addProperty("name", museum.name);
                museumObj.addProperty("address", museum.address);
                
                // Get directions from camp to museum
                maps_google_com.DirectionResult direction = maps.get_direction(campLocation, museum.address);
                museumObj.addProperty("distance", direction.distance);
                museumObj.addProperty("travel_time", direction.travelTime);
                museumObj.addProperty("route", direction.route);
                museumObj.addProperty("field_trip_potential", "Excellent educational opportunity");
                
                museumsArray.add(museumObj);
            }
            
            museumsInfo.add("museums", museumsArray);
            museumsInfo.addProperty("museums_found", museumsArray.size());
            museumsInfo.addProperty("educational_impact", "Field trips to enhance science learning");
            result.add("science_museums", museumsInfo);
            
            // Step 4: Search for recent science news for daily discussions
            News news = new News();
            News.NewsResponse scienceNews = news.searchEverything("science discovery breakthrough", "en", 15);
            
            JsonObject dailyDiscussions = new JsonObject();
            dailyDiscussions.addProperty("topic", "Recent Science News");
            dailyDiscussions.addProperty("purpose", "Daily discussion topics for campers");
            dailyDiscussions.addProperty("camp_duration", "5 days (August 12-16, 2025)");
            dailyDiscussions.addProperty("total_results", scienceNews.totalResults);
            dailyDiscussions.addProperty("status", scienceNews.status);
            
            JsonArray articlesArray = new JsonArray();
            if (scienceNews.articles != null) {
                int articleCount = Math.min(10, scienceNews.articles.size());
                for (int i = 0; i < articleCount; i++) {
                    News.NewsArticle article = scienceNews.articles.get(i);
                    JsonObject articleObj = new JsonObject();
                    articleObj.addProperty("title", article.title);
                    articleObj.addProperty("description", article.description);
                    articleObj.addProperty("url", article.url);
                    articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : "Unknown");
                    articleObj.addProperty("source", article.source);
                    articleObj.addProperty("discussion_value", "Inspiring scientific curiosity");
                    articleObj.addProperty("age_appropriate", "Suitable for camp discussions");
                    articlesArray.add(articleObj);
                }
            }
            
            dailyDiscussions.add("news_articles", articlesArray);
            dailyDiscussions.addProperty("articles_collected", articlesArray.size());
            dailyDiscussions.addProperty("daily_rotation", "2 articles per day for engaging discussions");
            result.add("daily_discussions", dailyDiscussions);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("program", "Science-Themed Summer Camp");
            summary.addProperty("location", "Chicago, Illinois");
            summary.addProperty("dates", "August 12-16, 2025");
            summary.addProperty("target_audience", "Kids interested in science");
            summary.addProperty("library_books_selected", bookCount);
            summary.addProperty("weather_forecast_available", !chicagoLocations.isEmpty());
            summary.addProperty("science_museums_found", scienceMuseums.businesses.size());
            summary.addProperty("discussion_articles_collected", articlesArray.size());
            summary.addProperty("camp_readiness", "Fully prepared for scientific exploration");
            result.add("camp_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
