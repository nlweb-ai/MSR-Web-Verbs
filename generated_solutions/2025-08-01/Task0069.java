import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;

public class Task0069 {
    public static JsonObject automate(BrowserContext context) {
        JsonObject result = new JsonObject();
        try {
            // 1. Search for latest news about healthy eating
            News news = new News();
            News.NewsResponse newsResult = news.searchEverything("healthy eating", "en", 10);
            JsonArray healthyEatingNewsArr = new JsonArray();
            
            if (newsResult.articles != null) {
                for (News.NewsArticle article : newsResult.articles) {
                    JsonObject articleObj = new JsonObject();
                    articleObj.addProperty("title", article.title);
                    articleObj.addProperty("description", article.description);
                    articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : null);
                    articleObj.addProperty("source", article.source);
                    healthyEatingNewsArr.add(articleObj);
                }
            }
            result.add("healthy_eating_news", healthyEatingNewsArr);

            // 2. Find top 3 most popular Spotify tracks about healthy food
            Spotify spotify = new Spotify();
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems("healthy food", "track", "US", 50, 0, null);
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
            result.add("top_3_healthy_food_tracks", topTracksArr);

            // 3. For each track, search for books about nutrition in OpenLibrary
            OpenLibrary openLibrary = new OpenLibrary();
            JsonArray nutritionBooksArr = new JsonArray();
            List<OpenLibrary.BookInfo> firstBooks = new ArrayList<>();
            
            for (Spotify.SpotifyTrack track : topTracks) {
                List<OpenLibrary.BookInfo> books = openLibrary.search("nutrition", "title,first_publish_year", "new", "en", 10, 1);
                
                JsonObject trackBooksObj = new JsonObject();
                trackBooksObj.addProperty("track_name", track.name);
                trackBooksObj.addProperty("track_artist", track.artistNames != null && !track.artistNames.isEmpty() ? track.artistNames.get(0) : "Unknown");
                
                JsonArray booksArr = new JsonArray();
                if (books != null && !books.isEmpty()) {
                    // Take first book for apartment search
                    firstBooks.add(books.get(0));
                    
                    for (OpenLibrary.BookInfo book : books) {
                        JsonObject bookObj = new JsonObject();
                        bookObj.addProperty("title", book.title);
                        booksArr.add(bookObj);
                    }
                }
                trackBooksObj.add("nutrition_books", booksArr);
                nutritionBooksArr.add(trackBooksObj);
            }
            result.add("nutrition_books_by_track", nutritionBooksArr);

            // 4. For first book of each track, check for apartments in San Diego, CA under $2600, within 2 miles of grocery store
            redfin_com redfin = new redfin_com(context);
            redfin_com.ApartmentSearchResult apartmentsResult = redfin.searchApartments("San Diego, CA", 0, 2600);
            List<redfin_com.ApartmentInfo> apartments = apartmentsResult.apartments != null ? apartmentsResult.apartments : new ArrayList<>();
            
            // Find nearby grocery stores in San Diego
            maps_google_com maps = new maps_google_com(context);
            maps_google_com.NearestBusinessesResult storesResult = maps.get_nearestBusinesses("San Diego, CA", "grocery store", 15);
            List<maps_google_com.BusinessInfo> groceryStores = storesResult.businesses != null ? storesResult.businesses : new ArrayList<>();
            
            JsonArray matchingApartmentsArr = new JsonArray();
            
            if (!firstBooks.isEmpty()) {
                for (redfin_com.ApartmentInfo apt : apartments) {
                    String aptAddr = apt.address;
                    boolean isNearGroceryStore = false;
                    String nearestStore = null;
                    double shortestDistance = Double.MAX_VALUE;
                    
                    for (maps_google_com.BusinessInfo store : groceryStores) {
                        String storeAddr = store.address;
                        maps_google_com.DirectionResult dir = maps.get_direction(aptAddr, storeAddr);
                        double miles = parseMiles(dir.distance);
                        if (miles > 0 && miles <= 2.0 && miles < shortestDistance) {
                            isNearGroceryStore = true;
                            nearestStore = store.name;
                            shortestDistance = miles;
                        }
                    }
                    
                    if (isNearGroceryStore) {
                        JsonObject aptObj = new JsonObject();
                        aptObj.addProperty("address", apt.address);
                        aptObj.addProperty("price", apt.price != null ? apt.price.amount : null);
                        aptObj.addProperty("url", apt.url);
                        aptObj.addProperty("nearest_grocery_store", nearestStore);
                        aptObj.addProperty("distance_to_store_miles", Math.round(shortestDistance * 100.0) / 100.0);
                        matchingApartmentsArr.add(aptObj);
                    }
                }
            }
            result.add("apartments_near_grocery_stores", matchingApartmentsArr);

            // Summary information
            JsonObject summaryObj = new JsonObject();
            summaryObj.addProperty("healthy_eating_news_found", healthyEatingNewsArr.size());
            summaryObj.addProperty("healthy_food_tracks_found", topTracksArr.size());
            summaryObj.addProperty("nutrition_books_searches", nutritionBooksArr.size());
            summaryObj.addProperty("matching_apartments_found", matchingApartmentsArr.size());
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
