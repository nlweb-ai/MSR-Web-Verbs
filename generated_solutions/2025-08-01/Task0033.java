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


public class Task0033 {
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
            // Step 1: Search for top country music playlists using Spotify
            Spotify spotify = new Spotify();
            List<Spotify.SpotifyPlaylist> countryPlaylists = spotify.searchPlaylists("country music Nashville", "US", 10);
            List<Spotify.SpotifyPlaylist> topCountryPlaylists = spotify.searchPlaylists("top country hits", "US", 10);
            List<Spotify.SpotifyPlaylist> classicCountryPlaylists = spotify.searchPlaylists("classic country", "US", 5);
            
            JsonArray playlistArray = new JsonArray();
            
            // Add Nashville country playlists
            if (countryPlaylists != null) {
                for (Spotify.SpotifyPlaylist playlist : countryPlaylists) {
                    JsonObject playlistObj = new JsonObject();
                    playlistObj.addProperty("name", playlist.name);
                    playlistObj.addProperty("description", playlist.description);
                    playlistObj.addProperty("owner", playlist.ownerName);
                    playlistObj.addProperty("totalTracks", playlist.totalTracks);
                    playlistObj.addProperty("category", "Nashville Country");
                    playlistArray.add(playlistObj);
                }
            }
            
            // Add top country hits playlists
            if (topCountryPlaylists != null) {
                for (Spotify.SpotifyPlaylist playlist : topCountryPlaylists) {
                    JsonObject playlistObj = new JsonObject();
                    playlistObj.addProperty("name", playlist.name);
                    playlistObj.addProperty("description", playlist.description);
                    playlistObj.addProperty("owner", playlist.ownerName);
                    playlistObj.addProperty("totalTracks", playlist.totalTracks);
                    playlistObj.addProperty("category", "Top Country Hits");
                    playlistArray.add(playlistObj);
                }
            }
            
            // Add classic country playlists
            if (classicCountryPlaylists != null) {
                for (Spotify.SpotifyPlaylist playlist : classicCountryPlaylists) {
                    JsonObject playlistObj = new JsonObject();
                    playlistObj.addProperty("name", playlist.name);
                    playlistObj.addProperty("description", playlist.description);
                    playlistObj.addProperty("owner", playlist.ownerName);
                    playlistObj.addProperty("totalTracks", playlist.totalTracks);
                    playlistObj.addProperty("category", "Classic Country");
                    playlistArray.add(playlistObj);
                }
            }
            
            output.add("music_playlists", playlistArray);
            
            // Step 2: Find famous music venues and museums in Nashville using Google Maps
            maps_google_com maps = new maps_google_com(context);
            
            // Search for music venues
            maps_google_com.NearestBusinessesResult musicVenues = maps.get_nearestBusinesses("Nashville, TN", "music venue", 10);
            maps_google_com.NearestBusinessesResult musicMuseums = maps.get_nearestBusinesses("Nashville, TN", "music museum", 8);
            maps_google_com.NearestBusinessesResult recordingStudios = maps.get_nearestBusinesses("Nashville, TN", "recording studio", 5);
            
            JsonArray venuesArray = new JsonArray();
            
            // Add music venues
            if (musicVenues != null && musicVenues.businesses != null) {
                for (maps_google_com.BusinessInfo venue : musicVenues.businesses) {
                    JsonObject venueObj = new JsonObject();
                    venueObj.addProperty("name", venue.name);
                    venueObj.addProperty("address", venue.address);
                    venueObj.addProperty("type", "Music Venue");
                    venueObj.addProperty("tour_priority", "High");
                    venuesArray.add(venueObj);
                }
            }
            
            // Add music museums
            if (musicMuseums != null && musicMuseums.businesses != null) {
                for (maps_google_com.BusinessInfo museum : musicMuseums.businesses) {
                    JsonObject museumObj = new JsonObject();
                    museumObj.addProperty("name", museum.name);
                    museumObj.addProperty("address", museum.address);
                    museumObj.addProperty("type", "Music Museum");
                    museumObj.addProperty("tour_priority", "High");
                    venuesArray.add(museumObj);
                }
            }
            
            // Add recording studios
            if (recordingStudios != null && recordingStudios.businesses != null) {
                for (maps_google_com.BusinessInfo studio : recordingStudios.businesses) {
                    JsonObject studioObj = new JsonObject();
                    studioObj.addProperty("name", studio.name);
                    studioObj.addProperty("address", studio.address);
                    studioObj.addProperty("type", "Recording Studio");
                    studioObj.addProperty("tour_priority", "Medium");
                    venuesArray.add(studioObj);
                }
            }
            
