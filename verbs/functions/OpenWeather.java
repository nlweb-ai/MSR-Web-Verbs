import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * OpenWeather API wrapper for current weather data
 * Extends BaseApiClient for HTTP functionality
 */
public class OpenWeather extends BaseApiClient {
    private static final String BASE_URL = "https://api.openweathermap.org/data/2.5";
    private static final String DEFAULT_UNITS = "metric";
    private static final String DEFAULT_LANG = "en";
    
    /**
     * Represents current weather data including temperature, conditions, and environmental factors.
     */
    public static class CurrentWeatherData {
        private final String cityName;
        private final String country;
        private final double latitude;
        private final double longitude;
        private final LocalDate date;
        private final String condition;
        private final String description;
        private final double temperature;
        private final double feelsLike;
        private final double tempMin;
        private final double tempMax;
        private final int humidity;
        private final int pressure;
        private final double windSpeed;
        private final int windDirection;
        private final double visibility;
        private final int cloudiness;

        public CurrentWeatherData(String cityName, String country, double latitude, double longitude,
                                LocalDate date, String condition, String description, double temperature,
                                double feelsLike, double tempMin, double tempMax, int humidity, int pressure,
                                double windSpeed, int windDirection, double visibility, int cloudiness) {
            this.cityName = cityName;
            this.country = country;
            this.latitude = latitude;
            this.longitude = longitude;
            this.date = date;
            this.condition = condition;
            this.description = description;
            this.temperature = temperature;
            this.feelsLike = feelsLike;
            this.tempMin = tempMin;
            this.tempMax = tempMax;
            this.humidity = humidity;
            this.pressure = pressure;
            this.windSpeed = windSpeed;
            this.windDirection = windDirection;
            this.visibility = visibility;
            this.cloudiness = cloudiness;
        }

        public String getCityName() { return cityName; }
        public String getCountry() { return country; }
        public double getLatitude() { return latitude; }
        public double getLongitude() { return longitude; }
        public LocalDate getDate() { return date; }
        public String getCondition() { return condition; }
        public String getDescription() { return description; }
        public double getTemperature() { return temperature; }
        public double getFeelsLike() { return feelsLike; }
        public double getTempMin() { return tempMin; }
        public double getTempMax() { return tempMax; }
        public int getHumidity() { return humidity; }
        public int getPressure() { return pressure; }
        public double getWindSpeed() { return windSpeed; }
        public int getWindDirection() { return windDirection; }
        public double getVisibility() { return visibility; }
        public int getCloudiness() { return cloudiness; }
    }

    /**
     * Represents weather forecast data for multiple time periods.
     */
    public static class WeatherForecastData {
        private final String cityName;
        private final String country;
        private final double latitude;
        private final double longitude;
        private final List<ForecastEntry> forecasts;

        public WeatherForecastData(String cityName, String country, double latitude, double longitude, List<ForecastEntry> forecasts) {
            this.cityName = cityName;
            this.country = country;
            this.latitude = latitude;
            this.longitude = longitude;
            this.forecasts = forecasts;
        }

        public String getCityName() { return cityName; }
        public String getCountry() { return country; }
        public double getLatitude() { return latitude; }
        public double getLongitude() { return longitude; }
        public List<ForecastEntry> getForecasts() { return forecasts; }
    }

    /**
     * Represents a single forecast entry.
     */
    public static class ForecastEntry {
        private final LocalDateTime dateTime;
        private final String condition;
        private final String description;
        private final double temperature;
        private final double tempMin;
        private final double tempMax;
        private final int humidity;
        private final double windSpeed;
        private final int cloudiness;

        public ForecastEntry(LocalDateTime dateTime, String condition, String description,
                           double temperature, double tempMin, double tempMax, int humidity,
                           double windSpeed, int cloudiness) {
            this.dateTime = dateTime;
            this.condition = condition;
            this.description = description;
            this.temperature = temperature;
            this.tempMin = tempMin;
            this.tempMax = tempMax;
            this.humidity = humidity;
            this.windSpeed = windSpeed;
            this.cloudiness = cloudiness;
        }

        public LocalDateTime getDateTime() { return dateTime; }
        public String getCondition() { return condition; }
        public String getDescription() { return description; }
        public double getTemperature() { return temperature; }
        public double getTempMin() { return tempMin; }
        public double getTempMax() { return tempMax; }
        public int getHumidity() { return humidity; }
        public double getWindSpeed() { return windSpeed; }
        public int getCloudiness() { return cloudiness; }
    }

    /**
     * Represents air pollution data including AQI and pollutant concentrations.
     */
    public static class AirPollutionData {
        private final double latitude;
        private final double longitude;
        private final List<PollutionEntry> pollutionEntries;

