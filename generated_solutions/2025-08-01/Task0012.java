import java.nio.file.Paths;
import java.time.LocalDate;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;


public class Task0012 {
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
        
        // 1. Search for apartments in Austin, Texas with rent between $1800-$2800
        redfin_com redfin = new redfin_com(context);
        redfin_com.ApartmentSearchResult apartmentResults = redfin.searchApartments("Austin, Texas", 1800, 2800);
        
        JsonObject apartmentInfo = new JsonObject();
        apartmentInfo.addProperty("location", "Austin, Texas");
        apartmentInfo.addProperty("minRent", 1800);
        apartmentInfo.addProperty("maxRent", 2800);
        
        if (apartmentResults.error != null) {
            apartmentInfo.addProperty("error", apartmentResults.error);
        }
        
        JsonArray apartmentsArray = new JsonArray();
        double totalRent = 0.0;
        int validRentCount = 0;
        double minRent = Double.MAX_VALUE;
        double maxRent = 0.0;
        
        for (redfin_com.ApartmentInfo apartment : apartmentResults.apartments) {
            JsonObject apartmentObj = new JsonObject();
            apartmentObj.addProperty("address", apartment.address);
            apartmentObj.addProperty("url", apartment.url);
            
            if (apartment.price != null) {
                apartmentObj.addProperty("rentAmount", apartment.price.amount);
                apartmentObj.addProperty("currency", apartment.price.currency);
                
                totalRent += apartment.price.amount;
                validRentCount++;
                minRent = Math.min(minRent, apartment.price.amount);
                maxRent = Math.max(maxRent, apartment.price.amount);
            } else {
                apartmentObj.addProperty("rentAmount", (String) null);
                apartmentObj.addProperty("currency", (String) null);
            }
            apartmentsArray.add(apartmentObj);
        }
        
        apartmentInfo.add("apartments", apartmentsArray);
        
        // Calculate rent statistics
        JsonObject budgetAnalysis = new JsonObject();
        budgetAnalysis.addProperty("totalApartmentsFound", apartmentResults.apartments.size());
        if (validRentCount > 0) {
            double averageRent = totalRent / validRentCount;
            budgetAnalysis.addProperty("averageRent", Math.round(averageRent * 100.0) / 100.0);
            budgetAnalysis.addProperty("minRentFound", Math.round(minRent * 100.0) / 100.0);
            budgetAnalysis.addProperty("maxRentFound", Math.round(maxRent * 100.0) / 100.0);
            budgetAnalysis.addProperty("apartmentsWithValidPricing", validRentCount);
            
            // Budget assessment
            if (averageRent <= 2300) {
                budgetAnalysis.addProperty("budgetAssessment", "Budget looks reasonable - average rent is within comfortable range");
            } else if (averageRent <= 2600) {
                budgetAnalysis.addProperty("budgetAssessment", "Budget is tight but manageable - consider upper range of budget");
            } else {
                budgetAnalysis.addProperty("budgetAssessment", "May need to adjust budget expectations - average rent exceeds comfortable range");
            }
        } else {
            budgetAnalysis.addProperty("budgetAssessment", "No valid pricing data found");
        }
        
        result.add("apartmentSearch", apartmentInfo);
        result.add("budgetAnalysis", budgetAnalysis);
        
        // 2. Check current weather in Austin, Texas
        try {
            OpenWeather weather = new OpenWeather();
            // Austin, Texas coordinates (approximate)
            double austinLat = 30.2672;
            double austinLon = -97.7431;
            
            OpenWeather.CurrentWeatherData currentWeather = weather.getCurrentWeather(austinLat, austinLon);
            
            JsonObject weatherInfo = new JsonObject();
            weatherInfo.addProperty("cityName", currentWeather.getCityName());
            weatherInfo.addProperty("country", currentWeather.getCountry());
            weatherInfo.addProperty("date", currentWeather.getDate().toString());
            weatherInfo.addProperty("condition", currentWeather.getCondition());
            weatherInfo.addProperty("description", currentWeather.getDescription());
            weatherInfo.addProperty("temperature", Math.round(currentWeather.getTemperature() * 100.0) / 100.0);
            weatherInfo.addProperty("feelsLike", Math.round(currentWeather.getFeelsLike() * 100.0) / 100.0);
            weatherInfo.addProperty("tempMin", Math.round(currentWeather.getTempMin() * 100.0) / 100.0);
            weatherInfo.addProperty("tempMax", Math.round(currentWeather.getTempMax() * 100.0) / 100.0);
            weatherInfo.addProperty("humidity", currentWeather.getHumidity());
            weatherInfo.addProperty("windSpeed", Math.round(currentWeather.getWindSpeed() * 100.0) / 100.0);
            weatherInfo.addProperty("cloudiness", currentWeather.getCloudiness());
            
            // Climate assessment for moving
            String climateAssessment;
            if (currentWeather.getTemperature() > 30) {
                climateAssessment = "Hot climate - pack light, breathable clothing and sun protection";
            } else if (currentWeather.getTemperature() > 20) {
                climateAssessment = "Warm climate - comfortable temperatures, pack summer and transitional clothes";
            } else if (currentWeather.getTemperature() > 10) {
                climateAssessment = "Mild climate - pack layers and light jackets";
            } else {
                climateAssessment = "Cool climate - pack warm clothing and jackets";
            }
            weatherInfo.addProperty("climateAssessment", climateAssessment);
            
            result.add("currentWeather", weatherInfo);
            
        } catch (java.io.IOException | InterruptedException e) {
            JsonObject weatherError = new JsonObject();
            weatherError.addProperty("error", "Failed to get weather data: " + e.getMessage());
            result.add("currentWeather", weatherError);
        }
        
