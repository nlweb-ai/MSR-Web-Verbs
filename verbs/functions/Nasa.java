import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * NASA API wrapper for various NASA services
 * Extends BaseApiClient for HTTP functionality
 */
public class Nasa extends BaseApiClient {
    private static final String BASE_URL = "https://api.nasa.gov";
    
    public Nasa() {
        super(ApiUtil.buildNasaUserAgent(), null); // NASA uses API key, not Bearer token
    }
    
    /**
     * Get the current user agent string for debugging/verification
     * @return The user agent string being used
     */
    public static String getUserAgent() {
        return ApiUtil.buildNasaUserAgent();
    }
    
    /**
     * Retrieves the Astronomy Picture of the Day (APOD) from NASA's API.
     * @param date The date for the APOD in YYYY-MM-DD format (optional, defaults to today)
     * @param hd Whether to retrieve the high definition image
     * @return ApodResult containing title, url, explanation, and date
     * @throws IOException if a network error occurs
     * @throws InterruptedException if the request is interrupted
     */
    public ApodResult getApod(String date, boolean hd) throws IOException, InterruptedException {
        String apiKey = loadApiKey();
        StringBuilder urlBuilder = new StringBuilder(BASE_URL + "/planetary/apod?");
        if (date != null && !date.isEmpty()) {
            urlBuilder.append("date=").append(URLEncoder.encode(date, StandardCharsets.UTF_8)).append("&");
        }
        urlBuilder.append("hd=").append(hd).append("&");
        urlBuilder.append("api_key=").append(apiKey);
        String responseBody = performGet(urlBuilder.toString());
        return ApodResult.fromJson(responseBody);
    }
    
    /**
     * Retrieves a list of Near Earth Objects (NEOs) for a given date range.
     * @param startDate Start date in YYYY-MM-DD format
     * @param endDate End date in YYYY-MM-DD format (optional)
     * @return List of NeoResult objects
     * @throws IOException if a network error occurs
     * @throws InterruptedException if the request is interrupted
     */
    public List<NeoResult> getNeoFeed(String startDate, String endDate) throws IOException, InterruptedException {
        String apiKey = loadApiKey();
        String encodedStartDate = URLEncoder.encode(startDate, StandardCharsets.UTF_8);
        StringBuilder urlBuilder = new StringBuilder(BASE_URL + "/neo/rest/v1/feed?");
        urlBuilder.append("start_date=").append(encodedStartDate);
        if (endDate != null && !endDate.isEmpty()) {
            String encodedEndDate = URLEncoder.encode(endDate, StandardCharsets.UTF_8);
            urlBuilder.append("&end_date=").append(encodedEndDate);
        }
        urlBuilder.append("&api_key=").append(apiKey);
        String responseBody = performGet(urlBuilder.toString());
        return NeoResult.listFromJson(responseBody);
    }
    
    /**
     * Looks up a specific Near Earth Object by its NASA JPL small body ID.
     * @param asteroidId The asteroid ID to lookup
     * @return NeoResult for the specific asteroid
     * @throws IOException if a network error occurs
     * @throws InterruptedException if the request is interrupted
     */
    public NeoResult getNeoLookup(int asteroidId) throws IOException, InterruptedException {
        String apiKey = loadApiKey();
        String url = String.format("%s/neo/rest/v1/neo/%d?api_key=%s", 
                BASE_URL, asteroidId, apiKey);
        String responseBody = performGet(url);
        return NeoResult.fromJson(responseBody);
    }
    
    /**
     * Retrieves a list of Near Earth Objects from the browse endpoint.
     * @return List of NeoResult objects from the browse endpoint
     * @throws IOException if a network error occurs
     * @throws InterruptedException if the request is interrupted
     */
    public List<NeoResult> getNeoBrowse() throws IOException, InterruptedException {
        String apiKey = loadApiKey();
        String url = String.format("%s/neo/rest/v1/neo/browse?api_key=%s", 
                BASE_URL, apiKey);
        String responseBody = performGet(url);
        return NeoResult.listFromJson(responseBody);
    }
    
    /**
     * Simple JSON parsing to extract Near Earth Object data using regex
     * In a real application, you'd use a proper JSON library like Jackson or Gson
     * @param jsonResponse The JSON response string
     * @return List of NEO names or identifiers
     */
    private static List<String> parseNeoData(String jsonResponse) {
        List<String> neoData = new ArrayList<>();
        
        // Extract NEO names from the response
        Pattern namePattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
        Pattern idPattern = Pattern.compile("\"id\"\\s*:\\s*\"([^\"]+)\"");
        
        Matcher nameMatcher = namePattern.matcher(jsonResponse);
        Matcher idMatcher = idPattern.matcher(jsonResponse);
        
        // Prefer names over IDs
        while (nameMatcher.find()) {
            neoData.add(nameMatcher.group(1));
        }
        
        // If no names found, use IDs
        if (neoData.isEmpty()) {
            while (idMatcher.find()) {
                neoData.add("NEO ID: " + idMatcher.group(1));
            }
        }
        
        return neoData;
    }
    /**
     * Load the NASA API key from the .env file
     * @return The API key, or "DEMO_KEY" if not found
     */
    private static String loadApiKey() {
        String apiKey = ApiUtil.loadEnvValue("NASA_API_KEY");
        return apiKey != null ? apiKey : "DEMO_KEY";
    }
    /**
     * Result class for Astronomy Picture of the Day (APOD).
     */
    public static class ApodResult {
        public String title;
        public String url;
        public String explanation;
        public LocalDate date;

        public static ApodResult fromJson(String json) {
            ApodResult result = new ApodResult();
            result.title = ApiUtil.extractJsonField(json, "title");
            result.url = ApiUtil.extractJsonField(json, "url");
            result.explanation = ApiUtil.extractJsonField(json, "explanation");
            String dateStr = ApiUtil.extractJsonField(json, "date");
            if (dateStr != null && !dateStr.isEmpty()) {
                result.date = LocalDate.parse(dateStr);
            }
            return result;
        }
    }

    /**
     * Result class for Near Earth Object (NEO) data.
     */
    public static class NeoResult {
        public String name;
        public String id;
        public LocalDate closeApproachDate;
        public Double estimatedDiameterKm;
        public CurrencyAmount missDistance;
        public Duration relativeVelocity;

        public static List<NeoResult> listFromJson(String json) {
            // This is a placeholder: in production, use a real JSON parser
            List<String> names = parseNeoData(json);
            List<NeoResult> results = new ArrayList<>();
            for (String name : names) {
                NeoResult neo = new NeoResult();
                neo.name = name;
                results.add(neo);
            }
            return results;
        }

        public static NeoResult fromJson(String json) {
            // This is a placeholder: in production, use a real JSON parser
            NeoResult neo = new NeoResult();
            neo.name = ApiUtil.extractJsonField(json, "name");
            neo.id = ApiUtil.extractJsonField(json, "id");
            // Optionally parse more fields if needed
            return neo;
        }
    }
}
