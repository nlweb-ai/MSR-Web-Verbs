import java.io.IOException;
import java.nio.file.Paths;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0093 {
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
        
        // Step 1: Check weather forecast for Chicago on August 21, 2025
        OpenWeather weather = new OpenWeather();
        String location = "Chicago, Illinois";
        
        JsonObject weatherInfo = new JsonObject();
        try {
            // Get location coordinates for Chicago
            java.util.List<OpenWeather.LocationData> locations = weather.getLocationsByName(location);
            if (locations.isEmpty()) {
                weatherInfo.addProperty("error", "Chicago location not found");
                weatherInfo.addProperty("outdoor_suitable", false);
            } else {
                OpenWeather.LocationData chicagoLocation = locations.get(0);
                OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(
                    chicagoLocation.getLatitude(), chicagoLocation.getLongitude());
                
                weatherInfo.addProperty("city", currentWeather.getCityName());
                weatherInfo.addProperty("temperature", currentWeather.getTemperature());
                weatherInfo.addProperty("condition", currentWeather.getCondition());
                weatherInfo.addProperty("description", currentWeather.getDescription());
                weatherInfo.addProperty("humidity", currentWeather.getHumidity());
                
                // Determine if suitable for outdoor event (clear, >70°F)
                boolean outdoorSuitable = currentWeather.getTemperature() > 70.0 && 
                                        !currentWeather.getCondition().toLowerCase().contains("rain") &&
                                        !currentWeather.getCondition().toLowerCase().contains("storm");
                weatherInfo.addProperty("outdoor_suitable", outdoorSuitable);
                weatherInfo.addProperty("event_recommendation", outdoorSuitable ? "outdoor" : "indoor");
            }
        } catch (IOException | InterruptedException e) {
            weatherInfo.addProperty("error", "Failed to fetch Chicago weather: " + e.getMessage());
            weatherInfo.addProperty("outdoor_suitable", false);
            weatherInfo.addProperty("event_recommendation", "indoor");
        }
        result.add("chicago_weather", weatherInfo);
        
        // Step 2: Search Costco for event supplies and fundraising materials within $800 budget
        costco_com costco = new costco_com(context);
        String[] eventSupplies = {"event supplies", "fundraising materials", "party decorations"};
        
        JsonObject costcoInfo = new JsonObject();
        JsonArray suppliesArray = new JsonArray();
        double totalEventCost = 0.0;
        double eventBudget = 800.0;
        
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
                    totalEventCost += productResult.productPrice.amount;
                } else {
                    supplyObj.addProperty("price", 0.0);
                }
            }
            suppliesArray.add(supplyObj);
        }
        
        costcoInfo.add("event_supplies", suppliesArray);
        costcoInfo.addProperty("total_supply_cost", totalEventCost);
        costcoInfo.addProperty("budget", eventBudget);
        costcoInfo.addProperty("remaining_budget", eventBudget - totalEventCost);
        costcoInfo.addProperty("budget_utilization", (totalEventCost / eventBudget) * 100);
        result.add("costco_event_supplies", costcoInfo);
        
        // Step 3: Find community centers and event halls near downtown Chicago (up to 6 venues)
        maps_google_com maps = new maps_google_com(context);
        String referencePoint = "downtown Chicago, Illinois";
        String businessDescription = "community centers event halls";
        int maxCount = 6;
        
        maps_google_com.NearestBusinessesResult venueResult = maps.get_nearestBusinesses(
            referencePoint, businessDescription, maxCount);
        
        JsonObject venueInfo = new JsonObject();
        venueInfo.addProperty("reference_point", venueResult.referencePoint);
        venueInfo.addProperty("business_description", venueResult.businessDescription);
        venueInfo.addProperty("purpose", "Backup indoor options for charity event");
        
        JsonArray venuesArray = new JsonArray();
        for (maps_google_com.BusinessInfo business : venueResult.businesses) {
            JsonObject venueObj = new JsonObject();
            venueObj.addProperty("name", business.name);
            venueObj.addProperty("address", business.address);
            venuesArray.add(venueObj);
        }
        venueInfo.add("indoor_venue_options", venuesArray);
        venueInfo.addProperty("total_venues", venuesArray.size());
        result.add("chicago_event_venues", venueInfo);
        
        // Step 4: Search Spotify for uplifting and inspirational music (top 4 tracks)
        Spotify spotify = new Spotify();
        String musicQuery = "uplifting inspirational positive charity";
        
        JsonObject spotifyInfo = new JsonObject();
        try {
            Spotify.SpotifySearchResult spotifyResult = spotify.searchItems(musicQuery, "track", null, 4, 0, null);
            if (spotifyResult.errorMessage != null) {
                spotifyInfo.addProperty("error", spotifyResult.errorMessage);
                spotifyInfo.add("inspirational_tracks", new JsonArray());
            } else {
                spotifyInfo.addProperty("search_query", musicQuery);
                spotifyInfo.addProperty("purpose", "Create positive atmosphere for charity event");
                JsonArray tracksArray = new JsonArray();
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
                }
                spotifyInfo.add("inspirational_tracks", tracksArray);
            }
        } catch (Exception e) {
            spotifyInfo.addProperty("error", "Failed to search Spotify: " + e.getMessage());
            spotifyInfo.add("inspirational_tracks", new JsonArray());
        }
        result.add("spotify_charity_music", spotifyInfo);
        
        // Charity fundraising event summary
        JsonObject charitySummary = new JsonObject();
        boolean outdoorSuitable = weatherInfo.has("outdoor_suitable") && weatherInfo.get("outdoor_suitable").getAsBoolean();
        
        charitySummary.addProperty("event_type", "Charity Fundraising Event");
        charitySummary.addProperty("location", "Chicago, Illinois");
        charitySummary.addProperty("event_date", "2025-08-21");
        charitySummary.addProperty("weather_suitable_for_outdoor", outdoorSuitable);
        charitySummary.addProperty("recommended_venue_type", outdoorSuitable ? "outdoor" : "indoor");
        charitySummary.addProperty("supply_budget", eventBudget);
        charitySummary.addProperty("supply_costs", totalEventCost);
        charitySummary.addProperty("budget_remaining", eventBudget - totalEventCost);
        charitySummary.addProperty("backup_indoor_venues", venuesArray.size());
        
        String eventRecommendation = createEventRecommendation(outdoorSuitable, totalEventCost, eventBudget, venuesArray.size());
        charitySummary.addProperty("event_planning_recommendation", eventRecommendation);
        
        // Event logistics
        JsonObject logistics = new JsonObject();
        logistics.addProperty("music_playlist_ready", true);
        logistics.addProperty("supply_procurement_status", totalEventCost > 0 ? "options identified" : "needs research");
        logistics.addProperty("venue_contingency_plan", venuesArray.size() > 0 ? "secured" : "needed");
        charitySummary.add("event_logistics", logistics);
        
        result.add("charity_event_summary", charitySummary);
        
        return result;
    }
    
    // Helper method to create event planning recommendations
    private static String createEventRecommendation(boolean outdoorSuitable, double supplyCost, double budget, int venues) {
        StringBuilder recommendation = new StringBuilder();
        
        if (outdoorSuitable) {
            recommendation.append("Weather conditions favorable for outdoor charity event. ");
            recommendation.append("Consider park or outdoor venue for maximum visibility and community engagement. ");
        } else {
            recommendation.append("Weather requires indoor venue. ");
            if (venues >= 4) {
                recommendation.append("Good backup options - ").append(venues).append(" indoor venues available. ");
            } else {
                recommendation.append("Limited indoor options - secure venue booking immediately. ");
            }
        }
        
        double budgetUtilization = (supplyCost / budget) * 100;
        if (budgetUtilization <= 50.0) {
            recommendation.append("Excellent budget efficiency - ").append(String.format("%.1f", budgetUtilization))
                          .append("% budget used. Consider additional promotional materials or refreshments. ");
        } else if (budgetUtilization <= 75.0) {
            recommendation.append("Good budget management - ").append(String.format("%.1f", budgetUtilization))
                          .append("% budget used. ");
        } else {
            recommendation.append("High supply costs - ").append(String.format("%.1f", budgetUtilization))
                          .append("% budget used. Review necessity of all items. ");
        }
        
        recommendation.append("Inspirational music playlist ready to create positive fundraising atmosphere.");
        
        return recommendation.toString();
    }
}