        // 3. Search for flights from Seattle, WA to Austin, TX for house-hunting trip
        alaskaair_com alaskaAir = new alaskaair_com(context);
        LocalDate outboundDate = LocalDate.of(2025, 8, 20);
        LocalDate returnDate = LocalDate.of(2025, 8, 22);
        
        alaskaair_com.SearchFlightsResult flightResults = alaskaAir.searchFlights("SEA", "AUS", outboundDate, returnDate);
        
        JsonObject flightInfo = new JsonObject();
        flightInfo.addProperty("origin", "Seattle, WA (SEA)");
        flightInfo.addProperty("destination", "Austin, TX (AUS)");
        flightInfo.addProperty("outboundDate", outboundDate.toString());
        flightInfo.addProperty("returnDate", returnDate.toString());
        
        if (flightResults.message != null) {
            flightInfo.addProperty("message", flightResults.message);
        }
        
        if (flightResults.flightInfo != null) {
            JsonArray flightsArray = new JsonArray();
            for (String flight : flightResults.flightInfo.flights) {
                flightsArray.add(flight);
            }
            flightInfo.add("availableFlights", flightsArray);
            
            if (flightResults.flightInfo.price != null) {
                flightInfo.addProperty("priceAmount", flightResults.flightInfo.price.amount);
                flightInfo.addProperty("priceCurrency", flightResults.flightInfo.price.currency);
            }
        }
        
        result.add("flightSearch", flightInfo);
        
        // 4. Search YouTube for "moving to Austin Texas" videos
        youtube_com youtube = new youtube_com(context);
        java.util.List<youtube_com.YouTubeVideoInfo> youtubeResults = youtube.searchVideos("moving to Austin Texas");
        
        JsonObject youtubeInfo = new JsonObject();
        youtubeInfo.addProperty("searchQuery", "moving to Austin Texas");
        
        JsonArray videosArray = new JsonArray();
        for (youtube_com.YouTubeVideoInfo video : youtubeResults) {
            JsonObject videoObj = new JsonObject();
            videoObj.addProperty("title", video.title);
            videoObj.addProperty("url", video.url);
            
            // Format Duration as hh:mm:ss or mm:ss
            long s = video.length.getSeconds();
            long h = s / 3600;
            long m = (s % 3600) / 60;
            long sec = s % 60;
            String lenStr = h > 0 ? String.format("%d:%02d:%02d", h, m, sec) : String.format("%d:%02d", m, sec);
            videoObj.addProperty("length", lenStr);
            
            videosArray.add(videoObj);
        }
        youtubeInfo.add("videos", videosArray);
        youtubeInfo.addProperty("purpose", "Educational content about living in Austin, Texas - tips from locals and relocation advice");
        
        result.add("youtubeResearch", youtubeInfo);
        
        // Add summary section
        JsonObject summary = new JsonObject();
        summary.addProperty("relocationType", "Work relocation to Austin, Texas");
        summary.addProperty("housingBudget", "$1800-$2800/month");
        summary.addProperty("houseHuntingTrip", "August 20-22, 2025 (Seattle to Austin)");
        summary.addProperty("nextSteps", "Review apartment options, book house-hunting flight, watch educational videos, prepare for Austin climate");
        
        result.add("relocationSummary", summary);
        
        return result;
    }
}
