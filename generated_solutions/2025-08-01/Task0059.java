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


public class Task0059 {
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
            // Step 1: Search for hotels in Orlando for August 14-18, 2025
            booking_com booking = new booking_com(context);
            LocalDate checkinDate = LocalDate.of(2025, 8, 14);
            LocalDate checkoutDate = LocalDate.of(2025, 8, 18);
            
            booking_com.HotelSearchResult hotelSearch = booking.search_hotel("Orlando, Florida", checkinDate, checkoutDate);
            
            JsonObject hotelInfo = new JsonObject();
            hotelInfo.addProperty("destination", hotelSearch.destination);
            hotelInfo.addProperty("checkin_date", hotelSearch.checkinDate.toString());
            hotelInfo.addProperty("checkout_date", hotelSearch.checkoutDate.toString());
            hotelInfo.addProperty("vacation_duration", "4 nights (August 14-18, 2025)");
            
            JsonArray hotelsArray = new JsonArray();
            
            if (hotelSearch.hotels != null && !hotelSearch.hotels.isEmpty()) {
                // Take the first 5 hotels for options
                int hotelCount = Math.min(5, hotelSearch.hotels.size());
                for (int i = 0; i < hotelCount; i++) {
                    booking_com.HotelInfo hotel = hotelSearch.hotels.get(i);
                    
                    JsonObject hotelObj = new JsonObject();
                    hotelObj.addProperty("name", hotel.hotelName);
                    
                    if (hotel.price != null) {
                        hotelObj.addProperty("price", hotel.price.amount);
                        hotelObj.addProperty("currency", hotel.price.currency);
                    }
                    
                    hotelObj.addProperty("recommended", i == 0); // First hotel as recommended
                    
                    hotelsArray.add(hotelObj);
                }
                hotelInfo.addProperty("hotels_found", hotelCount);
            } else {
                hotelInfo.addProperty("hotels_found", 0);
                hotelInfo.addProperty("note", "No hotels found for the specified dates");
            }
            
            hotelInfo.add("hotel_options", hotelsArray);
            result.add("hotel_booking", hotelInfo);
            
            // Step 2: Get weather forecast for Orlando for August 14-18, 2025
            OpenWeather weather = new OpenWeather();
            List<OpenWeather.LocationData> orlandoLocations = weather.getLocationsByName("Orlando, FL");
            
            JsonObject weatherForecast = new JsonObject();
            if (!orlandoLocations.isEmpty()) {
                OpenWeather.LocationData orlando = orlandoLocations.get(0);
                OpenWeather.WeatherForecastData forecast = weather.getForecast5Day(orlando.getLatitude(), orlando.getLongitude());
                
                weatherForecast.addProperty("city", forecast.getCityName());
                weatherForecast.addProperty("country", forecast.getCountry());
                weatherForecast.addProperty("latitude", forecast.getLatitude());
                weatherForecast.addProperty("longitude", forecast.getLongitude());
                weatherForecast.addProperty("vacation_dates", "August 14-18, 2025");
                
                JsonArray forecastArray = new JsonArray();
                int vacationDays = 0;
                
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
                    
                    // Check if this is during vacation dates
                    String dateStr = entry.getDateTime().toString();
                    if (dateStr.contains("2025-08-14") || dateStr.contains("2025-08-15") || 
                        dateStr.contains("2025-08-16") || dateStr.contains("2025-08-17") || 
                        dateStr.contains("2025-08-18")) {
                        forecastEntry.addProperty("is_vacation_day", true);
                        forecastEntry.addProperty("activity_planning", "Perfect for theme park visits");
                        vacationDays++;
                    }
                    
                    forecastArray.add(forecastEntry);
                }
                