            output.add("music_venues", venuesArray);
            
            // Step 3: Find recent articles about country music events in Nashville
            News news = new News();
            LocalDate fromDate = LocalDate.of(2025, 7, 1); // Recent articles from July 2025
            LocalDate toDate = LocalDate.of(2025, 8, 9);   // Up to tour date
            
            JsonArray newsArray = new JsonArray();
            try {
                // Search for Nashville country music events
                News.NewsResponse countryMusicNews = news.searchEverything("Nashville country music events concerts", 
                                                                        null, null, null, null, 
                                                                        fromDate, toDate, "en", 
                                                                        "publishedAt", 15, 1);
                
                if (countryMusicNews != null && countryMusicNews.articles != null) {
                    for (News.NewsArticle article : countryMusicNews.articles) {
                        // Filter for articles about Nashville music events
                        if (article.title != null && 
                            (article.title.toLowerCase().contains("nashville") ||
                             article.title.toLowerCase().contains("country music") ||
                             article.title.toLowerCase().contains("grand ole opry") ||
                             article.title.toLowerCase().contains("music city") ||
                             article.title.toLowerCase().contains("concert") ||
                             article.title.toLowerCase().contains("festival"))) {
                            
                            JsonObject articleObj = new JsonObject();
                            articleObj.addProperty("title", article.title);
                            articleObj.addProperty("description", article.description);
                            articleObj.addProperty("url", article.url);
                            articleObj.addProperty("source", article.source);
                            articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                            articleObj.addProperty("relevance", "High");
                            newsArray.add(articleObj);
                        }
                    }
                }
                
                // If we need more articles, search more broadly
                if (newsArray.size() < 8) {
                    News.NewsResponse musicNews = news.searchEverything("country music Tennessee", 
                                                                      null, null, null, null, 
                                                                      fromDate, toDate, "en", 
                                                                      "publishedAt", 10, 1);
                    
                    if (musicNews != null && musicNews.articles != null) {
                        for (News.NewsArticle article : musicNews.articles) {
                            if (newsArray.size() >= 15) break; // Limit total articles
                            
                            JsonObject articleObj = new JsonObject();
                            articleObj.addProperty("title", article.title);
                            articleObj.addProperty("description", article.description);
                            articleObj.addProperty("url", article.url);
                            articleObj.addProperty("source", article.source);
                            articleObj.addProperty("publishedAt", article.publishedAt != null ? article.publishedAt.toString() : null);
                            articleObj.addProperty("relevance", "Medium");
                            newsArray.add(articleObj);
                        }
                    }
                }
                
            } catch (Exception e) {
                JsonObject newsError = new JsonObject();
                newsError.addProperty("error", "Failed to get country music news: " + e.getMessage());
                newsArray.add(newsError);
            }
            
            output.add("music_news", newsArray);
            
            // Step 4: Check weather forecast for Nashville on August 9, 2025
            OpenWeather weather = new OpenWeather();
            JsonObject weatherInfo = new JsonObject();
            
            try {
                // Get Nashville coordinates
                List<OpenWeather.LocationData> locations = weather.getLocationsByName("Nashville, TN");
                if (!locations.isEmpty()) {
                    OpenWeather.LocationData nashvilleLocation = locations.get(0);
                    double lat = nashvilleLocation.getLatitude();
                    double lon = nashvilleLocation.getLongitude();
                    
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
                    
                    // Get 5-day forecast to cover August 9, 2025
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
                    
                    // Walking tour weather recommendations
                    String tourRecommendation;
                    String clothingRecommendation;
                    
                    double temp = currentWeather.getTemperature();
                    double windSpeed = currentWeather.getWindSpeed();
                    int humidity = currentWeather.getHumidity();
                    
                    if (temp > 25 && humidity > 70) {
                        tourRecommendation = "Hot and humid conditions - plan frequent breaks in air-conditioned venues. Start early morning or late afternoon.";
                        clothingRecommendation = "Light, breathable clothing, sun hat, sunscreen, and plenty of water.";
                    } else if (temp > 20) {
                        tourRecommendation = "Perfect weather for walking! Comfortable temperatures for outdoor exploration.";
                        clothingRecommendation = "Comfortable walking shoes, light layers, and a light jacket for indoor venues.";
                    } else if (temp > 15) {
                        tourRecommendation = "Cool weather - ideal for extended walking with comfortable layers.";
                        clothingRecommendation = "Comfortable walking shoes, layers, and a medium jacket.";
                    } else {
                        tourRecommendation = "Cool conditions - indoor venues will be more comfortable. Plan shorter outdoor segments.";
                        clothingRecommendation = "Warm layers, comfortable walking shoes, and a warm jacket.";
                    }
                    
                    if (windSpeed > 15) {
                        tourRecommendation += " Windy conditions - secure loose items and consider indoor alternatives.";
                    }
                    
                    weatherInfo.addProperty("tour_recommendation", tourRecommendation);
                    weatherInfo.addProperty("clothing_recommendation", clothingRecommendation);
                    
                } else {
                    weatherInfo.addProperty("error", "Could not find location data for Nashville, TN");
                }
            } catch (Exception e) {
                weatherInfo.addProperty("error", "Failed to get weather information: " + e.getMessage());
            }
            