        public AirPollutionData(double latitude, double longitude, List<PollutionEntry> pollutionEntries) {
            this.latitude = latitude;
            this.longitude = longitude;
            this.pollutionEntries = pollutionEntries;
        }

        public double getLatitude() { return latitude; }
        public double getLongitude() { return longitude; }
        public List<PollutionEntry> getPollutionEntries() { return pollutionEntries; }
    }

    /**
     * Represents a single pollution measurement entry.
     */
    public static class PollutionEntry {
        private final LocalDateTime dateTime;
        private final int aqi;
        private final double co;
        private final double no;
        private final double no2;
        private final double o3;
        private final double so2;
        private final double pm2_5;
        private final double pm10;
        private final double nh3;

        public PollutionEntry(LocalDateTime dateTime, int aqi, double co, double no, double no2,
                            double o3, double so2, double pm2_5, double pm10, double nh3) {
            this.dateTime = dateTime;
            this.aqi = aqi;
            this.co = co;
            this.no = no;
            this.no2 = no2;
            this.o3 = o3;
            this.so2 = so2;
            this.pm2_5 = pm2_5;
            this.pm10 = pm10;
            this.nh3 = nh3;
        }

        public LocalDateTime getDateTime() { return dateTime; }
        public int getAqi() { return aqi; }
        public double getCo() { return co; }
        public double getNo() { return no; }
        public double getNo2() { return no2; }
        public double getO3() { return o3; }
        public double getSo2() { return so2; }
        public double getPm2_5() { return pm2_5; }
        public double getPm10() { return pm10; }
        public double getNh3() { return nh3; }
    }

    /**
     * Represents location data including name, coordinates, and country information.
     */
    public static class LocationData {
        private final String name;
        private final double latitude;
        private final double longitude;
        private final String country;
        private final String state;
        private final String zipCode;

        public LocationData(String name, double latitude, double longitude, String country, String state, String zipCode) {
            this.name = name;
            this.latitude = latitude;
            this.longitude = longitude;
            this.country = country;
            this.state = state;
            this.zipCode = zipCode;
        }

        public String getName() { return name; }
        public double getLatitude() { return latitude; }
        public double getLongitude() { return longitude; }
        public String getCountry() { return country; }
        public String getState() { return state; }
        public String getZipCode() { return zipCode; }
    }
    
    public OpenWeather() {
        super(ApiUtil.buildOpenWeatherUserAgent());
    }
    
    /**
     * Parse weather JSON response into CurrentWeatherData object
     */
    private CurrentWeatherData parseCurrentWeatherResponse(String jsonResponse) {
        // Extract location information
        Pattern latPattern = Pattern.compile("\"lat\"\\s*:\\s*([\\d.-]+)");
        Pattern lonPattern = Pattern.compile("\"lon\"\\s*:\\s*([\\d.-]+)");
        Pattern namePattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
        Pattern countryPattern = Pattern.compile("\"country\"\\s*:\\s*\"([^\"]+)\"");
        
        // Extract weather condition
        Pattern weatherMainPattern = Pattern.compile("\"main\"\\s*:\\s*\"([^\"]+)\"");
        Pattern weatherDescPattern = Pattern.compile("\"description\"\\s*:\\s*\"([^\"]+)\"");
        
        // Extract temperature and related data
        Pattern tempPattern = Pattern.compile("\"temp\"\\s*:\\s*([\\d.-]+)");
        Pattern feelsLikePattern = Pattern.compile("\"feels_like\"\\s*:\\s*([\\d.-]+)");
        Pattern tempMinPattern = Pattern.compile("\"temp_min\"\\s*:\\s*([\\d.-]+)");
        Pattern tempMaxPattern = Pattern.compile("\"temp_max\"\\s*:\\s*([\\d.-]+)");
        Pattern humidityPattern = Pattern.compile("\"humidity\"\\s*:\\s*(\\d+)");
        Pattern pressurePattern = Pattern.compile("\"pressure\"\\s*:\\s*(\\d+)");
        
        // Extract wind data
        Pattern windSpeedPattern = Pattern.compile("\"speed\"\\s*:\\s*([\\d.-]+)");
        Pattern windDegPattern = Pattern.compile("\"deg\"\\s*:\\s*(\\d+)");
        
        // Extract visibility and clouds
        Pattern visibilityPattern = Pattern.compile("\"visibility\"\\s*:\\s*(\\d+)");
        Pattern cloudsPattern = Pattern.compile("\"all\"\\s*:\\s*(\\d+)");
        
        // Extract values using matchers
        String cityName = extractValue(namePattern, jsonResponse, "Unknown");
        String country = extractValue(countryPattern, jsonResponse, "Unknown");
        double latitude = Double.parseDouble(extractValue(latPattern, jsonResponse, "0.0"));
        double longitude = Double.parseDouble(extractValue(lonPattern, jsonResponse, "0.0"));
        LocalDate date = LocalDate.now();
        String condition = extractValue(weatherMainPattern, jsonResponse, "Unknown");
        String description = extractValue(weatherDescPattern, jsonResponse, "Unknown");
        double temperature = Double.parseDouble(extractValue(tempPattern, jsonResponse, "0.0"));
        double feelsLike = Double.parseDouble(extractValue(feelsLikePattern, jsonResponse, "0.0"));
        double tempMin = Double.parseDouble(extractValue(tempMinPattern, jsonResponse, "0.0"));
        double tempMax = Double.parseDouble(extractValue(tempMaxPattern, jsonResponse, "0.0"));
        int humidity = Integer.parseInt(extractValue(humidityPattern, jsonResponse, "0"));
        int pressure = Integer.parseInt(extractValue(pressurePattern, jsonResponse, "0"));
        double windSpeed = Double.parseDouble(extractValue(windSpeedPattern, jsonResponse, "0.0"));
        int windDirection = Integer.parseInt(extractValue(windDegPattern, jsonResponse, "0"));
        double visibility = Double.parseDouble(extractValue(visibilityPattern, jsonResponse, "0")) / 1000.0; // Convert to km
        int cloudiness = Integer.parseInt(extractValue(cloudsPattern, jsonResponse, "0"));
        
        return new CurrentWeatherData(cityName, country, latitude, longitude, date, condition, description,
                                    temperature, feelsLike, tempMin, tempMax, humidity, pressure,
                                    windSpeed, windDirection, visibility, cloudiness);
    }
    