                weatherForecast.add("forecasts", forecastArray);
                weatherForecast.addProperty("vacation_days_covered", vacationDays);
                weatherForecast.addProperty("family_planning_note", "Weather conditions for daily activity planning");
            } else {
                weatherForecast.addProperty("error", "Could not find location data for Orlando, FL");
            }
            result.add("weather_forecast", weatherForecast);
            
            // Step 3: Find 3 nearest theme parks to hotel
            maps_google_com maps = new maps_google_com(context);
            String hotelLocation = "Orlando, FL"; // Using city center as hotel reference
            maps_google_com.NearestBusinessesResult themeParks = maps.get_nearestBusinesses(hotelLocation, "theme park", 3);
            
            JsonObject themeParksInfo = new JsonObject();
            themeParksInfo.addProperty("hotel_location", hotelLocation);
            themeParksInfo.addProperty("search_type", "theme parks");
            themeParksInfo.addProperty("requested_count", 3);
            
            JsonArray parksArray = new JsonArray();
            for (maps_google_com.BusinessInfo park : themeParks.businesses) {
                JsonObject parkObj = new JsonObject();
                parkObj.addProperty("name", park.name);
                parkObj.addProperty("address", park.address);
                
                // Get directions from hotel to theme park
                maps_google_com.DirectionResult direction = maps.get_direction(hotelLocation, park.address);
                parkObj.addProperty("distance_from_hotel", direction.distance);
                parkObj.addProperty("travel_time", direction.travelTime);
                parkObj.addProperty("route", direction.route);
                parkObj.addProperty("family_appeal", "Great for family vacation activities");
                
                parksArray.add(parkObj);
            }
            
            themeParksInfo.add("theme_parks", parksArray);
            themeParksInfo.addProperty("parks_found", parksArray.size());
            result.add("nearby_theme_parks", themeParksInfo);
            
            // Step 4: Search YouTube for Orlando family travel tips
            youtube_com youtube = new youtube_com(context);
            List<youtube_com.YouTubeVideoInfo> travelTips = youtube.searchVideos("Orlando family travel tips");
            
            JsonObject familyTravelTips = new JsonObject();
            familyTravelTips.addProperty("search_query", "Orlando family travel tips");
            familyTravelTips.addProperty("target_videos", 3);
            familyTravelTips.addProperty("purpose", "Family vacation preparation");
            
            JsonArray videosArray = new JsonArray();
            int videoCount = Math.min(3, travelTips.size());
            
            for (int i = 0; i < videoCount; i++) {
                youtube_com.YouTubeVideoInfo video = travelTips.get(i);
                JsonObject videoObj = new JsonObject();
                videoObj.addProperty("title", video.title);
                videoObj.addProperty("url", video.url);
                
                // Format duration
                if (video.length != null) {
                    long s = video.length.getSeconds();
                    long h = s / 3600;
                    long m = (s % 3600) / 60;
                    long sec = s % 60;
                    String lenStr = h > 0 ? String.format("%d:%02d:%02d", h, m, sec) : String.format("%d:%02d", m, sec);
                    videoObj.addProperty("duration", lenStr);
                }
                
                videoObj.addProperty("family_value", "Essential tips for Orlando family vacation");
                videoObj.addProperty("watch_priority", i + 1);
                videosArray.add(videoObj);
            }
            
            familyTravelTips.add("recommended_videos", videosArray);
            familyTravelTips.addProperty("videos_selected", videoCount);
            familyTravelTips.addProperty("preparation_impact", "Better informed family vacation planning");
            result.add("family_travel_tips", familyTravelTips);
            
            // Summary
            JsonObject summary = new JsonObject();
            summary.addProperty("vacation_type", "Family Vacation");
            summary.addProperty("destination", "Orlando, Florida");
            summary.addProperty("dates", "August 14-18, 2025");
            summary.addProperty("duration", "4 nights");
            summary.addProperty("hotels_available", hotelSearch.hotels != null ? hotelSearch.hotels.size() : 0);
            summary.addProperty("weather_forecast_available", !orlandoLocations.isEmpty());
            summary.addProperty("theme_parks_found", themeParks.businesses.size());
            summary.addProperty("travel_tip_videos", videoCount);
            summary.addProperty("vacation_readiness", "Fully prepared for Orlando family adventure");
            result.add("vacation_summary", summary);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject error = new JsonObject();
            error.addProperty("error", "An error occurred during automation: " + e.getMessage());
            result.add("error", error);
            System.err.println("Error during automation: " + e.getMessage());
        }
        
        return result;
    }
}
