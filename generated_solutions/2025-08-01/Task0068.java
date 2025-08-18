import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0068 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Find top 2 most popular Spotify playlists about summer
            Spotify spotify = new Spotify();
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems("summer", "playlist", "US", 50, 0, null);
            JsonArray topPlaylistsArr = new JsonArray();
            List<Spotify.SpotifyPlaylist> topPlaylists = new ArrayList<>();
            
            if (spotifyResult.playlists != null && !spotifyResult.playlists.isEmpty()) {
                // Take first 2 playlists (assuming they are ordered by popularity)
                int playlistCount = Math.min(2, spotifyResult.playlists.size());
                
                for (int i = 0; i < playlistCount; i++) {
                    Spotify.SpotifyPlaylist playlist = spotifyResult.playlists.get(i);
                    topPlaylists.add(playlist);
                    JsonObject playlistObj = new JsonObject();
                    playlistObj.addProperty("name", playlist.name);
                    playlistObj.addProperty("description", playlist.description);
                    playlistObj.addProperty("owner", playlist.ownerName);
                    playlistObj.addProperty("total_tracks", playlist.totalTracks);
                    playlistObj.addProperty("is_public", playlist.isPublic);
                    topPlaylistsArr.add(playlistObj);
                }
            }
            result.add("top_2_summer_playlists", topPlaylistsArr);

            // 2. Search for books about summer activities in OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            List<OpenLibrary.BookInfo> books = openLibrary.search("summer activities", "title,first_publish_year", "new", "en", 20, 1);
            JsonArray summerBooksArr = new JsonArray();
            
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                summerBooksArr.add(bookObj);
            }
            result.add("summer_activities_books", summerBooksArr);

            // 3. For each playlist, check for apartments in Miami, FL under $2700, within 1 mile of a beach
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("Miami, FL", 0, 2700);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            
            // Find nearby beaches in Miami
            maps_google_com maps = new maps_google_com(context);
            maps_google_com.NearestBusinessesResult beachesResult = maps.get_nearestBusinesses("Miami, FL", "beach", 10);
            List<maps_google_com.BusinessInfo> beaches = beachesResult.businesses != null ? beachesResult.businesses : new ArrayList<>();
            
            JsonArray matchingApartmentsArr = new JsonArray();
            List<redfin_com.ApartmentInfo> closeApartments = new ArrayList<>();
            
            if (!topPlaylists.isEmpty()) {
                for (redfin_com.ApartmentInfo apt : apartments) {
                    String aptAddr = apt.address;
                    boolean isNearBeach = false;
                    
                    for (maps_google_com.BusinessInfo beach : beaches) {
                        String beachAddr = beach.address;
                        maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, beachAddr);
                        double miles = parseMiles(dir.distance);
                        if (miles > 0 && miles <= 1.0) {
                            isNearBeach = true;
                            break;
                        }
                    }
                    
                    if (isNearBeach) {
                        closeApartments.add(apt);
                        JsonObject aptObj = new JsonObject();
                        aptObj.addProperty("address", apt.address);
                        aptObj.addProperty("price", apt.price != null ? apt.price.amount : null);
                        aptObj.addProperty("url", apt.url);
                        aptObj.addProperty("near_beach", true);
                        matchingApartmentsArr.add(aptObj);
                    }
                }
            }
            result.add("apartments_near_beach", matchingApartmentsArr);

            // 4. Get weather forecast for Miami, FL for August 18, 2025
            LocalDate targetDate = LocalDate.of(2025, 8, 18);
            LocalDate today = LocalDate.now();
            JsonArray weatherForecastsArr = new JsonArray();
            
            if (!closeApartments.isEmpty()) {
                if (!targetDate.isBefore(today) && targetDate.isBefore(today.plusDays(5))) {
                    // Miami, FL coordinates: 25.7617, -80.1918
                    OpenWeather openWeather = new OpenWeather();
                    OpenWeather.WeatherForecastData forecast = openWeather.getForecast5Day(25.7617, -80.1918);
                    
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
            result.add("weather_forecasts_miami", weatherForecastsArr);

            // Summary information
            JsonObject summaryObj = new JsonObject();
            summaryObj.addProperty("summer_playlists_found", topPlaylistsArr.size());
            summaryObj.addProperty("summer_books_found", summerBooksArr.size());
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
