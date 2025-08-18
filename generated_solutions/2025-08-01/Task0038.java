import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0038 {
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
            // Step 1: Get comprehensive news headlines for Chicago on August 2, 2025
            News news = new News();
            JsonObject newsResult = new JsonObject();
            
            try {
                // Get various news categories
                News.NewsResponse nationalNews = news.searchEverything("breaking news headlines today");
                News.NewsResponse chicagoNews = news.searchEverything("Chicago news local events Illinois");
                News.NewsResponse businessNews = news.searchEverything("business news markets economy today");
                News.NewsResponse weatherNews = news.searchEverything("weather forecast Chicago Illinois August");
                
                JsonArray allNewsArray = new JsonArray();
                
                // Process national news
                if (nationalNews != null && nationalNews.articles != null) {
                    for (News.NewsArticle article : nationalNews.articles) {
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("headline", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("source", article.source);
                        articleObj.addProperty("category", "National News");
                        articleObj.addProperty("priority", "High");
                        allNewsArray.add(articleObj);
                    }
                }
                
                // Process Chicago local news
                if (chicagoNews != null && chicagoNews.articles != null) {
                    for (News.NewsArticle article : chicagoNews.articles) {
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("headline", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("source", article.source);
                        articleObj.addProperty("category", "Chicago Local");
                        articleObj.addProperty("priority", "High");
                        allNewsArray.add(articleObj);
                    }
                }
                
                // Process business news
                if (businessNews != null && businessNews.articles != null) {
                    for (News.NewsArticle article : businessNews.articles) {
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("headline", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("source", article.source);
                        articleObj.addProperty("category", "Business & Economy");
                        articleObj.addProperty("priority", "Medium");
                        allNewsArray.add(articleObj);
                    }
                }
                
                // Process weather-related news
                if (weatherNews != null && weatherNews.articles != null) {
                    for (News.NewsArticle article : weatherNews.articles) {
                        JsonObject articleObj = new JsonObject();
                        articleObj.addProperty("headline", article.title);
                        articleObj.addProperty("description", article.description);
                        articleObj.addProperty("source", article.source);
                        articleObj.addProperty("category", "Weather News");
                        articleObj.addProperty("priority", "Medium");
                        allNewsArray.add(articleObj);
                    }
                }
                
                newsResult.add("daily_headlines", allNewsArray);
                newsResult.addProperty("total_articles", allNewsArray.size());
                newsResult.addProperty("briefing_date", "August 2, 2025");
                newsResult.addProperty("location", "Chicago, IL");
                
            } catch (Exception e) {
                newsResult.addProperty("error", "Failed to fetch news: " + e.getMessage());
            }
            
            output.add("news_briefing", newsResult);
            
            // Step 2: Get comprehensive weather forecast for Chicago (using coordinates)
            OpenWeather weather = new OpenWeather();
            JsonObject weatherResult = new JsonObject();
            
            try {
                // Chicago coordinates: 41.8781, -87.6298
                double lat = 41.8781;
                double lon = -87.6298;
                
                // Get current weather
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(lat, lon);
                
                JsonObject currentWeatherObj = new JsonObject();
                if (currentWeather != null) {
                    currentWeatherObj.addProperty("temperature", currentWeather.getTemperature());
                    currentWeatherObj.addProperty("feels_like", currentWeather.getFeelsLike());
                    currentWeatherObj.addProperty("humidity", currentWeather.getHumidity());
                    currentWeatherObj.addProperty("pressure", currentWeather.getPressure());
                    currentWeatherObj.addProperty("visibility", currentWeather.getVisibility());
                    currentWeatherObj.addProperty("weather_condition", currentWeather.getCondition());
                    currentWeatherObj.addProperty("weather_description", currentWeather.getDescription());
                    currentWeatherObj.addProperty("wind_speed", currentWeather.getWindSpeed());
                    currentWeatherObj.addProperty("wind_direction", currentWeather.getWindDirection());
                    currentWeatherObj.addProperty("cloudiness", currentWeather.getCloudiness());
                }
                
                weatherResult.add("current_weather", currentWeatherObj);
                weatherResult.addProperty("location", "Chicago, IL");
                weatherResult.addProperty("forecast_date", "August 2, 2025");
                weatherResult.addProperty("coordinates", "(" + lat + ", " + lon + ")");
                
            } catch (Exception e) {
                weatherResult.addProperty("error", "Failed to fetch weather data: " + e.getMessage());
            }
            
            output.add("weather_forecast", weatherResult);
            
            // Step 3: Get historical events for this date using Wikimedia
            Wikimedia wikimedia = new Wikimedia();
            JsonObject historicalEvents = new JsonObject();
            
            try {
                // Search for historical events on August 2
                Wikimedia.SearchResult august2Events = wikimedia.search("August 2 historical events", "en", 5);
                Wikimedia.SearchResult chicagoHistory = wikimedia.search("Chicago history events", "en", 4);
                Wikimedia.SearchResult todayInHistory = wikimedia.search("this day in history August", "en", 4);
                
                JsonArray eventsArray = new JsonArray();
                
                // Process August 2 historical events
                if (august2Events != null && august2Events.titles != null) {
                    for (String title : august2Events.titles) {
                        JsonObject eventObj = new JsonObject();
                        eventObj.addProperty("event_title", title);
                        eventObj.addProperty("category", "Historical Events");
                        eventObj.addProperty("relevance", "Date Specific");
                        eventsArray.add(eventObj);
                    }
                }
                
                // Process Chicago historical events
                if (chicagoHistory != null && chicagoHistory.titles != null) {
                    for (String title : chicagoHistory.titles) {
                        JsonObject eventObj = new JsonObject();
                        eventObj.addProperty("event_title", title);
                        eventObj.addProperty("category", "Chicago History");
                        eventObj.addProperty("relevance", "Location Specific");
                        eventsArray.add(eventObj);
                    }
                }
                
                // Process general "this day in history"
                if (todayInHistory != null && todayInHistory.titles != null) {
                    for (String title : todayInHistory.titles) {
                        JsonObject eventObj = new JsonObject();
                        eventObj.addProperty("event_title", title);
                        eventObj.addProperty("category", "This Day in History");
                        eventObj.addProperty("relevance", "General Historical");
                        eventsArray.add(eventObj);
                    }
                }
                
                historicalEvents.add("historical_events", eventsArray);
                historicalEvents.addProperty("total_events", eventsArray.size());
                historicalEvents.addProperty("date_focus", "August 2");
                
            } catch (Exception e) {
                historicalEvents.addProperty("error", "Failed to fetch historical events: " + e.getMessage());
            }
            
            output.add("historical_context", historicalEvents);
            
            // Step 4: Get Chicago music and local artist information using Spotify
            Spotify spotify = new Spotify();
            JsonObject musicSection = new JsonObject();
            
            try {
                // Search for Chicago-based playlists
                java.util.List<Spotify.SpotifyPlaylist> chicagoMusic = spotify.searchPlaylists("Chicago music local artists", null, 5);
                java.util.List<Spotify.SpotifyPlaylist> bluesMusic = spotify.searchPlaylists("Chicago blues music", null, 5);
                java.util.List<Spotify.SpotifyPlaylist> jazzMusic = spotify.searchPlaylists("Chicago jazz music", null, 5);
                
                JsonArray playlistsArray = new JsonArray();
                
                // Process Chicago music playlists
                if (chicagoMusic != null) {
                    for (Spotify.SpotifyPlaylist playlist : chicagoMusic) {
                        JsonObject playlistObj = new JsonObject();
                        playlistObj.addProperty("name", playlist.name);
                        playlistObj.addProperty("description", playlist.description);
                        playlistObj.addProperty("category", "Chicago Local Music");
                        playlistObj.addProperty("genre_focus", "Mixed Chicago Artists");
                        playlistsArray.add(playlistObj);
                    }
                }
                
                // Process Chicago blues playlists
                if (bluesMusic != null) {
                    for (Spotify.SpotifyPlaylist playlist : bluesMusic) {
                        JsonObject playlistObj = new JsonObject();
                        playlistObj.addProperty("name", playlist.name);
                        playlistObj.addProperty("description", playlist.description);
                        playlistObj.addProperty("category", "Chicago Blues");
                        playlistObj.addProperty("genre_focus", "Blues Music");
                        playlistsArray.add(playlistObj);
                    }
                }
                
                // Process Chicago jazz playlists
                if (jazzMusic != null) {
                    for (Spotify.SpotifyPlaylist playlist : jazzMusic) {
                        JsonObject playlistObj = new JsonObject();
                        playlistObj.addProperty("name", playlist.name);
                        playlistObj.addProperty("description", playlist.description);
                        playlistObj.addProperty("category", "Chicago Jazz");
                        playlistObj.addProperty("genre_focus", "Jazz Music");
                        playlistsArray.add(playlistObj);
                    }
                }
                
                musicSection.add("chicago_music_playlists", playlistsArray);
                musicSection.addProperty("total_playlists", playlistsArray.size());
                musicSection.addProperty("music_culture", "Chicago has a rich musical heritage in blues, jazz, and house music");
                
            } catch (Exception e) {
                musicSection.addProperty("error", "Failed to fetch music data: " + e.getMessage());
            }
            
            output.add("local_music_scene", musicSection);
            
            // Step 5: Create comprehensive daily briefing summary
            JsonObject dailyBriefing = new JsonObject();
            dailyBriefing.addProperty("briefing_title", "Chicago Daily News & Weather Briefing");
            dailyBriefing.addProperty("date", "Saturday, August 2, 2025");
            dailyBriefing.addProperty("location", "Chicago, Illinois");
            
            // Weather summary
            JsonObject weatherSummary = new JsonObject();
            if (weatherResult.has("current_weather")) {
                JsonObject currentTemp = weatherResult.get("current_weather").getAsJsonObject();
                if (currentTemp.has("temperature") && currentTemp.has("weather_description")) {
                    weatherSummary.addProperty("temperature", currentTemp.get("temperature").getAsDouble() + "°F");
                    weatherSummary.addProperty("conditions", currentTemp.get("weather_description").getAsString());
                    
                    if (currentTemp.has("feels_like")) {
                        weatherSummary.addProperty("feels_like", currentTemp.get("feels_like").getAsDouble() + "°F");
                    }
                    
                    if (currentTemp.has("humidity")) {
                        weatherSummary.addProperty("humidity", currentTemp.get("humidity").getAsInt() + "%");
                    }
                    
                    if (currentTemp.has("wind_speed")) {
                        weatherSummary.addProperty("wind_speed", currentTemp.get("wind_speed").getAsDouble() + " mph");
                    }
                }
            }
            
            dailyBriefing.add("weather_summary", weatherSummary);
            
            // News highlights
            JsonArray newsHighlights = new JsonArray();
            if (newsResult.has("daily_headlines")) {
                JsonArray headlines = newsResult.get("daily_headlines").getAsJsonArray();
                for (int i = 0; i < Math.min(10, headlines.size()); i++) {
                    JsonObject headline = headlines.get(i).getAsJsonObject();
                    JsonObject highlight = new JsonObject();
                    highlight.addProperty("headline", headline.get("headline").getAsString());
                    highlight.addProperty("category", headline.get("category").getAsString());
                    if (headline.has("priority")) {
                        highlight.addProperty("priority", headline.get("priority").getAsString());
                    }
                    newsHighlights.add(highlight);
                }
            }
            
            dailyBriefing.add("top_news_highlights", newsHighlights);
            
            // Historical context for the day
            JsonArray todaysHistory = new JsonArray();
            if (historicalEvents.has("historical_events")) {
                JsonArray events = historicalEvents.get("historical_events").getAsJsonArray();
                for (int i = 0; i < Math.min(3, events.size()); i++) {
                    JsonObject event = events.get(i).getAsJsonObject();
                    todaysHistory.add(event.get("event_title").getAsString());
                }
            }
            
            if (todaysHistory.size() > 0) {
                dailyBriefing.add("on_this_day_in_history", todaysHistory);
            }
            
            // Local culture highlight
            JsonObject cultureHighlight = new JsonObject();
            cultureHighlight.addProperty("music_scene", "Chicago's legendary blues and jazz heritage");
            
            if (musicSection.has("chicago_music_playlists")) {
                JsonArray playlists = musicSection.get("chicago_music_playlists").getAsJsonArray();
                if (playlists.size() > 0) {
                    JsonObject featuredPlaylist = playlists.get(0).getAsJsonObject();
                    cultureHighlight.addProperty("featured_playlist", featuredPlaylist.get("name").getAsString());
                    cultureHighlight.addProperty("playlist_category", featuredPlaylist.get("category").getAsString());
                }
            }
            
            dailyBriefing.add("local_culture_spotlight", cultureHighlight);
            
            // Daily recommendations
            JsonArray recommendations = new JsonArray();
            
            // Weather-based recommendations
            if (weatherSummary.has("temperature")) {
                double temp = Double.parseDouble(weatherSummary.get("temperature").getAsString().replace("°F", ""));
                if (temp >= 70 && temp <= 85) {
                    recommendations.add("Great weather for outdoor activities along Lake Michigan");
                    recommendations.add("Perfect day for walking through Millennium Park");
                } else if (temp >= 60 && temp < 70) {
                    recommendations.add("Comfortable weather for exploring Chicago's museums and indoor attractions");
                    recommendations.add("Great day for the Architecture Boat Tour");
                } else if (temp > 85) {
                    recommendations.add("Hot day - consider indoor activities during peak afternoon hours");
                    recommendations.add("Stay hydrated and seek shade during outdoor activities");
                } else {
                    recommendations.add("Cooler weather - perfect for cozy indoor activities and hot coffee");
                }
            }
            
            // Music recommendations
            recommendations.add("Explore Chicago's music scene with local blues and jazz venues");
            recommendations.add("Check out live music events happening this weekend");
            recommendations.add("Visit historic music venues like Buddy Guy's Legends or Green Mill Cocktail Lounge");
            
            // General Chicago recommendations
            recommendations.add("Take a walk along the Chicago Riverwalk for beautiful city views");
            recommendations.add("Visit Millennium Park and see Cloud Gate (The Bean)");
            recommendations.add("Explore one of Chicago's many world-class museums");
            
            dailyBriefing.add("daily_recommendations", recommendations);
            
            // Create a summary of key information
            JsonObject briefingSummary = new JsonObject();
            briefingSummary.addProperty("weather_outlook", "Check current conditions for outdoor planning");
            briefingSummary.addProperty("news_focus", "Stay informed with local and national developments");
            briefingSummary.addProperty("cultural_highlight", "Immerse yourself in Chicago's rich musical heritage");
            briefingSummary.addProperty("historical_context", "Learn about significant events that happened on this day");
            
            dailyBriefing.add("briefing_summary", briefingSummary);
            
            output.add("daily_briefing_summary", dailyBriefing);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while creating the daily briefing: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
