import java.nio.file.Paths;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0056 {
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
            // Step 1: Create a custom country music playlist using Spotify
            Spotify spotify = new Spotify();
            Spotify.SpotifySearchResult countryMusic = spotify.searchItems("country music", "track", "US", 30, 0, null);
            
            JsonObject playlist = new JsonObject();
            playlist.addProperty("theme", "Country Music Birthday Party");
            playlist.addProperty("target_songs", 20);
            playlist.addProperty("genre", "Country Music");
            
            JsonArray playlistArray = new JsonArray();
            int songCount = 0;
            
            if (countryMusic.tracks != null) {
                for (Spotify.SpotifyTrack track : countryMusic.tracks) {
                    if (songCount >= 20) break;
                    
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
                    songObj.addProperty("party_vibe", "Country music celebration");
                    
                    playlistArray.add(songObj);
                    songCount++;
                }
            }
            
            playlist.addProperty("actual_songs", songCount);
            playlist.add("songs", playlistArray);
            
            if (countryMusic.errorMessage != null) {
                playlist.addProperty("search_error", countryMusic.errorMessage);
            }
            
            result.add("party_playlist", playlist);
            
            // Step 2: Get weather forecast for Nashville on August 23, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> nashvilleLocations = weather.getLocationsByName("Nashville, TN");
            
            JsonObject weatherForecast = new JsonObject();
            if (!nashvilleLocations.isEmpty()) {
                OpenWeather.LocationData nashville = nashvilleLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(nashville.getLatitude(), nashville.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("party_date", "August 23, 2025");
                
                JsonArray forecastArray = new JsonArray();
                boolean foundPartyDate = false;
                
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
                    
                    // Check if this is the party date
                    String dateStr = entry.getDateTime().toString();
                    if (dateStr.contains("2025-08-23")) {
                        forecastEntry.addProperty("is_party_date", true);
                        foundPartyDate = true;
                    }
                    
                    forecastArray.add(forecastEntry);
                }
                
                weatherForecast.add("forecasts", forecastArray);
                weatherForecast.addProperty("outdoor_party_feasible", foundPartyDate ? "Check specific conditions" : "Weather data for planning");
            } else {
                weatherForecast.addProperty("error", "Could not find location data for Nashville, TN");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Find 3 best-rated bakeries near party venue
            maps_google_com maps = new maps_google_com(context);
            String partyVenue = "Nashville, TN"; // Using city center as party venue reference
            maps_google_com.NearestBusinessesResult bakeries = maps.get_nearestBusinesses(partyVenue, "bakery", 3);
            
            JsonObject bakeriesInfo = new JsonObject();
            bakeriesInfo.addProperty("party_venue", partyVenue);
            bakeriesInfo.addProperty("search_type", "best-rated bakeries");
            bakeriesInfo.addProperty("requested_count", 3);
            
            JsonArray bakeriesArray = new JsonArray();
            for (maps_google_com.BusinessInfo bakery : bakeries.businesses) {
                JsonObject bakeryObj = new JsonObject();
                bakeryObj.addProperty("name", bakery.name);
                bakeryObj.addProperty("address", bakery.address);
                
                // Get directions from venue to bakery
                maps_google_com.DirectionResult direction = maps.get_direction(partyVenue, bakery.address);
                bakeryObj.addProperty("distance", direction.distance);
                bakeryObj.addProperty("travel_time", direction.travelTime);
                bakeryObj.addProperty("route", direction.route);
                bakeryObj.addProperty("recommendation", "Custom birthday cake options");
                
                bakeriesArray.add(bakeryObj);
            }
            
            bakeriesInfo.add("bakeries", bakeriesArray);
            bakeriesInfo.addProperty("bakeries_found", bakeriesArray.size());
            result.add("local_bakeries", bakeriesInfo);
            
            // Step 4: Research country music history for trivia games
            OpenLibrary library = new OpenLibrary();
            List<OpenLibrary.BookInfo> countryMusicBooks = library.search("country music history", "title,author_name", "new", "en", 10, 1);
            
            JsonObject triviaResearch = new JsonObject();
            triviaResearch.addProperty("research_topic", "Country Music History");
            triviaResearch.addProperty("purpose", "Trivia game preparation");
            triviaResearch.addProperty("target_books", 3);
            
            JsonArray booksArray = new JsonArray();
            int bookCount = Math.min(3, countryMusicBooks.size());
            
            for (int i = 0; i < bookCount; i++) {
                OpenLibrary.BookInfo book = countryMusicBooks.get(i);
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                bookObj.addProperty("trivia_potential", "High - Country music historical facts");
                bookObj.addProperty("party_relevance", "Perfect for music-themed trivia");
                booksArray.add(bookObj);
            }
            
            triviaResearch.add("reference_books", booksArray);
            triviaResearch.addProperty("books_selected", bookCount);
            
            if (bookCount == 0) {
                triviaResearch.addProperty("note", "No specific country music history books found, general music books may be available");
            }
            
            result.add("trivia_research", triviaResearch);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("event", "Music-Themed Birthday Party");
            summary.addProperty("location", "Nashville, Tennessee");
            summary.addProperty("date", "August 23, 2025");
            summary.addProperty("theme", "Country Music");
            summary.addProperty("playlist_songs", songCount);
            summary.addProperty("weather_forecast_available", !nashvilleLocations.isEmpty());
            summary.addProperty("bakeries_found", bakeries.businesses.size());
            summary.addProperty("trivia_books_selected", bookCount);
            summary.addProperty("party_planning_status", "Ready to celebrate in Music City");
            result.add("party_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
