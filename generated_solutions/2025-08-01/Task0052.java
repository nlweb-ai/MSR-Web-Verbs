import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0052 {
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
            // Step 1: Search for round-trip flights from Seattle (SEA) to San Diego (SAN)
            // Departing August 15, returning August 17, 2025
            alaskaair_com alaskaAir = new alaskaair_com(context);
            LocalDate departDate = LocalDate.of(2025, 8, 15);
            LocalDate returnDate = LocalDate.of(2025, 8, 17);
            
            alaskaair_com.SearchFlightsResult flightSearch = alaskaAir.searchFlights("SEA", "SAN", departDate, returnDate);
            
            JsonObject flightInfo = new JsonObject();
            if (flightSearch.flightInfo != null) {
                flightInfo.addProperty("origin", "SEA");
                flightInfo.addProperty("destination", "SAN");
                flightInfo.addProperty("departure_date", departDate.toString());
                flightInfo.addProperty("return_date", returnDate.toString());
                
                if (flightSearch.flightInfo.price != null) {
                    flightInfo.addProperty("price", flightSearch.flightInfo.price.amount);
                    flightInfo.addProperty("currency", flightSearch.flightInfo.price.currency);
                }
                
                JsonArray flightsArray = new JsonArray();
                if (flightSearch.flightInfo.flights != null) {
                    for (String flight : flightSearch.flightInfo.flights) {
                        flightsArray.add(flight);
                    }
                }
                flightInfo.add("flights", flightsArray);
                flightInfo.addProperty("search_successful", true);
            } else {
                flightInfo.addProperty("search_successful", false);
                flightInfo.addProperty("message", flightSearch.message != null ? flightSearch.message : "No flights found");
            }
            result.add("flight_search", flightInfo);
            
            // Step 2: Get weather forecast for San Diego for August 15-17, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> sanDiegoLocations = weather.getLocationsByName("San Diego, CA");
            
            JsonObject weatherForecast = new JsonObject();
            if (!sanDiegoLocations.isEmpty()) {
                OpenWeather.LocationData sanDiego = sanDiegoLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(sanDiego.getLatitude(), sanDiego.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("travel_dates", "August 15-17, 2025");
                
                JsonArray forecastArray = new JsonArray();
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
                    forecastArray.add(forecastEntry);
                }
                weatherForecast.add("forecasts", forecastArray);
            } else {
                weatherForecast.addProperty("error", "Could not find location data for San Diego, CA");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Find 5 best-rated seafood restaurants near hotel using Google Maps
            maps_google_com maps = new maps_google_com(context);
            String hotelLocation = "San Diego, CA"; // Using city center as hotel reference
            maps_google_com.NearestBusinessesResult seafoodRestaurants = maps.get_nearestBusinesses(hotelLocation, "seafood restaurant", 5);
            
            JsonObject restaurantsInfo = new JsonObject();
            restaurantsInfo.addProperty("reference_location", hotelLocation);
            restaurantsInfo.addProperty("business_type", "seafood restaurant");
            restaurantsInfo.addProperty("requested_count", 5);
            
            JsonArray restaurantsArray = new JsonArray();
            for (maps_google_com.BusinessInfo restaurant : seafoodRestaurants.businesses) {
                JsonObject restaurantObj = new JsonObject();
                restaurantObj.addProperty("name", restaurant.name);
                restaurantObj.addProperty("address", restaurant.address);
                
                // Get distance and directions from hotel to restaurant
                maps_google_com.DirectionResult direction = maps.get_direction(hotelLocation, restaurant.address);
                restaurantObj.addProperty("distance", direction.distance);
                restaurantObj.addProperty("travel_time", direction.travelTime);
                restaurantObj.addProperty("route", direction.route);
                
                restaurantsArray.add(restaurantObj);
            }
            restaurantsInfo.add("restaurants", restaurantsArray);
            result.add("seafood_restaurants", restaurantsInfo);
            
            // Step 4: Create a beach/summer themed playlist using Spotify
            Spotify spotify = new Spotify();
            
            // Search for beach themed songs
            Spotify.SpotifySearchResult beachSongs = spotify.searchItems("beach", "track", "US", 20, 0, null);
            
            // Search for summer themed songs
            Spotify.SpotifySearchResult summerSongs = spotify.searchItems("summer", "track", "US", 20, 0, null);
            
            JsonObject playlistInfo = new JsonObject();
            playlistInfo.addProperty("theme", "Beach & Summer Travel");
            playlistInfo.addProperty("target_songs", 10);
            
            JsonArray playlistArray = new JsonArray();
            int songCount = 0;
            
            // Add beach songs first
            if (beachSongs.tracks != null) {
                for (Spotify.SpotifyTrack track : beachSongs.tracks) {
                    if (songCount >= 10) break;
                    
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
                    songObj.addProperty("theme", "beach");
                    
                    playlistArray.add(songObj);
                    songCount++;
                }
            }
            
            // Add summer songs to reach 10 total
            if (summerSongs.tracks != null && songCount < 10) {
                for (Spotify.SpotifyTrack track : summerSongs.tracks) {
                    if (songCount >= 10) break;
                    
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
                    songObj.addProperty("theme", "summer");
                    
                    playlistArray.add(songObj);
                    songCount++;
                }
            }
            
            playlistInfo.addProperty("actual_songs", songCount);
            playlistInfo.add("songs", playlistArray);
            
            // Add error information if searches failed
            if (beachSongs.errorMessage != null || summerSongs.errorMessage != null) {
                JsonObject errors = new JsonObject();
                if (beachSongs.errorMessage != null) {
                    errors.addProperty("beach_search_error", beachSongs.errorMessage);
                }
                if (summerSongs.errorMessage != null) {
                    errors.addProperty("summer_search_error", summerSongs.errorMessage);
                }
                playlistInfo.add("search_errors", errors);
            }
            
            result.add("travel_playlist", playlistInfo);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("trip_destination", "San Diego, California");
            summary.addProperty("travel_dates", "August 15-17, 2025");
            summary.addProperty("departure_city", "Seattle");
            summary.addProperty("flights_found", flightSearch.flightInfo != null);
            summary.addProperty("weather_forecast_available", !sanDiegoLocations.isEmpty());
            summary.addProperty("seafood_restaurants_found", seafoodRestaurants.businesses.size());
            summary.addProperty("playlist_songs_found", songCount);
            result.add("trip_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