    /**
     * Parse forecast JSON response into WeatherForecastData object
     */
    private WeatherForecastData parseForecastResponse(String jsonResponse) {
        // Extract location information
        Pattern namePattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
        Pattern countryPattern = Pattern.compile("\"country\"\\s*:\\s*\"([^\"]+)\"");
        Pattern latPattern = Pattern.compile("\"lat\"\\s*:\\s*([\\d.-]+)");
        Pattern lonPattern = Pattern.compile("\"lon\"\\s*:\\s*([\\d.-]+)");
        
        String cityName = extractValue(namePattern, jsonResponse, "Unknown");
        String country = extractValue(countryPattern, jsonResponse, "Unknown");
        double latitude = Double.parseDouble(extractValue(latPattern, jsonResponse, "0.0"));
        double longitude = Double.parseDouble(extractValue(lonPattern, jsonResponse, "0.0"));
        
        List<ForecastEntry> forecasts = new ArrayList<>();
        
        // Extract forecast entries from the "list" array
        Pattern listPattern = Pattern.compile("\"list\"\\s*:\\s*\\[(.*?)\\]", Pattern.DOTALL);
        Matcher listMatcher = listPattern.matcher(jsonResponse);
        
        if (listMatcher.find()) {
            String listContent = listMatcher.group(1);
            String[] forecastEntries = listContent.split("\\}\\s*,\\s*\\{");
            
            for (String entry : forecastEntries) {
                if (!entry.startsWith("{")) entry = "{" + entry;
                if (!entry.endsWith("}")) entry = entry + "}";
                
                // Extract forecast data
                Pattern dtPattern = Pattern.compile("\"dt\"\\s*:\\s*(\\d+)");
                Pattern tempPattern = Pattern.compile("\"temp\"\\s*:\\s*([\\d.-]+)");
                Pattern tempMinPattern = Pattern.compile("\"temp_min\"\\s*:\\s*([\\d.-]+)");
                Pattern tempMaxPattern = Pattern.compile("\"temp_max\"\\s*:\\s*([\\d.-]+)");
                Pattern weatherMainPattern = Pattern.compile("\"main\"\\s*:\\s*\"([^\"]+)\"");
                Pattern weatherDescPattern = Pattern.compile("\"description\"\\s*:\\s*\"([^\"]+)\"");
                Pattern windSpeedPattern = Pattern.compile("\"speed\"\\s*:\\s*([\\d.-]+)");
                Pattern humidityPattern = Pattern.compile("\"humidity\"\\s*:\\s*(\\d+)");
                Pattern cloudsPattern = Pattern.compile("\"all\"\\s*:\\s*(\\d+)");
                
                long timestamp = Long.parseLong(extractValue(dtPattern, entry, "0"));
                LocalDateTime dateTime = LocalDateTime.ofInstant(Instant.ofEpochSecond(timestamp), ZoneId.systemDefault());
                String condition = extractValue(weatherMainPattern, entry, "Unknown");
                String description = extractValue(weatherDescPattern, entry, "Unknown");
                double temperature = Double.parseDouble(extractValue(tempPattern, entry, "0.0"));
                double tempMin = Double.parseDouble(extractValue(tempMinPattern, entry, "0.0"));
                double tempMax = Double.parseDouble(extractValue(tempMaxPattern, entry, "0.0"));
                int humidity = Integer.parseInt(extractValue(humidityPattern, entry, "0"));
                double windSpeed = Double.parseDouble(extractValue(windSpeedPattern, entry, "0.0"));
                int cloudiness = Integer.parseInt(extractValue(cloudsPattern, entry, "0"));
                
                forecasts.add(new ForecastEntry(dateTime, condition, description, temperature, tempMin, tempMax, humidity, windSpeed, cloudiness));
            }
        }
        
        return new WeatherForecastData(cityName, country, latitude, longitude, forecasts);
    }
    
