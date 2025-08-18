import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0070 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Find top 3 most popular Spotify tracks about rain
            Spotify spotify = new Spotify();
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems("rain", "track", "US", 50, 0, null);
            JsonArray topTracksArr = new JsonArray();
            List<Spotify.SpotifyTrack> topTracks = new ArrayList<>();
            
            if (spotifyResult.tracks != null && !spotifyResult.tracks.isEmpty()) {
                // Take first 3 tracks (assuming they are ordered by popularity)
                int trackCount = Math.min(3, spotifyResult.tracks.size());
                
                for (int i = 0; i < trackCount; i++) {
                    Spotify.SpotifyTrack track = spotifyResult.tracks.get(i);
                    topTracks.add(track);
                    JsonObject trackObj = new JsonObject();
                    trackObj.addProperty("name", track.name);
                    trackObj.addProperty("artist", track.artistNames != null && !track.artistNames.isEmpty() ? track.artistNames.get(0) : "Unknown");
                    trackObj.addProperty("album", track.albumName);
                    trackObj.addProperty("popularity", track.popularity);
                    trackObj.addProperty("duration_ms", track.duration != null ? track.duration.toMillis() : null);
                    topTracksArr.add(trackObj);
                }
            }
            result.add("top_3_rain_tracks", topTracksArr);

            // 2. Search for books about weather in OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            List<OpenLibrary.BookInfo> books = openLibrary.search("weather", "title,first_publish_year", "new", "en", 10, 1);
            JsonArray weatherBooksArr = new JsonArray();
            
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                weatherBooksArr.add(bookObj);
            }
            result.add("weather_books", weatherBooksArr);

            // 3. For each book, check for apartments in Portland, OR under $2100, within 1 mile of a public park
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("Portland, OR", 0, 2100);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            
            // Find nearby public parks in Portland
            maps_google_com maps = new maps_google_com(context);
            maps_google_com.NearestBusinessesResult parksResult = maps.get_nearestBusinesses("Portland, OR", "public park", 15);
            List<maps_google_com.BusinessInfo> parks = parksResult.businesses != null ? parksResult.businesses : new ArrayList<>();
            
            JsonArray matchingApartmentsArr = new JsonArray();
            List<redfin_com.ApartmentInfo> closeApartments = new ArrayList<>();
            
            if (!books.isEmpty()) {
                for (redfin_com.ApartmentInfo apt : apartments) {
                    String aptAddr = apt.address;
                    boolean isNearPark = false;
                    String nearestPark = null;
                    double shortestDistance = Double.MAX_VALUE;
                    
                    for (maps_google_com.BusinessInfo park : parks) {
                        String parkAddr = park.address;
                        maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, parkAddr);
                        double miles = parseMiles(dir.distance);
                        if (miles > 0 && miles <= 1.0 && miles < shortestDistance) {
                            isNearPark = true;
                            nearestPark = park.name;
                            shortestDistance = miles;
                        }
                    }
                    
                    if (isNearPark) {
                        closeApartments.add(apt);
                        JsonObject aptObj = new JsonObject();
                        aptObj.addProperty("address", apt.address);
                        aptObj.addProperty("price", apt.price != null ? apt.price.amount : null);
                        aptObj.addProperty("url", apt.url);
                        aptObj.addProperty("nearest_park", nearestPark);
                        aptObj.addProperty("distance_to_park_miles", Math.round(shortestDistance * 100.0) / 100.0);
                        matchingApartmentsArr.add(aptObj);
                    }
                }
            }
            result.add("apartments_near_parks", matchingApartmentsArr);

            // 4. Get weather forecast for Portland, OR for August 22, 2025
            LocalDate targetDate = LocalDate.of(2025, 8, 22);
            LocalDate today = LocalDate.now();
            JsonArray weatherForecastsArr = new JsonArray();
            
            if (!closeApartments.isEmpty()) {
                if (!targetDate.isBefore(today) && targetDate.isBefore(today.plusDays(5))) {
                    // Portland, OR coordinates: 45.5152, -122.6784
                    OpenWeather openWeather = new OpenWeather();
                    OpenWeather.WeatherForecastData forecast = openWeather.getForecast5Day(45.5152, -122.6784);
                    
                    for (redfin_com.ApartmentInfo apt : closeApartments) {
                        JsonObject weatherObj = new JsonObject();
                        weatherObj.addProperty("apartment_address", apt.address);
                        weatherObj.addProperty("target_date", targetDate.toString());
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
                        break; // Only get forecast for first matching apartment
                    }
                } else {
                    JsonObject weatherObj = new JsonObject();
                    weatherObj.addProperty("target_date", targetDate.toString());
                    weatherObj.addProperty("message", "Target date is outside 5-day forecast range");
                    weatherForecastsArr.add(weatherObj);
                }
            }
            result.add("weather_forecasts_portland", weatherForecastsArr);

            // Summary information
            JsonObject summaryObj = new JsonObject();
            summaryObj.addProperty("rain_tracks_found", topTracksArr.size());
            summaryObj.addProperty("weather_books_found", weatherBooksArr.size());
            summaryObj.addProperty("matching_apartments_found", matchingApartmentsArr.size());
            summaryObj.addProperty("weather_forecasts_generated", weatherForecastsArr.size());
            result.add("search_summary", summaryObj);
            
        } catch (Exception e) {
            result.addProperty("error", e.toString());
        }
        return result;
    }
    
    // Helper method to parse miles from distance string
    private static double parseMiles(String distanceStr) {
        if (distanceStr == null) return -1;
        distanceStr = distanceStr.toLowerCase().trim();
        try {
            if (distanceStr.contains("mile")) {
                String num = distanceStr.split("mile")[0].replaceAll("[^0-9.]+", "");
                return Double.parseDouble(num);
            } else if (distanceStr.contains("ft")) {
                String num = distanceStr.split("ft")[0].replaceAll("[^0-9.]+", "");
                double feet = Double.parseDouble(num);
                return feet / 5280.0;
            }
        } catch (Exception e) {
            return -1;
        }
        return -1;
    }
}