            output.add("weather_forecast", weatherInfo);
            
            // Step 5: Create comprehensive tour plan
            JsonObject tourPlan = new JsonObject();
            tourPlan.addProperty("tour_name", "Nashville Music Heritage Walking Tour");
            tourPlan.addProperty("date", "August 9, 2025");
            tourPlan.addProperty("city", "Nashville, Tennessee");
            tourPlan.addProperty("theme", "Country Music and Nashville's Musical Heritage");
            tourPlan.addProperty("duration", "6-8 hours");
            tourPlan.addProperty("difficulty", "Moderate Walking");
            
            // Create suggested route
            JsonArray routeStops = new JsonArray();
            
            // Add high-priority venues to route
            int stopNumber = 1;
            if (musicVenues != null && musicVenues.businesses != null) {
                for (int i = 0; i < Math.min(4, musicVenues.businesses.size()); i++) {
                    maps_google_com.BusinessInfo venue = musicVenues.businesses.get(i);
                    JsonObject stop = new JsonObject();
                    stop.addProperty("stop_number", stopNumber++);
                    stop.addProperty("name", venue.name);
                    stop.addProperty("address", venue.address);
                    stop.addProperty("type", "Music Venue");
                    stop.addProperty("estimated_time", "45-60 minutes");
                    routeStops.add(stop);
                }
            }
            
            if (musicMuseums != null && musicMuseums.businesses != null) {
                for (int i = 0; i < Math.min(3, musicMuseums.businesses.size()); i++) {
                    maps_google_com.BusinessInfo museum = musicMuseums.businesses.get(i);
                    JsonObject stop = new JsonObject();
                    stop.addProperty("stop_number", stopNumber++);
                    stop.addProperty("name", museum.name);
                    stop.addProperty("address", museum.address);
                    stop.addProperty("type", "Music Museum");
                    stop.addProperty("estimated_time", "60-90 minutes");
                    routeStops.add(stop);
                }
            }
            
            tourPlan.add("route_stops", routeStops);
            
            // Music recommendations for the tour
            JsonObject musicRecommendations = new JsonObject();
            
            JsonArray preWalkPlaylists = new JsonArray();
            if (countryPlaylists != null && !countryPlaylists.isEmpty()) {
                for (int i = 0; i < Math.min(3, countryPlaylists.size()); i++) {
                    preWalkPlaylists.add(countryPlaylists.get(i).name);
                }
            }
            musicRecommendations.add("pre_tour_playlists", preWalkPlaylists);
            
            JsonArray walkingPlaylists = new JsonArray();
            if (topCountryPlaylists != null && !topCountryPlaylists.isEmpty()) {
                for (int i = 0; i < Math.min(2, topCountryPlaylists.size()); i++) {
                    walkingPlaylists.add(topCountryPlaylists.get(i).name);
                }
            }
            musicRecommendations.add("walking_playlists", walkingPlaylists);
            
            tourPlan.add("music_recommendations", musicRecommendations);
            
            // Tour tips and preparation
            JsonObject tourTips = new JsonObject();
            tourTips.addProperty("best_start_time", "9:00 AM or 2:00 PM");
            tourTips.addProperty("group_size", "8-12 people maximum");
            tourTips.addProperty("preparation", "Download offline maps, charge devices, bring portable phone charger");
            tourTips.addProperty("what_to_bring", "Comfortable walking shoes, water bottle, camera, notebook for venue information");
            
            if (newsArray.size() > 0) {
                tourTips.addProperty("current_events", "Check recent news for special events or closures - " + newsArray.size() + " relevant articles found");
            }
            
            tourPlan.add("tour_tips", tourTips);
            
            output.add("tour_plan", tourPlan);
            
        } catch (Exception e) {
            JsonObject errorObj = new JsonObject();
            errorObj.addProperty("error", "An error occurred while planning the Nashville music tour: " + e.getMessage());
            output.add("error_details", errorObj);
        }
        
        return output;
    }
}