    /**
     * Parse air pollution JSON response into AirPollutionData object
     */
    private AirPollutionData parseAirPollutionResponse(String jsonResponse) {
        Pattern latPattern = Pattern.compile("\"lat\"\\s*:\\s*([\\d.-]+)");
        Pattern lonPattern = Pattern.compile("\"lon\"\\s*:\\s*([\\d.-]+)");
        
        double latitude = Double.parseDouble(extractValue(latPattern, jsonResponse, "0.0"));
        double longitude = Double.parseDouble(extractValue(lonPattern, jsonResponse, "0.0"));
        
        List<PollutionEntry> pollutionEntries = new ArrayList<>();
        
        // Extract pollution data from the "list" array
        Pattern listPattern = Pattern.compile("\"list\"\\s*:\\s*\\[(.*?)\\]", Pattern.DOTALL);
        Matcher listMatcher = listPattern.matcher(jsonResponse);
        
        if (listMatcher.find()) {
            String listContent = listMatcher.group(1);
            String[] entries = listContent.split("\\}\\s*,\\s*\\{");
            
            for (String entry : entries) {
                if (!entry.startsWith("{")) entry = "{" + entry;
                if (!entry.endsWith("}")) entry = entry + "}";
                
                // Extract pollution data
                Pattern dtPattern = Pattern.compile("\"dt\"\\s*:\\s*(\\d+)");
                Pattern aqiPattern = Pattern.compile("\"aqi\"\\s*:\\s*(\\d+)");
                Pattern coPattern = Pattern.compile("\"co\"\\s*:\\s*([\\d.-]+)");
                Pattern noPattern = Pattern.compile("\"no\"\\s*:\\s*([\\d.-]+)");
                Pattern no2Pattern = Pattern.compile("\"no2\"\\s*:\\s*([\\d.-]+)");
                Pattern o3Pattern = Pattern.compile("\"o3\"\\s*:\\s*([\\d.-]+)");
                Pattern so2Pattern = Pattern.compile("\"so2\"\\s*:\\s*([\\d.-]+)");
                Pattern pm2_5Pattern = Pattern.compile("\"pm2_5\"\\s*:\\s*([\\d.-]+)");
                Pattern pm10Pattern = Pattern.compile("\"pm10\"\\s*:\\s*([\\d.-]+)");
                Pattern nh3Pattern = Pattern.compile("\"nh3\"\\s*:\\s*([\\d.-]+)");
                
                long timestamp = Long.parseLong(extractValue(dtPattern, entry, "0"));
                LocalDateTime dateTime = LocalDateTime.ofInstant(Instant.ofEpochSecond(timestamp), ZoneId.systemDefault());
                int aqi = Integer.parseInt(extractValue(aqiPattern, entry, "0"));
                double co = Double.parseDouble(extractValue(coPattern, entry, "0.0"));
                double no = Double.parseDouble(extractValue(noPattern, entry, "0.0"));
                double no2 = Double.parseDouble(extractValue(no2Pattern, entry, "0.0"));
                double o3 = Double.parseDouble(extractValue(o3Pattern, entry, "0.0"));
                double so2 = Double.parseDouble(extractValue(so2Pattern, entry, "0.0"));
                double pm2_5 = Double.parseDouble(extractValue(pm2_5Pattern, entry, "0.0"));
                double pm10 = Double.parseDouble(extractValue(pm10Pattern, entry, "0.0"));
                double nh3 = Double.parseDouble(extractValue(nh3Pattern, entry, "0.0"));
                
                pollutionEntries.add(new PollutionEntry(dateTime, aqi, co, no, no2, o3, so2, pm2_5, pm10, nh3));
            }
        }
        
        return new AirPollutionData(latitude, longitude, pollutionEntries);
    }
    
