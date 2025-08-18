import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0062 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Find top 5 most popular tracks by Taylor Swift on Spotify
            Spotify spotify = new Spotify();
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems("Taylor Swift", "track", "US", 50, 0, null);
            JsonArray topTracksArr = new JsonArray();
            List<Integer> trackReleaseYears = new ArrayList<>();
            
            if (spotifyResult.tracks != null && !spotifyResult.tracks.isEmpty()) {
                // Sort by popularity and take top 5
                spotifyResult.tracks.sort((a, b) -> Integer.compare(b.popularity, a.popularity));
                int trackCount = Math.min(5, spotifyResult.tracks.size());
                
                for (int i = 0; i < trackCount; i++) {
                    Spotify.SpotifyTrack track = spotifyResult.tracks.get(i);
                    JsonObject trackObj = new JsonObject();
                    trackObj.addProperty("name", track.name);
                    trackObj.addProperty("album", track.albumName);
                    trackObj.addProperty("popularity", track.popularity);
                    if (track.releaseDate != null) {
                        trackObj.addProperty("release_date", track.releaseDate.toString());
                        trackReleaseYears.add(track.releaseDate.getYear());
                    }
                    topTracksArr.add(trackObj);
                }
            }
            result.add("top_5_tracks", topTracksArr);

            // 2. Search for books about Taylor Swift using OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            List<OpenLibrary.BookInfo> books = openLibrary.search("Taylor Swift", "title,first_publish_year", "new", "en", 20, 1);
            JsonArray booksArr = new JsonArray();
            List<JsonObject> matchingBooks = new ArrayList<>();
            
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                
                // Extract year from book title or use a default approach
                // Since OpenLibrary BookInfo only contains title, we'll try to parse year from title
                Integer bookYear = extractYearFromTitle(book.title);
                if (bookYear != null) {
                    bookObj.addProperty("release_year", bookYear);
                    
                    // 3. Check if book release year matches any track release year
                    if (trackReleaseYears.contains(bookYear)) {
                        bookObj.addProperty("matches_track_year", true);
                        matchingBooks.add(bookObj);
                    } else {
                        bookObj.addProperty("matches_track_year", false);
                    }
                } else {
                    bookObj.addProperty("matches_track_year", false);
                }
                
                booksArr.add(bookObj);
            }
            result.add("books", booksArr);
            result.add("matching_books", convertToJsonArray(matchingBooks));

            // 4. For matching books, get weather forecast for Nashville, TN (if within next 30 days)
            JsonArray weatherForecastsArr = new JsonArray();
            LocalDate today = LocalDate.now();
            LocalDate thirtyDaysFromNow = today.plusDays(30);
            
            for (JsonObject matchingBook : matchingBooks) {
                if (matchingBook.has("release_year")) {
                    int releaseYear = matchingBook.get("release_year").getAsInt();
                    // Assume the book was released on January 1st of the release year
                    LocalDate bookReleaseDate = LocalDate.of(releaseYear, 1, 1);
                    
                    if (!bookReleaseDate.isBefore(today) && !bookReleaseDate.isAfter(thirtyDaysFromNow)) {
                        // Get weather forecast for Nashville, TN (coordinates: 36.1627, -86.7816)
                        OpenWeather openWeather = new OpenWeather();
                        OpenWeather.WeatherForecastData forecast = openWeather.getForecast5Day(36.1627, -86.7816);
                        
                        JsonObject weatherObj = new JsonObject();
                        weatherObj.addProperty("book_title", matchingBook.get("title").getAsString());
                        weatherObj.addProperty("book_release_date", bookReleaseDate.toString());
                        weatherObj.addProperty("city", forecast.getCityName());
                        weatherObj.addProperty("country", forecast.getCountry());
                        
                        JsonArray forecastEntriesArr = new JsonArray();
                        for (OpenWeather.ForecastEntry entry : forecast.getForecasts()) {
                            JsonObject entryObj = new JsonObject();
                            entryObj.addProperty("date_time", entry.getDateTime().toString());
                            entryObj.addProperty("condition", entry.getCondition());
                            entryObj.addProperty("description", entry.getDescription());
                            entryObj.addProperty("temperature", entry.getTemperature());
                            entryObj.addProperty("humidity", entry.getHumidity());
                            entryObj.addProperty("wind_speed", entry.getWindSpeed());
                            forecastEntriesArr.add(entryObj);
                        }
                        weatherObj.add("forecast_entries", forecastEntriesArr);
                        weatherForecastsArr.add(weatherObj);
                    }
                }
            }
            result.add("weather_forecasts", weatherForecastsArr);
            
        } catch (Exception e) {
            result.addProperty("error", e.toString());
        }
        return result;
    }
    
    // Helper method to extract year from book title (simple heuristic)
    private static Integer extractYearFromTitle(String title) {
        if (title == null) return null;
        
        // Look for 4-digit years in the title (between 1900-2030)
        for (int year = 1900; year <= 2030; year++) {
            if (title.contains(String.valueOf(year))) {
                return year;
            }
        }
        
        // If no year found in title, return null
        return null;
    }
    
    // Helper method to convert List<JsonObject> to JsonArray
    private static JsonArray convertToJsonArray(List<JsonObject> list) {
        JsonArray array = new JsonArray();
        for (JsonObject obj : list) {
            array.add(obj);
        }
        return array;
    }
}
