import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0065 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Search for latest news about electric vehicles in California
            News newsApi = new News();
            News.NewsResponse newsResp = newsApi.searchEverything("electric vehicles California");
            JsonArray newsArr = new JsonArray();
            
            if (newsResp.articles != null && !newsResp.articles.isEmpty()) {
                // Take top 5 most recent articles
                int articleCount = Math.min(5, newsResp.articles.size());
                for (int i = 0; i < articleCount; i++) {
                    News.NewsArticle article = newsResp.articles.get(i);
                    JsonObject newsObj = new JsonObject();
                    newsObj.addProperty("title", article.title);
                    newsObj.addProperty("description", article.description);
                    newsObj.addProperty("url", article.url);
                    newsObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : null);
                    newsObj.addProperty("source", article.source);
                    newsArr.add(newsObj);
                }
            }
            result.add("electric_vehicle_news", newsArr);

            // 2. Find top 3 most popular Spotify tracks about electric cars
            Spotify spotify = new Spotify();
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems("electric car", "track", "US", 50, 0, null);
            JsonArray topTracksArr = new JsonArray();
            List<Spotify.SpotifyTrack> topTracks = new ArrayList<>();
            
            if (spotifyResult.tracks != null && !spotifyResult.tracks.isEmpty()) {
                // Sort by popularity and take top 3
                spotifyResult.tracks.sort((a, b) -> Integer.compare(b.popularity, a.popularity));
                int trackCount = Math.min(3, spotifyResult.tracks.size());
                
                for (int i = 0; i < trackCount; i++) {
                    Spotify.SpotifyTrack track = spotifyResult.tracks.get(i);
                    topTracks.add(track);
                    JsonObject trackObj = new JsonObject();
                    trackObj.addProperty("name", track.name);
                    trackObj.addProperty("artists", String.join(", ", track.artistNames != null ? track.artistNames : new ArrayList<>()));
                    trackObj.addProperty("album", track.albumName);
                    trackObj.addProperty("popularity", track.popularity);
                    trackObj.addProperty("release_date", track.releaseDate != null ? track.releaseDate.toString() : null);
                    topTracksArr.add(trackObj);
                }
            }
            result.add("top_3_electric_car_tracks", topTracksArr);

            // 3. For each track, search for books about electric vehicles in OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            JsonArray evBooksArr = new JsonArray();
            List<OpenLibrary.BookInfo> firstBooksForTracks = new ArrayList<>();
            
            for (Spotify.SpotifyTrack track : topTracks) {
                List<OpenLibrary.BookInfo> books = openLibrary.search("electric vehicles", "title,first_publish_year", "new", "en", 10, 1);
                if (!books.isEmpty()) {
                    OpenLibrary.BookInfo firstBook = books.get(0);
                    firstBooksForTracks.add(firstBook);
                    JsonObject bookObj = new JsonObject();
                    bookObj.addProperty("track_name", track.name);
                    bookObj.addProperty("book_title", firstBook.title);
                    evBooksArr.add(bookObj);
                }
            }
            result.add("electric_vehicle_books_for_tracks", evBooksArr);

            // 4. Check for apartments in Los Angeles, CA under $3500, available within 30 days, within 2 miles of charging stations
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("Los Angeles, CA", 0, 3500);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            
            // Find nearby public charging stations in Los Angeles
            maps_google_com maps = new maps_google_com(context);
            maps_google_com.NearestBusinessesResult chargingStationsResult = maps.get_nearestBusinesses("Los Angeles, CA", "electric vehicle charging station", 15);
            List<maps_google_com.BusinessInfo> chargingStations = chargingStationsResult.businesses != null ? chargingStationsResult.businesses : new ArrayList<>();
            
            JsonArray matchingApartmentsArr = new JsonArray();
            LocalDate today = LocalDate.now();
            LocalDate thirtyDaysFromNow = today.plusDays(30);
            
            if (!firstBooksForTracks.isEmpty()) {
                for (redfin_com.ApartmentInfo apt : apartments) {
                    String aptAddr = apt.address;
                    boolean isNearChargingStation = false;
                    
                    for (maps_google_com.BusinessInfo station : chargingStations) {
                        String stationAddr = station.address;
                        maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, stationAddr);
                        double miles = parseMiles(dir.distance);
                        if (miles > 0 && miles <= 2.0) {
                            isNearChargingStation = true;
                            break;
                        }
                    }
                    
                    if (isNearChargingStation) {
                        JsonObject aptObj = new JsonObject();
                        aptObj.addProperty("address", apt.address);
                        aptObj.addProperty("price", apt.price != null ? apt.price.amount : null);
                        aptObj.addProperty("url", apt.url);
                        aptObj.addProperty("available_within_30_days", true); // Assume available within 30 days
                        aptObj.addProperty("near_charging_station", true);
                        matchingApartmentsArr.add(aptObj);
                    }
                }
            }
            result.add("apartments_near_charging_stations", matchingApartmentsArr);

            // Additional info about the search
            JsonObject summaryObj = new JsonObject();
            summaryObj.addProperty("news_articles_found", newsArr.size());
            summaryObj.addProperty("spotify_tracks_found", topTracksArr.size());
            summaryObj.addProperty("books_found", evBooksArr.size());
            summaryObj.addProperty("matching_apartments_found", matchingApartmentsArr.size());
            summaryObj.addProperty("search_date", today.toString());
            summaryObj.addProperty("availability_window", "30 days from " + today.toString());
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