    /**
     * Parse geocoding JSON response into LocationData objects
     */
    private List<LocationData> parseGeocodingResponse(String jsonResponse) {
        List<LocationData> locations = new ArrayList<>();
        
        // Check if it's an array response or single object
        boolean isArrayResponse = jsonResponse.trim().startsWith("[");
        
        if (isArrayResponse) {
            // Handle array response for direct/reverse geocoding
            String content = jsonResponse.trim();
            if (content.startsWith("[") && content.endsWith("]")) {
                content = content.substring(1, content.length() - 1);
            }
            
            String[] locationEntries = content.split("\\}\\s*,\\s*\\{");
            
            for (String entry : locationEntries) {
                if (!entry.startsWith("{")) entry = "{" + entry;
                if (!entry.endsWith("}")) entry = entry + "}";
                
                locations.add(parseLocationEntry(entry));
            }
        } else {
            // Single object response (zip code geocoding)
            locations.add(parseLocationEntry(jsonResponse));
        }
        
        return locations;
    }
    
    /**
     * Parse a single location entry
     */
    private LocationData parseLocationEntry(String entry) {
        Pattern namePattern = Pattern.compile("\"name\"\\s*:\\s*\"([^\"]+)\"");
        Pattern latPattern = Pattern.compile("\"lat\"\\s*:\\s*([\\d.-]+)");
        Pattern lonPattern = Pattern.compile("\"lon\"\\s*:\\s*([\\d.-]+)");
        Pattern countryPattern = Pattern.compile("\"country\"\\s*:\\s*\"([^\"]+)\"");
        Pattern statePattern = Pattern.compile("\"state\"\\s*:\\s*\"([^\"]+)\"");
        Pattern zipPattern = Pattern.compile("\"zip\"\\s*:\\s*\"([^\"]+)\"");
        
        String name = extractValue(namePattern, entry, "Unknown");
        double latitude = Double.parseDouble(extractValue(latPattern, entry, "0.0"));
        double longitude = Double.parseDouble(extractValue(lonPattern, entry, "0.0"));
        String country = extractValue(countryPattern, entry, "Unknown");
        String state = extractValue(statePattern, entry, null);
        String zipCode = extractValue(zipPattern, entry, null);
        
        return new LocationData(name, latitude, longitude, country, state, zipCode);
    }
    
    /**
     * Helper method to extract value from regex pattern with default value
     */
    private String extractValue(Pattern pattern, String text, String defaultValue) {
        Matcher matcher = pattern.matcher(text);
        return matcher.find() ? matcher.group(1) : defaultValue;
    }
    
