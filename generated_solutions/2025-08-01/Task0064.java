import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0064 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Find top 2 most popular Spotify albums with jazz genre released in last 2 years
            Spotify spotify = new Spotify();
            LocalDate twoYearsAgo = LocalDate.now().minusYears(2);
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems("genre:jazz year:" + twoYearsAgo.getYear() + "-" + LocalDate.now().getYear(), "album", "US", 50, 0, null);
            JsonArray topAlbumsArr = new JsonArray();
            List<Spotify.SpotifyAlbum> topAlbums = new ArrayList<>();
            
            if (spotifyResult.albums != null && !spotifyResult.albums.isEmpty()) {
                // Sort albums by release date (most recent first) and take top 2
                spotifyResult.albums.sort((a, b) -> {
                    if (a.releaseDate == null && b.releaseDate == null) return 0;
                    if (a.releaseDate == null) return 1;
                    if (b.releaseDate == null) return -1;
                    return b.releaseDate.compareTo(a.releaseDate);
                });
                
                int albumCount = Math.min(2, spotifyResult.albums.size());
                for (int i = 0; i < albumCount; i++) {
                    Spotify.SpotifyAlbum album = spotifyResult.albums.get(i);
                    topAlbums.add(album);
                    JsonObject albumObj = new JsonObject();
                    albumObj.addProperty("name", album.name);
                    albumObj.addProperty("artists", String.join(", ", album.artistNames != null ? album.artistNames : new ArrayList<>()));
                    albumObj.addProperty("release_date", album.releaseDate != null ? album.releaseDate.toString() : null);
                    albumObj.addProperty("album_type", album.albumType);
                    topAlbumsArr.add(albumObj);
                }
            }
            result.add("top_2_jazz_albums", topAlbumsArr);

            // 2. For each album, search for books about jazz music in OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            JsonArray jazzBooksArr = new JsonArray();
            List<OpenLibrary.BookInfo> firstBooksForAlbums = new ArrayList<>();
            
            for (Spotify.SpotifyAlbum album : topAlbums) {
                List<OpenLibrary.BookInfo> books = openLibrary.search("jazz music", "title,first_publish_year", "new", "en", 10, 1);
                if (!books.isEmpty()) {
                    OpenLibrary.BookInfo firstBook = books.get(0);
                    firstBooksForAlbums.add(firstBook);
                    JsonObject bookObj = new JsonObject();
                    bookObj.addProperty("album_name", album.name);
                    bookObj.addProperty("book_title", firstBook.title);
                    jazzBooksArr.add(bookObj);
                }
            }
            result.add("jazz_books_for_albums", jazzBooksArr);

            // 3. Check for apartments in New Orleans, LA under $2000, within 3 miles of jazz clubs
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("New Orleans, LA", 0, 2000);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            
            // Find nearby jazz clubs in New Orleans
            maps_google_com maps = new maps_google_com(context);
            maps_google_com.NearestBusinessesResult jazzClubsResult = maps.get_nearestBusinesses("New Orleans, LA", "jazz club", 10);
            List<maps_google_com.BusinessInfo> jazzClubs = jazzClubsResult.businesses != null ? jazzClubsResult.businesses : new ArrayList<>();
            
            JsonArray matchingApartmentsArr = new JsonArray();
            List<redfin_com.ApartmentInfo> closeApartments = new ArrayList<>();
            
            if (!firstBooksForAlbums.isEmpty()) {
                for (redfin_com.ApartmentInfo apt : apartments) {
                    String aptAddr = apt.address;
                    boolean isNearJazzClub = false;
                    
                    for (maps_google_com.BusinessInfo jazzClub : jazzClubs) {
                        String clubAddr = jazzClub.address;
                        maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, clubAddr);
                        double miles = parseMiles(dir.distance);
                        if (miles > 0 && miles <= 3.0) {
                            isNearJazzClub = true;
                            break;
                        }
                    }
                    
                    if (isNearJazzClub) {
                        closeApartments.add(apt);
                        JsonObject aptObj = new JsonObject();
                        aptObj.addProperty("address", apt.address);
                        aptObj.addProperty("price", apt.price != null ? apt.price.amount : null);
                        aptObj.addProperty("url", apt.url);
                        matchingApartmentsArr.add(aptObj);
                    }
                }
            }
            result.add("apartments_near_jazz_clubs", matchingApartmentsArr);

            // 4. Get weather forecast for move-in date (August 15, 2025) in New Orleans
            LocalDate moveInDate = LocalDate.of(2025, 8, 15);
            LocalDate today = LocalDate.now();
            JsonArray weatherForecastsArr = new JsonArray();
            
            if (!closeApartments.isEmpty() && !moveInDate.isBefore(today) && moveInDate.isBefore(today.plusDays(5))) {
                // New Orleans, LA coordinates: 29.9511, -90.0715
                OpenWeather openWeather = new OpenWeather();
                OpenWeather.WeatherForecastData forecast = openWeather.getForecast5Day(29.9511, -90.0715);
                
                for (redfin_com.ApartmentInfo apt : closeApartments) {
                    JsonObject weatherObj = new JsonObject();
                    weatherObj.addProperty("apartment_address", apt.address);
                    weatherObj.addProperty("move_in_date", moveInDate.toString());
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
            } else if (!closeApartments.isEmpty()) {
                JsonObject weatherObj = new JsonObject();
                weatherObj.addProperty("move_in_date", moveInDate.toString());
                weatherObj.addProperty("message", "Move-in date is outside 5-day forecast range");
                weatherForecastsArr.add(weatherObj);
            }
            result.add("weather_forecasts_new_orleans", weatherForecastsArr);
            
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
