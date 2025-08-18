import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0058 {
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
            // Step 1: Find 5 coworking spaces or event venues near Midtown Manhattan
            maps_google_com maps = new maps_google_com(context);
            String midtownLocation = "Midtown Manhattan, New York, NY";
            maps_google_com.NearestBusinessesResult eventVenues = maps.get_nearestBusinesses(midtownLocation, "coworking space event venue", 5);
            
            JsonObject venuesInfo = new JsonObject();
            venuesInfo.addProperty("search_area", midtownLocation);
            venuesInfo.addProperty("venue_type", "Coworking spaces and event venues");
            venuesInfo.addProperty("requested_count", 5);
            
            JsonArray venuesArray = new JsonArray();
            for (maps_google_com.BusinessInfo venue : eventVenues.businesses) {
                JsonObject venueObj = new JsonObject();
                venueObj.addProperty("name", venue.name);
                venueObj.addProperty("address", venue.address);
                
                // Get directions from Midtown center to venue
                maps_google_com.DirectionResult direction = maps.get_direction(midtownLocation, venue.address);
                venueObj.addProperty("distance_from_midtown", direction.distance);
                venueObj.addProperty("travel_time", direction.travelTime);
                venueObj.addProperty("route", direction.route);
                venueObj.addProperty("networking_suitability", "Professional tech networking environment");
                
                venuesArray.add(venueObj);
            }
            
            venuesInfo.add("venues", venuesArray);
            venuesInfo.addProperty("venues_found", venuesArray.size());
            result.add("event_venues", venuesInfo);
            
            // Step 2: Get weather forecast for New York City on August 21, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> nycLocations = weather.getLocationsByName("New York, NY");
            
            JsonObject weatherForecast = new JsonObject();
            if (!nycLocations.isEmpty()) {
                OpenWeather.LocationData nyc = nycLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(nyc.getLatitude(), nyc.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("event_date", "August 21, 2025");
                
                JsonArray forecastArray = new JsonArray();
                boolean foundEventDate = false;
                
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
                    
                    // Check if this is the event date
                    String dateStr = entry.getDateTime().toString();
                    if (dateStr.contains("2025-08-21")) {
                        forecastEntry.addProperty("is_event_date", true);
                        forecastEntry.addProperty("outdoor_networking_feasible", "Check conditions for outdoor activities");
                        foundEventDate = true;
                    }
                    
                    forecastArray.add(forecastEntry);
                }
                
                weatherForecast.add("forecasts", forecastArray);
                weatherForecast.addProperty("event_planning_note", foundEventDate ? "Weather available for event date" : "General forecast for planning");
            } else {
                weatherForecast.addProperty("error", "Could not find location data for New York, NY");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Create tech-themed playlist using Spotify
            Spotify spotify = new Spotify();
            
            // Search for technology and electronic music
            Spotify.SpotifySearchResult techMusic = spotify.searchItems("technology electronic", "track", "US", 20, 0, null);
            
            JsonObject playlist = new JsonObject();
            playlist.addProperty("theme", "Tech Networking Event");
            playlist.addProperty("target_songs", 15);
            playlist.addProperty("genre", "Technology and Electronic");
            
            JsonArray playlistArray = new JsonArray();
            int songCount = 0;
            
            if (techMusic.tracks != null) {
                for (Spotify.SpotifyTrack track : techMusic.tracks) {
                    if (songCount >= 15) break;
                    
                    JsonObject songObj = new JsonObject();
                    songObj.addProperty("name", track.name);
                    songObj.addProperty("id", track.id);
                    songObj.addProperty("uri", track.uri);
                    
                    JsonArray artistsArray = new JsonArray();
                    if (track.artistNames != null) {
                        for (String artist : track.artistNames) {
                            artistsArray.add(artist);
                        }
                    }
                    songObj.add("artists", artistsArray);
                    
                    songObj.addProperty("album", track.albumName);
                    songObj.addProperty("duration_ms", track.duration != null ? track.duration.toMillis() : 0);
                    songObj.addProperty("popularity", track.popularity);
                    songObj.addProperty("preview_url", track.previewUrl);
                    songObj.addProperty("event_vibe", "Professional tech networking atmosphere");
                    
                    playlistArray.add(songObj);
                    songCount++;
                }
            }
            
            playlist.addProperty("actual_songs", songCount);
            playlist.add("songs", playlistArray);
            
            if (techMusic.errorMessage != null) {
                playlist.addProperty("search_error", techMusic.errorMessage);
            }
            
            result.add("event_playlist", playlist);
            
            // Step 4: Search for recent AI startup news for discussion topics
            News news = new News();
            News.NewsResponse aiStartupNews = news.searchEverything("AI startup artificial intelligence", "en", 15);
            
            JsonObject discussionTopics = new JsonObject();
            discussionTopics.addProperty("topic_category", "AI Startups and Innovation");
            discussionTopics.addProperty("purpose", "Networking conversation starters");
            discussionTopics.addProperty("target_audience", "Tech professionals and entrepreneurs");
            discussionTopics.addProperty("total_results", aiStartupNews.totalResults);
            discussionTopics.addProperty("status", aiStartupNews.status);
            
            JsonArray articlesArray = new JsonArray();
            if (aiStartupNews.articles != null) {
                int articleCount = Math.min(10, aiStartupNews.articles.size());
                for (int i = 0; i < articleCount; i++) {
                    News.NewsArticle article = aiStartupNews.articles.get(i);
                    JsonObject articleObj = new JsonObject();
                    articleObj.addProperty("title", article.title);
                    articleObj.addProperty("description", article.description);
                    articleObj.addProperty("url", article.url);
                    articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : "Unknown");
                    articleObj.addProperty("source", article.source);
                    articleObj.addProperty("discussion_value", "High relevance for tech networking");
                    articleObj.addProperty("conversation_starter", "Perfect for AI and startup discussions");
                    articlesArray.add(articleObj);
                }
            }
            
            discussionTopics.add("news_articles", articlesArray);
            discussionTopics.addProperty("articles_prepared", articlesArray.size());
            discussionTopics.addProperty("networking_impact", "Current AI trends for meaningful conversations");
            result.add("discussion_topics", discussionTopics);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("event", "Tech Networking Event");
            summary.addProperty("location", "New York City");
            summary.addProperty("date", "August 21, 2025");
            summary.addProperty("focus_area", "Technology and AI");
            summary.addProperty("venues_found", eventVenues.businesses.size());
            summary.addProperty("weather_forecast_available", !nycLocations.isEmpty());
            summary.addProperty("playlist_songs", songCount);
            summary.addProperty("discussion_articles", articlesArray.size());
            summary.addProperty("event_readiness", "Fully prepared for tech networking in NYC");
            result.add("networking_event_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