    /**
     * Gets current weather data for a specific location.
     * Provides comprehensive weather information including temperature, conditions, wind, and atmospheric data.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @param units Units of measurement - "standard" (Kelvin), "metric" (Celsius), or "imperial" (Fahrenheit)
     * @param lang Language code for weather descriptions (e.g., "en", "es", "fr")
     * @return CurrentWeatherData object containing all weather information for the location
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public CurrentWeatherData getCurrentWeather(double lat, double lon, String units, String lang) throws IOException, InterruptedException {
        // Use defaults if not provided
        if (units == null || units.trim().isEmpty()) {
            units = DEFAULT_UNITS;
        }
        if (lang == null || lang.trim().isEmpty()) {
            lang = DEFAULT_LANG;
        }
        
        String apiKey = loadApiKey();
        if (apiKey == null) {
            throw new IllegalStateException("OPENWEATHER_API_KEY not found in .env file");
        }
        
        String url = String.format("%s/weather?lat=%s&lon=%s&appid=%s&units=%s&lang=%s", 
                BASE_URL, lat, lon, apiKey, units, lang);
        
        try {
            String responseBody = performGet(url);
            return parseCurrentWeatherResponse(responseBody);
        } catch (IOException e) {
            if (e.getMessage().contains("HTTP 400") && (e.getMessage().contains("wrong latitude") || e.getMessage().contains("wrong longitude"))) {
                // Handle invalid coordinates gracefully - return default weather data with error info
                return new CurrentWeatherData("Error: Invalid coordinates", "Error", lat, lon, LocalDate.now(),
                        "Error", "Invalid coordinates provided. Latitude must be between -90 and 90, longitude between -180 and 180",
                        0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0, 0.0, 0);
            }
            throw e; // Re-throw other IOExceptions
        }
    }
    
    /**
     * Gets current weather data for a location with default units (metric) and language (English).
     * This is a convenience method that uses metric units (Celsius) and English descriptions.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @return CurrentWeatherData object containing all weather information for the location
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public CurrentWeatherData getCurrentWeather(double lat, double lon) throws IOException, InterruptedException {
        return getCurrentWeather(lat, lon, DEFAULT_UNITS, DEFAULT_LANG);
    }
    
    /**
     * Load the OpenWeather API key from the .env file
     * @return The API key, or null if not found
     */
    private static String loadApiKey() {
        return ApiUtil.loadEnvValue("OPENWEATHER_API_KEY");
    }
    /**
     * Gets 5-day weather forecast data for a specific location.
     * Returns detailed forecast information with data points every 3 hours for the next 5 days.
     * Each forecast entry includes temperature, weather conditions, wind, and humidity information.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @param units Units of measurement - "standard" (Kelvin), "metric" (Celsius), or "imperial" (Fahrenheit)
     * @param lang Language code for weather descriptions (e.g., "en", "es", "fr")
     * @param cnt Number of forecast data points to return (max 40 for 5 days at 3-hour intervals)
     * @return WeatherForecastData object containing location info and list of forecast entries
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public WeatherForecastData getForecast5Day(double lat, double lon, String units, String lang, Integer cnt) throws IOException, InterruptedException {
        // Use defaults if not provided
        if (units == null || units.trim().isEmpty()) {
            units = DEFAULT_UNITS;
        }
        if (lang == null || lang.trim().isEmpty()) {
            lang = DEFAULT_LANG;
        }
        
        String apiKey = loadApiKey();
        if (apiKey == null) {
            throw new IllegalStateException("OPENWEATHER_API_KEY not found in .env file");
        }
        
        String url = String.format("%s/forecast?lat=%s&lon=%s&appid=%s&units=%s&lang=%s", 
                BASE_URL, lat, lon, apiKey, units, lang);
        
        if (cnt != null && cnt > 0) {
            url += "&cnt=" + cnt;
        }
        
        String responseBody = performGet(url);
        return parseForecastResponse(responseBody);
    }
    
    /**
     * Gets 5-day weather forecast data for a location with default units (metric) and language (English).
     * This is a convenience method that uses metric units (Celsius) and English descriptions.
     * Returns all available forecast data points (up to 40 entries covering 5 days).
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @return WeatherForecastData object containing location info and list of forecast entries
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public WeatherForecastData getForecast5Day(double lat, double lon) throws IOException, InterruptedException {
        return getForecast5Day(lat, lon, DEFAULT_UNITS, DEFAULT_LANG, null);
    }
    
    /**
     * Gets 5-day weather forecast data for a location with specified number of data points.
     * Uses default units (metric) and language (English) but allows limiting the number of forecast entries.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @param cnt Number of forecast data points to return (max 40)
     * @return WeatherForecastData object containing location info and list of forecast entries
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public WeatherForecastData getForecast5Day(double lat, double lon, int cnt) throws IOException, InterruptedException {
        return getForecast5Day(lat, lon, DEFAULT_UNITS, DEFAULT_LANG, cnt);
    }
    
    /**
     * Get the current user agent string for debugging/verification
     * @return The user agent string being used
     */
    public static String getUserAgent() {
        return ApiUtil.buildOpenWeatherUserAgent();
    }
    
