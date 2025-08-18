import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0066 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Find top 4 most popular Spotify artists in the "rock" genre
            Spotify spotify = new Spotify();
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems("genre:rock", "artist", "US", 50, 0, null);
            JsonArray topArtistsArr = new JsonArray();
            List<Spotify.SpotifyArtist> topArtists = new ArrayList<>();
            
            if (spotifyResult.artists != null && !spotifyResult.artists.isEmpty()) {
                // Sort by popularity and take top 4
                spotifyResult.artists.sort((a, b) -> Integer.compare(b.popularity, a.popularity));
                int artistCount = Math.min(4, spotifyResult.artists.size());
                
                for (int i = 0; i < artistCount; i++) {
                    Spotify.SpotifyArtist artist = spotifyResult.artists.get(i);
                    topArtists.add(artist);
                    JsonObject artistObj = new JsonObject();
                    artistObj.addProperty("name", artist.name);
                    artistObj.addProperty("popularity", artist.popularity);
                    artistObj.addProperty("followers", artist.followers);
                    artistObj.addProperty("genres", String.join(", ", artist.genres != null ? artist.genres : new ArrayList<>()));
                    topArtistsArr.add(artistObj);
                }
            }
            result.add("top_4_rock_artists", topArtistsArr);

            // 2. Search for books about rock music in OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            List<OpenLibrary.BookInfo> books = openLibrary.search("rock music", "title,first_publish_year", "new", "en", 20, 1);
            JsonArray rockBooksArr = new JsonArray();
            
            for (OpenLibrary.BookInfo book : books) {
                JsonObject bookObj = new JsonObject();
                bookObj.addProperty("title", book.title);
                rockBooksArr.add(bookObj);
            }
            result.add("rock_music_books", rockBooksArr);

            // 3. For each artist, check for apartments in Austin, TX under $2200, within 1 mile of live music venues
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("Austin, TX", 0, 2200);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            
            // Find nearby live music venues in Austin
            maps_google_com maps = new maps_google_com(context);
            maps_google_com.NearestBusinessesResult venuesResult = maps.get_nearestBusinesses("Austin, TX", "live music venue", 15);
            List<maps_google_com.BusinessInfo> venues = venuesResult.businesses != null ? venuesResult.businesses : new ArrayList<>();
            
            JsonArray matchingApartmentsArr = new JsonArray();
            List<redfin_com.ApartmentInfo> closeApartments = new ArrayList<>();
            
            if (!topArtists.isEmpty()) {
                for (redfin_com.ApartmentInfo apt : apartments) {
                    String aptAddr = apt.address;
                    boolean isNearVenue = false;
                    
                    for (maps_google_com.BusinessInfo venue : venues) {
                        String venueAddr = venue.address;
                        maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, venueAddr);
                        double miles = parseMiles(dir.distance);
                        if (miles > 0 && miles <= 1.0) {
                            isNearVenue = true;
                            break;
                        }
                    }
                    
                    if (isNearVenue) {
                        closeApartments.add(apt);
                        JsonObject aptObj = new JsonObject();
                        aptObj.addProperty("address", apt.address);
                        aptObj.addProperty("price", apt.price != null ? apt.price.amount : null);
                        aptObj.addProperty("url", apt.url);
                        aptObj.addProperty("near_live_music_venue", true);
                        matchingApartmentsArr.add(aptObj);
                    }
                }
            }
            result.add("apartments_near_music_venues", matchingApartmentsArr);

            // 4. Get weather forecast for Austin, TX for August 20, 2025
            LocalDate targetDate = LocalDate.of(2025, 8, 20);
            LocalDate today = LocalDate.now();
            JsonArray weatherForecastsArr = new JsonArray();
            
            if (!closeApartments.isEmpty()) {
                if (!targetDate.isBefore(today) && targetDate.isBefore(today.plusDays(5))) {
                    // Austin, TX coordinates: 30.2672, -97.7431
                    OpenWeather openWeather = new OpenWeather();
                    OpenWeather.WeatherForecastData forecast = openWeather.getForecast5Day(30.2672, -97.7431);
                    
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
            result.add("weather_forecasts_austin", weatherForecastsArr);

            // Summary information
            JsonObject summaryObj = new JsonObject();
            summaryObj.addProperty("rock_artists_found", topArtistsArr.size());
            summaryObj.addProperty("rock_books_found", rockBooksArr.size());
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
