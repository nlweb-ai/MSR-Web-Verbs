import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0089 {
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
        
        // Step 1: Search Spotify for top 6 country music tracks
        Spotify spotify = new Spotify();
        String countryQuery = "country music";
        
        JsonObject spotifyInfo = new JsonObject();
        try {
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems(countryQuery, "track", null, 6, 0, null);
            if (spotifyResult.errorMessage != null) {
                spotifyInfo.addProperty("error", spotifyResult.errorMessage);
                spotifyInfo.add("country_tracks", new JsonArray());
                spotifyInfo.addProperty("average_popularity", 0.0);
            } else {
                spotifyInfo.addProperty("search_query", countryQuery);
                JsonArray tracksArray = new JsonArray();
                int totalPopularity = 0;
                int trackCount = 0;
                
                for (Spotify.SpotifyTrack track : spotifyResult.tracks) {
                    JsonObject trackObj = new JsonObject();
                    trackObj.addProperty("name", track.name);
                    trackObj.addProperty("artists", String.join(", ", track.artistNames));
                    trackObj.addProperty("album", track.albumName);
                    trackObj.addProperty("popularity", track.popularity);
                    trackObj.addProperty("uri", track.uri);
                    if (track.duration != null) {
                        long minutes = track.duration.toMinutes();
                        long seconds = track.duration.getSeconds() % 60;
                        trackObj.addProperty("duration", String.format("%d:%02d", minutes, seconds));
                    }
                    tracksArray.add(trackObj);
                    totalPopularity += track.popularity;
                    trackCount++;
                }
                
                double averagePopularity = trackCount > 0 ? (double) totalPopularity / trackCount : 0.0;
                spotifyInfo.add("country_tracks", tracksArray);
                spotifyInfo.addProperty("average_popularity", averagePopularity);
                spotifyInfo.addProperty("trending_assessment", getTrendingAssessment(averagePopularity));
            }
        } catch (Exception e) {
            spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
            spotifyInfo.add("country_tracks", new JsonArray());
            spotifyInfo.addProperty("average_popularity", 0.0);
        }
        result.add("spotify_country_music", spotifyInfo);
        
        // Step 2: Search Costco for event planning supplies and audio equipment
        costco_com costco = new costco_com(context);
        String[] eventSupplies = {"event planning supplies", "audio equipment", "stage equipment"};
        
        JsonObject costcoInfo = new JsonObject();
        JsonArray suppliesArray = new JsonArray();
        double totalEquipmentCost = 0.0;
        
        for (String supply : eventSupplies) {
            costco_com.ProductInfo productResult = costco.searchProduct(supply);
            JsonObject supplyObj = new JsonObject();
            supplyObj.addProperty("search_term", supply);
            
            if (productResult.error != null) {
                supplyObj.addProperty("error", productResult.error);
                supplyObj.addProperty("price", 0.0);
            } else {
                supplyObj.addProperty("product_name", productResult.productName);
                if (productResult.productPrice != null) {
                    supplyObj.addProperty("price", productResult.productPrice.amount);
                    supplyObj.addProperty("currency", productResult.productPrice.currency);
                    totalEquipmentCost += productResult.productPrice.amount;
                } else {
                    supplyObj.addProperty("price", 0.0);
                }
            }
            suppliesArray.add(supplyObj);
        }
        
        costcoInfo.add("festival_infrastructure", suppliesArray);
        costcoInfo.addProperty("total_equipment_cost", totalEquipmentCost);
        result.add("costco_festival_supplies", costcoInfo);
        
        // Step 3: Find event venues and concert halls near downtown Nashville (up to 10)
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "downtown Nashville, Tennessee";
        String businessDescription = "event venues concert halls";
        int maxCount = 10;
        
        maps_google_com.NearestBusinessesResult venueResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxCount);
        
        JsonObject venueInfo = new JsonObject();
        venueInfo.addProperty("reference_point", venueResult.referencePoint);
        venueInfo.addProperty("business_description", venueResult.businessDescription);
        
        JsonArray venuesArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : venueResult.businesses) {
            JsonObject venueObj = new JsonObject();
            venueObj.addProperty("name", business.name);
            venueObj.addProperty("address", business.address);
            venuesArray.add(venueObj);
        }
        venueInfo.add("festival_venues", venuesArray);
        venueInfo.addProperty("total_venues_found", venuesArray.size());
        result.add("nashville_festival_venues", venueInfo);
        
        // Step 4: Get recent news about music festivals and live events
        News news = new News();
        String newsQuery = "music festivals live events best practices safety";
        
        JsonObject newsInfo = new JsonObject();
        try {
            News.NewsResponse newsResult = news.searchEverything(newsQuery);
            newsInfo.addProperty("status", newsResult.status);
            newsInfo.addProperty("total_results", newsResult.totalResults);
            newsInfo.addProperty("search_query", newsQuery);
            
            JsonArray articlesArray = new JsonArray();
            for (News.NewsArticle article : newsResult.articles) {
                JsonObject articleObj = new JsonObject();
                articleObj.addProperty("title", article.title);
                articleObj.addProperty("description", article.description);
                articleObj.addProperty("url", article.url);
                articleObj.addProperty("published_at", article.publishedAt != null ? article.publishedAt.toString() : null);
                articleObj.addProperty("source", article.source);
                articlesArray.add(articleObj);
            }
            newsInfo.add("articles", articlesArray);
        } catch (IOException | InterruptedException e) {
            newsInfo.addProperty("error", "Failed to fetch festival news: " + e.getMessage());
            newsInfo.add("articles", new JsonArray());
        }
        result.add("music_festival_news", newsInfo);
        
        // Festival planning summary
        JsonObject festivalSummary = new JsonObject();
        double avgPopularity = spotifyInfo.has("average_popularity") ? spotifyInfo.get("average_popularity").getAsDouble() : 0.0;
        int totalVenues = venuesArray.size();
        
        festivalSummary.addProperty("event_type", "Music Festival");
        festivalSummary.addProperty("location", "Nashville, Tennessee");
        festivalSummary.addProperty("planning_date", "2025-08-28");
        festivalSummary.addProperty("country_music_trend_score", avgPopularity);
        festivalSummary.addProperty("equipment_budget_estimate", totalEquipmentCost);
        festivalSummary.addProperty("potential_venues", totalVenues);
        
        String festivalRecommendation = getFestivalRecommendation(avgPopularity, totalVenues, totalEquipmentCost);
        festivalSummary.addProperty("planning_recommendation", festivalRecommendation);
        
        result.add("festival_planning_summary", festivalSummary);
        
        return result;
    }
    
    // Helper method to assess music trending based on popularity scores
    private static String getTrendingAssessment(double averagePopularity) {
        if (averagePopularity >= 80.0) {
            return "High trending - excellent festival lineup potential";
        } else if (averagePopularity >= 60.0) {
            return "Moderate trending - good audience appeal expected";
        } else if (averagePopularity >= 40.0) {
            return "Low-moderate trending - consider mixing with other genres";
        } else if (averagePopularity > 0.0) {
            return "Low trending - focus on emerging artists or niche audiences";
        } else {
            return "No data available - research alternative music sources";
        }
    }
    
    // Helper method to provide festival planning recommendations
    private static String getFestivalRecommendation(double avgPopularity, int venueCount, double equipmentCost) {
        StringBuilder recommendation = new StringBuilder();
        
        if (avgPopularity >= 60.0) {
            recommendation.append("Strong country music appeal - proceed with country-focused lineup. ");
        } else {
            recommendation.append("Consider diversifying genres beyond country music. ");
        }
        
        if (venueCount >= 8) {
            recommendation.append("Excellent venue options available - ").append(venueCount).append(" potential locations. ");
        } else if (venueCount >= 5) {
            recommendation.append("Good venue selection - ").append(venueCount).append(" options to evaluate. ");
        } else {
            recommendation.append("Limited venues found - expand search radius or consider outdoor locations. ");
        }
        
        if (equipmentCost > 5000.0) {
            recommendation.append("High equipment costs - consider rental alternatives or phased equipment acquisition.");
        } else if (equipmentCost > 2000.0) {
            recommendation.append("Moderate equipment investment - budget accordingly for additional festival needs.");
        } else {
            recommendation.append("Equipment costs appear manageable - allocate remaining budget to talent and marketing.");
        }
        
        return recommendation.toString();
    }
}
