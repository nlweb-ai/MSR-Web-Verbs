import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0053 {
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
            // Step 1: Search for highly-rated fiction books published in the last 5 years
            OpenLibrary library = new OpenLibrary();
            List<OpenLibrary.BookInfo> fictionBooks = library.search("fiction", "title,author_name,first_publish_year", "new", "en", 20, 1);
            
            JsonObject bookSelection = new JsonObject();
            OpenLibrary.BookInfo selectedBook = null;
            
            if (!fictionBooks.isEmpty()) {
                // Select the first book as our choice
                selectedBook = fictionBooks.get(0);
                bookSelection.addProperty("selected_book", selectedBook.title);
                bookSelection.addProperty("selection_criteria", "Highly-rated fiction book from recent years");
                
                JsonArray availableBooksArray = new JsonArray();
                for (int i = 0; i < Math.min(5, fictionBooks.size()); i++) {
                    JsonObject bookObj = new JsonObject();
                    bookObj.addProperty("title", fictionBooks.get(i).title);
                    availableBooksArray.add(bookObj);
                }
                bookSelection.add("alternative_options", availableBooksArray);
            } else {
                bookSelection.addProperty("error", "No fiction books found");
            }
            result.add("book_selection", bookSelection);
            
            // Step 2: Get weather forecast for Boston on August 22, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> bostonLocations = weather.getLocationsByName("Boston, MA");
            
            JsonObject weatherForecast = new JsonObject();
            if (!bostonLocations.isEmpty()) {
                OpenWeather.LocationData boston = bostonLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(boston.getLatitude(), boston.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("meeting_date", "August 22, 2025");
                
                // Find forecast for August 22, 2025, or closest available date
                JsonArray forecastArray = new JsonArray();
                boolean foundTargetDate = false;
                
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
                    
                    // Check if this is close to our target date
                    String dateStr = entry.getDateTime().toString();
                    if (dateStr.contains("2025-08-22")) {
                        forecastEntry.addProperty("is_meeting_date", true);
                        foundTargetDate = true;
                    }
                    
                    forecastArray.add(forecastEntry);
                }
                
                weatherForecast.add("forecasts", forecastArray);
                weatherForecast.addProperty("outdoor_meeting_recommendation", foundTargetDate ? "Check specific forecast for outdoor meeting feasibility" : "Weather data available for planning");
            } else {
                weatherForecast.addProperty("error", "Could not find location data for Boston, MA");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Find the closest coffee shop to meeting location
            maps_google_com maps = new maps_google_com(context);
            String meetingLocation = "Boston, MA"; // Using city center as meeting reference
            maps_google_com.NearestBusinessesResult coffeeShops = maps.get_nearestBusinesses(meetingLocation, "coffee shop", 1);
            
            JsonObject coffeeShopInfo = new JsonObject();
            coffeeShopInfo.addProperty("meeting_location", meetingLocation);
            coffeeShopInfo.addProperty("search_type", "closest coffee shop");
            
            if (!coffeeShops.businesses.isEmpty()) {
                maps_google_com.BusinessInfo closestCoffeeShop = coffeeShops.businesses.get(0);
                coffeeShopInfo.addProperty("name", closestCoffeeShop.name);
                coffeeShopInfo.addProperty("address", closestCoffeeShop.address);
                
                // Get directions from meeting location to coffee shop
                maps_google_com.DirectionResult direction = maps.get_direction(meetingLocation, closestCoffeeShop.address);
                coffeeShopInfo.addProperty("distance", direction.distance);
                coffeeShopInfo.addProperty("travel_time", direction.travelTime);
                coffeeShopInfo.addProperty("route", direction.route);
            } else {
                coffeeShopInfo.addProperty("error", "No coffee shops found near meeting location");
            }
            result.add("coffee_shop", coffeeShopInfo);
            
            // Step 4: Search for recent news articles about the chosen author
            JsonObject authorNews = new JsonObject();
            if (selectedBook != null) {
                News news = new News();
                
                // Extract author name from book title (this is a simplified approach)
                String authorQuery = selectedBook.title + " author";
                News.NewsResponse newsResponse = news.searchEverything(authorQuery, "en", 10);
                
                authorNews.addProperty("search_query", authorQuery);
                authorNews.addProperty("selected_book", selectedBook.title);
                authorNews.addProperty("total_results", newsResponse.totalResults);
                authorNews.addProperty("status", newsResponse.status);
                
                JsonArray articlesArray = new JsonArray();
                if (newsResponse.articles != null) {
                    int articleCount = Math.min(5, newsResponse.articles.size());
                    for (int i = 0; i < articleCount; i++) {
                        News.NewsArticle article = newsResponse.articles.get(i);
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("title", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("url", article.url);
                        articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : "Unknown");
                        articleObj.addProperty("source", article.source);
                        articlesArray.add(articleObj);
                    }
                }
                authorNews.add("articles", articlesArray);
                authorNews.addProperty("articles_found", articlesArray.size());
            } else {
                authorNews.addProperty("error", "No book selected, cannot search for author news");
            }
            result.add("author_news", authorNews);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("event", "Book Club Meeting");
            summary.addProperty("location", "Boston, Massachusetts");
            summary.addProperty("date", "August 22, 2025");
            summary.addProperty("book_selected", selectedBook != null);
            summary.addProperty("weather_forecast_available", !bostonLocations.isEmpty());
            summary.addProperty("coffee_shop_found", !coffeeShops.businesses.isEmpty());
            summary.addProperty("author_articles_found", authorNews.has("articles_found") ? 
                authorNews.get("articles_found").getAsInt() : 0);
            result.add("meeting_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
