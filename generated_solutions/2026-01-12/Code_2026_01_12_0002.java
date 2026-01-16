import java.nio.file.Paths;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.time.LocalDate;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonArray;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;
public class Code_2026_01_12_0002 {
    static BrowserContext context = null;
    static java.util.Scanner scanner= new java.util.Scanner(System.in);
    public static void main(String[] args) {
        try (Playwright playwright = Playwright.create()) {
            String userDataDir = System.getProperty("user.home") +"\\AppData\\Local\\Google\\Chrome\\User Data\\Default";
            BrowserType.LaunchPersistentContextOptions options = new BrowserType.LaunchPersistentContextOptions()
                .setChannel("chrome")
                .setHeadless(false)
                .setArgs(java.util.Arrays.asList(
                    "--disable-blink-features=AutomationControlled",
                    //"--no-sandbox",
                    //"--disable-web-security",
                    "--disable-infobars",
                    "--disable-extensions",
                    "--start-maximized"
                ));
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
            // Append result to known_facts.md
            try {
                String resultStr = "\n\n## Refinement Round\n" + prettyResult + "\n";
                Files.write(
                    Paths.get("tasks\\2026-01-12\\known_facts.md"),
                    resultStr.getBytes(),
                    StandardOpenOption.APPEND
                );
            } catch (Exception e) {
                System.err.println("Failed to append to known_facts.md: " + e.getMessage());
            }
            context.close();
        }
    }
    /* Do not modify anything above this line.
       The following "automate(...)" function is the one you should modify.
       The current function body is just an example specifically about youtube.
    */
    static JsonObject automate(BrowserContext context) {
        // Refinement Strategy: Calculate distances from each hotel to all 4 museums
        // and select the hotel with the smallest total distance.
        //
        // Based on known_facts.md, we have:
        // - 5 hotel options already identified
        // - 4 museums already selected:
        //   1. Anchorage Museum at Rasmuson Center
        //   2. Alaska Native Heritage Center
        //   3. Alaska Aviation Museum
        //   4. Oscar Anderson House Museum
        //
        // The new requirement asks to select the hotel with smallest total distance
        // to all museums. We'll use Google Maps get_direction API to calculate
        // distances from each hotel to each museum, sum them up, and recommend
        // the optimal hotel.
        maps_google_com mapsInstance = new maps_google_com(context);
        // Define hotels from known_facts.md
        String[] hotels = {
            "The Wildbirch Hotel - JdV by Hyatt, Anchorage",
            "Hyatt Place Anchorage-Midtown",
            "La Quinta by Wyndham Anchorage Airport",
            "The Voyager Inn, Anchorage",
            "Baymont Inn & Suites by Wyndham Anchorage Airport"
        };
        // Define museums from known_facts.md
        String[] museums = {
            "Anchorage Museum at Rasmuson Center",
            "Alaska Native Heritage Center",
            "Alaska Aviation Museum",
            "Oscar Anderson House Museum"
        };
        JsonObject result = new JsonObject();
        JsonArray hotelDistanceAnalysis = new JsonArray();
        String bestHotel = null;
        double minTotalDistance = Double.MAX_VALUE;
        // For each hotel, calculate total distance to all museums
        for (String hotel : hotels) {
            JsonObject hotelData = new JsonObject();
            hotelData.addProperty("hotel_name", hotel);
            JsonArray museumDistances = new JsonArray();
            double totalDistance = 0.0;
            boolean allDistancesValid = true;
            // Calculate distance from this hotel to each museum
            for (String museum : museums) {
                JsonObject distanceInfo = new JsonObject();
                distanceInfo.addProperty("museum", museum);
                try {
                    // Get direction information from hotel to museum
                    maps_google_com.DirectionResult dirResult =
                        mapsInstance.get_direction(hotel, museum);
                    distanceInfo.addProperty("distance", dirResult.distance);
                    distanceInfo.addProperty("travel_time", dirResult.travelTime);
                    // Parse distance string to extract numeric value
                    // Expecting format like "5.2 mi" or "3.1 km"
                    String distStr = dirResult.distance;
                    double distValue = parseDistance(distStr);
                    if (distValue >= 0) {
                        totalDistance += distValue;
                    } else {
                        allDistancesValid = false;
                    }
                } catch (Exception e) {
                    distanceInfo.addProperty("error", e.getMessage());
                    allDistancesValid = false;
                }
                museumDistances.add(distanceInfo);
            }
            hotelData.add("museum_distances", museumDistances);
            hotelData.addProperty("total_distance", totalDistance);
            hotelData.addProperty("all_distances_valid", allDistancesValid);
            // Track the hotel with minimum total distance
            if (allDistancesValid && totalDistance < minTotalDistance) {
                minTotalDistance = totalDistance;
                bestHotel = hotel;
            }
            hotelDistanceAnalysis.add(hotelData);
        }
        result.add("hotel_distance_analysis", hotelDistanceAnalysis);
        result.addProperty("recommended_hotel", bestHotel);
        result.addProperty("minimum_total_distance", minTotalDistance);
        // Add reasoning to explain the recommendation
        result.addProperty("reasoning",
            "Calculated the total distance from each of the 5 hotel options to all 4 museums. " +
            "The hotel with the smallest cumulative distance is recommended, as it minimizes " +
            "travel time and makes it most convenient to visit all museums during the trip.");
        // Reference the date interpretation from previous refinement
        result.addProperty("date_context",
            "Trip dates: January 21-24, 2026 (check-in Jan 21, check-out Jan 24). " +
            "Full museum visit days: January 22-23, 2026.");
        return result;
    }
    /**
     * Helper method to parse distance strings like "5.2 mi" or "3.1 km" into numeric values.
     * Converts everything to miles for consistent comparison.
     * @param distanceStr Distance string from Google Maps
     * @return Distance in miles, or -1 if parsing fails
     */
    private static double parseDistance(String distanceStr) {
        try {
            distanceStr = distanceStr.trim().toLowerCase();
            // Extract numeric part
            String[] parts = distanceStr.split("\\s+");
            if (parts.length < 2) return -1;
            double value = Double.parseDouble(parts[0].replace(",", ""));
            String unit = parts[1];
            // Convert to miles if needed
            if (unit.contains("km")) {
                return value * 0.621371; // km to miles
            } else if (unit.contains("mi")) {
                return value;
            } else if (unit.contains("ft")) {
                return value / 5280.0; // feet to miles
            } else if (unit.contains("m") && !unit.contains("mi")) {
                return value * 0.000621371; // meters to miles
            }
            return -1;
        } catch (Exception e) {
            return -1;
        }
    }
}