    /**
     * Gets current air pollution data for a specific location.
     * Provides Air Quality Index (AQI) and concentrations of various pollutants including
     * CO, NO, NO2, O3, SO2, PM2.5, PM10, and NH3.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @return AirPollutionData object containing location and pollution measurements
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public AirPollutionData getCurrentAirPollution(double lat, double lon) throws IOException, InterruptedException {
        String apiKey = loadApiKey();
        if (apiKey == null) {
            throw new IllegalStateException("OPENWEATHER_API_KEY not found in .env file");
        }
        
        String url = String.format("%s/air_pollution?lat=%s&lon=%s&appid=%s", 
                BASE_URL, lat, lon, apiKey);
        
        try {
            String responseBody = performGet(url);
            return parseAirPollutionResponse(responseBody);
        } catch (IOException e) {
            if (e.getMessage().contains("HTTP 400") && (e.getMessage().contains("wrong latitude") || e.getMessage().contains("wrong longitude"))) {
                // Handle invalid coordinates gracefully - return empty pollution data with error info
                List<PollutionEntry> errorEntries = new ArrayList<>();
                errorEntries.add(new PollutionEntry(LocalDateTime.now(), 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0));
                return new AirPollutionData(lat, lon, errorEntries);
            }
            throw e; // Re-throw other IOExceptions
        }
    }
    
    /**
     * Gets air pollution forecast data for a specific location.
     * Provides forecasted Air Quality Index (AQI) and pollutant concentrations for the upcoming period.
     * The forecast typically covers 5 days with data points every few hours.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @return AirPollutionData object containing location and forecasted pollution measurements
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public AirPollutionData getAirPollutionForecast(double lat, double lon) throws IOException, InterruptedException {
        String apiKey = loadApiKey();
        if (apiKey == null) {
            throw new IllegalStateException("OPENWEATHER_API_KEY not found in .env file");
        }
        
        String url = String.format("%s/air_pollution/forecast?lat=%s&lon=%s&appid=%s", 
                BASE_URL, lat, lon, apiKey);
        
        try {
            String responseBody = performGet(url);
            return parseAirPollutionResponse(responseBody);
        } catch (IOException e) {
            if (e.getMessage().contains("HTTP 400") && (e.getMessage().contains("wrong latitude") || e.getMessage().contains("wrong longitude"))) {
                // Handle invalid coordinates gracefully - return empty pollution data with error info
                List<PollutionEntry> errorEntries = new ArrayList<>();
                errorEntries.add(new PollutionEntry(LocalDateTime.now(), 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0));
                return new AirPollutionData(lat, lon, errorEntries);
            }
            throw e; // Re-throw other IOExceptions
        }
    }
    
    /**
     * Gets historical air pollution data for a specific location within a time range.
     * Retrieves past Air Quality Index (AQI) and pollutant concentration data for analysis.
     * Useful for tracking pollution trends and conducting historical air quality studies.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @param start Start date as Unix timestamp (seconds since epoch)
     * @param end End date as Unix timestamp (seconds since epoch)
     * @return AirPollutionData object containing location and historical pollution measurements
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public AirPollutionData getHistoricalAirPollution(double lat, double lon, long start, long end) throws IOException, InterruptedException {
        String apiKey = loadApiKey();
        if (apiKey == null) {
            throw new IllegalStateException("OPENWEATHER_API_KEY not found in .env file");
        }
        
        String url = String.format("%s/air_pollution/history?lat=%s&lon=%s&start=%s&end=%s&appid=%s", 
                BASE_URL, lat, lon, start, end, apiKey);
        
        try {
            String responseBody = performGet(url);
            return parseAirPollutionResponse(responseBody);
        } catch (IOException e) {
            if (e.getMessage().contains("HTTP 400") && (e.getMessage().contains("wrong latitude") || e.getMessage().contains("wrong longitude"))) {
                // Handle invalid coordinates gracefully - return empty pollution data with error info
                List<PollutionEntry> errorEntries = new ArrayList<>();
                errorEntries.add(new PollutionEntry(LocalDateTime.now(), 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0));
                return new AirPollutionData(lat, lon, errorEntries);
            }
            throw e; // Re-throw other IOExceptions
        }
    }
    
    /**
     * Gets location data by searching for place names using direct geocoding.
     * Searches for locations by city name, state, and country codes. Supports various formats
     * like "London", "New York,NY,US", or "Paris,FR". Returns detailed geographic information
     * including coordinates, administrative divisions, and country data.
     * 
     * @param query Location name to search for (city name, optionally with state and country codes separated by commas)
     * @param limit Maximum number of locations to return (between 1 and 5)
     * @return List of LocationData objects containing matching locations with their geographic information
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public List<LocationData> getLocationsByName(String query, Integer limit) throws IOException, InterruptedException {
        if (query == null || query.trim().isEmpty()) {
            List<LocationData> errorResult = new ArrayList<>();
            errorResult.add(new LocationData("Error: Query cannot be empty", 0.0, 0.0, 
                          "Please provide a location name (e.g., 'London', 'New York,NY,US')", null, null));
            return errorResult;
        }
        
        String apiKey = loadApiKey();
        if (apiKey == null) {
            throw new IllegalStateException("OPENWEATHER_API_KEY not found in .env file");
        }
        
        String encodedQuery = URLEncoder.encode(query.trim(), StandardCharsets.UTF_8);
        String url = String.format("https://api.openweathermap.org/geo/1.0/direct?q=%s&appid=%s", 
                encodedQuery, apiKey);
        
        if (limit != null && limit > 0 && limit <= 5) {
            url += "&limit=" + limit;
        }
        
        try {
            String responseBody = performGet(url);
            return parseGeocodingResponse(responseBody);
        } catch (IOException e) {
            if (e.getMessage().contains("HTTP 400")) {
                List<LocationData> errorResult = new ArrayList<>();
                errorResult.add(new LocationData("Error: Invalid query", 0.0, 0.0, 
                              "Please check the location name format", null, null));
                return errorResult;
            }
            throw e;
        }
    }
    
    /**
     * Gets location data by searching for place names using direct geocoding with default limit.
     * This is a convenience method that searches for up to 5 matching locations.
     * 
     * @param query Location name to search for
     * @return List of LocationData objects containing matching locations (up to 5 results)
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public List<LocationData> getLocationsByName(String query) throws IOException, InterruptedException {
        return getLocationsByName(query, 5);
    }
    
    /**
     * Gets location data by zip/postal code using zip code geocoding.
     * Supports various formats including "10001", "E14,GB", or separate zip code and country parameters.
     * Returns detailed geographic information for the specified postal area.
     * 
     * @param zipCode Zip/postal code, optionally with country code (e.g., "E14,GB" or "10001")
     * @param countryCode ISO 3166 country code (optional if included in zipCode parameter)
     * @return List containing a single LocationData object for the specified zip code area
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public List<LocationData> getLocationByZipCode(String zipCode, String countryCode) throws IOException, InterruptedException {
        if (zipCode == null || zipCode.trim().isEmpty()) {
            List<LocationData> errorResult = new ArrayList<>();
            errorResult.add(new LocationData("Error: Zip code cannot be empty", 0.0, 0.0,
                          "Please provide a zip/postal code (e.g., '10001' or 'E14,GB')", null, null));
            return errorResult;
        }
        
        String apiKey = loadApiKey();
        if (apiKey == null) {
            throw new IllegalStateException("OPENWEATHER_API_KEY not found in .env file");
        }
        
        String zipParam = zipCode.trim();
        if (countryCode != null && !countryCode.trim().isEmpty() && !zipParam.contains(",")) {
            zipParam += "," + countryCode.trim();
        }
        
        String encodedZip = URLEncoder.encode(zipParam, StandardCharsets.UTF_8);
        String url = String.format("https://api.openweathermap.org/geo/1.0/zip?zip=%s&appid=%s", 
                encodedZip, apiKey);
        
        try {
            String responseBody = performGet(url);
            return parseGeocodingResponse(responseBody);
        } catch (IOException e) {
            if (e.getMessage().contains("HTTP 400") || e.getMessage().contains("HTTP 404")) {
                List<LocationData> errorResult = new ArrayList<>();
                errorResult.add(new LocationData("Error: Invalid zip/postal code", 0.0, 0.0,
                              "Please check the zip code format and country code", null, zipCode));
                return errorResult;
            }
            throw e;
        }
    }
    
    /**
     * Gets location data by zip/postal code using zip code geocoding without separate country code.
     * This is a convenience method for zip codes that already include country information
     * or for cases where the country code is not needed.
     * 
     * @param zipCode Zip/postal code (should include country code if needed, e.g., "E14,GB")
     * @return List containing a single LocationData object for the specified zip code area
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public List<LocationData> getLocationByZipCode(String zipCode) throws IOException, InterruptedException {
        return getLocationByZipCode(zipCode, null);
    }
    
    /**
     * Gets location data by coordinates using reverse geocoding.
     * Converts latitude and longitude coordinates into human-readable location information
     * including city names, administrative divisions, and country data. Useful for determining
     * location names from GPS coordinates or map selections.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @param limit Maximum number of location results to return (between 1 and 5)
     * @return List of LocationData objects containing locations near the specified coordinates
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public List<LocationData> getLocationsByCoordinates(double lat, double lon, Integer limit) throws IOException, InterruptedException {
        String apiKey = loadApiKey();
        if (apiKey == null) {
            throw new IllegalStateException("OPENWEATHER_API_KEY not found in .env file");
        }
        
        String url = String.format("https://api.openweathermap.org/geo/1.0/reverse?lat=%s&lon=%s&appid=%s", 
                lat, lon, apiKey);
        
        if (limit != null && limit > 0 && limit <= 5) {
            url += "&limit=" + limit;
        }
        
        try {
            String responseBody = performGet(url);
            return parseGeocodingResponse(responseBody);
        } catch (IOException e) {
            if (e.getMessage().contains("HTTP 400") && (e.getMessage().contains("wrong latitude") || e.getMessage().contains("wrong longitude"))) {
                List<LocationData> errorResult = new ArrayList<>();
                errorResult.add(new LocationData("Error: Invalid coordinates", lat, lon, 
                              "Latitude must be between -90 and 90, longitude between -180 and 180", null, null));
                return errorResult;
            }
            throw e;
        }
    }
    
    /**
     * Gets location data by coordinates using reverse geocoding with default limit.
     * This is a convenience method that returns up to 5 location results for the specified coordinates.
     * 
     * @param lat Latitude coordinate of the location (between -90 and 90)
     * @param lon Longitude coordinate of the location (between -180 and 180)
     * @return List of LocationData objects containing locations near the specified coordinates (up to 5 results)
     * @throws IOException if network request fails
     * @throws InterruptedException if the request is interrupted
     * @throws IllegalStateException if OPENWEATHER_API_KEY is not found in .env file
     */
    public List<LocationData> getLocationsByCoordinates(double lat, double lon) throws IOException, InterruptedException {
        return getLocationsByCoordinates(lat, lon, 5);
    }
}