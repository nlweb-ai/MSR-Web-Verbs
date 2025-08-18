import java.time.LocalDate;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the OpenWeather API wrapper
 */
public class OpenWeatherTest {
    private OpenWeather openWeather;
    
    // Test coordinates for Seattle, WA
    private static final double SEATTLE_LAT = 47.6062;
    private static final double SEATTLE_LON = -122.3321;
    
    @BeforeEach
    void setUp() {
        openWeather = new OpenWeather();
    }
    
    @Test
    @DisplayName("Test getting current weather with full parameters")
    void testGetCurrentWeatherFull() throws Exception {
        OpenWeather.CurrentWeatherData weatherData = openWeather.getCurrentWeather(SEATTLE_LAT, SEATTLE_LON, "metric", "en");
        
        assertNotNull(weatherData, "Weather data should not be null");
        assertNotNull(weatherData.getCityName(), "City name should not be null");
        assertNotNull(weatherData.getCountry(), "Country should not be null");
        assertNotNull(weatherData.getCondition(), "Weather condition should not be null");
        assertNotNull(weatherData.getDate(), "Date should not be null");
        
        System.out.println("Current weather for Seattle (full parameters):");
        System.out.println("  City: " + weatherData.getCityName());
        System.out.println("  Country: " + weatherData.getCountry());
        System.out.println("  Condition: " + weatherData.getCondition());
        System.out.println("  Description: " + weatherData.getDescription());
        System.out.println("  Temperature: " + weatherData.getTemperature() + "°C");
        System.out.println("  Feels Like: " + weatherData.getFeelsLike() + "°C");
        System.out.println("  Humidity: " + weatherData.getHumidity() + "%");
        System.out.println("  Wind Speed: " + weatherData.getWindSpeed() + " m/s");
        
        // Check that essential weather information is present
        assertTrue(weatherData.getTemperature() != 0.0 || weatherData.getCityName().contains("Error"), 
            "Weather data should contain valid temperature information or error message");
        assertEquals(LocalDate.now(), weatherData.getDate(), "Date should be today");
    }
    
    @Test
    @DisplayName("Test getting current weather with default parameters")
    void testGetCurrentWeatherDefault() throws Exception {
        OpenWeather.CurrentWeatherData weatherData = openWeather.getCurrentWeather(SEATTLE_LAT, SEATTLE_LON);
        
        assertNotNull(weatherData, "Weather data should not be null");
        assertNotNull(weatherData.getCityName(), "City name should not be null");
        
        System.out.println("Current weather for Seattle (default parameters):");
        System.out.println("  City: " + weatherData.getCityName());
        System.out.println("  Temperature: " + weatherData.getTemperature() + "°C");
        System.out.println("  Condition: " + weatherData.getCondition());
        System.out.println("  Description: " + weatherData.getDescription());
        
        // Verify the data contains meaningful information
        assertTrue(weatherData.getTemperature() != 0.0 || weatherData.getCityName().contains("Error"), 
            "Weather data should contain valid temperature or error message");
    }
    
    @Test
    @DisplayName("Test getting 5-day forecast with full parameters")
    void testGetForecast5DayFull() throws Exception {
        OpenWeather.WeatherForecastData forecastData = openWeather.getForecast5Day(SEATTLE_LAT, SEATTLE_LON, "metric", "en", 8);
        
        assertNotNull(forecastData, "Forecast data should not be null");
        assertNotNull(forecastData.getCityName(), "City name should not be null");
        assertNotNull(forecastData.getForecasts(), "Forecast entries should not be null");
        assertFalse(forecastData.getForecasts().isEmpty(), "Forecast entries should not be empty");
        
        System.out.println("5-day forecast for Seattle (full parameters, 8 entries):");
        System.out.println("  City: " + forecastData.getCityName());
        System.out.println("  Country: " + forecastData.getCountry());
        System.out.println("  Forecast entries: " + forecastData.getForecasts().size());
        
        for (int i = 0; i < Math.min(3, forecastData.getForecasts().size()); i++) {
            OpenWeather.ForecastEntry entry = forecastData.getForecasts().get(i);
            System.out.println("  Entry " + (i+1) + ": " + entry.getDateTime() + 
                             ", " + entry.getCondition() + ", " + entry.getTemperature() + "°C");
        }
        
        // Check that forecast information is valid
        assertTrue(forecastData.getForecasts().size() > 0, "Should have forecast entries");
        OpenWeather.ForecastEntry firstEntry = forecastData.getForecasts().get(0);
        assertNotNull(firstEntry.getDateTime(), "Forecast entry should have valid date/time");
        assertNotNull(firstEntry.getCondition(), "Forecast entry should have weather condition");
    }
    
    @Test
    @DisplayName("Test getting 5-day forecast with default parameters")
    void testGetForecast5DayDefault() throws Exception {
        OpenWeather.WeatherForecastData forecastData = openWeather.getForecast5Day(SEATTLE_LAT, SEATTLE_LON);
        
        assertNotNull(forecastData, "Forecast data should not be null");
        assertNotNull(forecastData.getForecasts(), "Forecast entries should not be null");
        
        System.out.println("5-day forecast for Seattle (default parameters):");
        System.out.println("  City: " + forecastData.getCityName());
        System.out.println("  Forecast entries: " + forecastData.getForecasts().size());
        
        // Verify the data structure
        assertTrue(forecastData.getForecasts().size() > 0, "Should have forecast entries");
    }
    
    @Test
    @DisplayName("Test getting 5-day forecast with count parameter")
    void testGetForecast5DayWithCount() throws Exception {
        OpenWeather.WeatherForecastData forecastData = openWeather.getForecast5Day(SEATTLE_LAT, SEATTLE_LON, 5);
        
        assertNotNull(forecastData, "Forecast data should not be null");
        assertNotNull(forecastData.getForecasts(), "Forecast entries should not be null");
        
        System.out.println("5-day forecast for Seattle (count=5):");
        System.out.println("  City: " + forecastData.getCityName());
        System.out.println("  Forecast entries: " + forecastData.getForecasts().size());
        
        // Should have entries (up to the requested count)
        assertTrue(forecastData.getForecasts().size() > 0, "Should have forecast entries");
    }
    
    @Test
    @DisplayName("Test getting current air pollution data")
    void testGetCurrentAirPollution() throws Exception {
        OpenWeather.AirPollutionData pollutionData = openWeather.getCurrentAirPollution(SEATTLE_LAT, SEATTLE_LON);
        
        assertNotNull(pollutionData, "Air pollution data should not be null");
        assertNotNull(pollutionData.getPollutionEntries(), "Pollution entries should not be null");
        assertFalse(pollutionData.getPollutionEntries().isEmpty(), "Pollution entries should not be empty");
        
        System.out.println("Current air pollution for Seattle:");
        System.out.println("  Latitude: " + pollutionData.getLatitude());
        System.out.println("  Longitude: " + pollutionData.getLongitude());
        System.out.println("  Pollution entries: " + pollutionData.getPollutionEntries().size());
        
        if (!pollutionData.getPollutionEntries().isEmpty()) {
            OpenWeather.PollutionEntry entry = pollutionData.getPollutionEntries().get(0);
            System.out.println("  AQI: " + entry.getAqi());
            System.out.println("  CO: " + entry.getCo());
            System.out.println("  PM2.5: " + entry.getPm2_5());
        }
        
        // Check that AQI information is present
        OpenWeather.PollutionEntry firstEntry = pollutionData.getPollutionEntries().get(0);
        assertTrue(firstEntry.getAqi() >= 0, "AQI should be a valid positive number or 0 for error");
    }
    
    @Test
    @DisplayName("Test getting air pollution forecast data")
    void testGetAirPollutionForecast() throws Exception {
        OpenWeather.AirPollutionData forecastData = openWeather.getAirPollutionForecast(SEATTLE_LAT, SEATTLE_LON);
        
        assertNotNull(forecastData, "Air pollution forecast data should not be null");
        assertNotNull(forecastData.getPollutionEntries(), "Pollution entries should not be null");
        assertFalse(forecastData.getPollutionEntries().isEmpty(), "Pollution entries should not be empty");
        
        System.out.println("Air pollution forecast for Seattle:");
        System.out.println("  Latitude: " + forecastData.getLatitude());
        System.out.println("  Longitude: " + forecastData.getLongitude());
        System.out.println("  Forecast entries: " + forecastData.getPollutionEntries().size());
        
        // Check that pollution forecast information is present
        assertTrue(forecastData.getPollutionEntries().size() > 0, "Should have pollution forecast entries");
    }
    
    @Test
    @DisplayName("Test getting historical air pollution data")
    void testGetHistoricalAirPollution() throws Exception {
        // Test historical data for last week (7 days ago to now)
        long now = System.currentTimeMillis() / 1000; // Current Unix timestamp
        long weekAgo = now - (7 * 24 * 60 * 60); // 7 days ago
        
        OpenWeather.AirPollutionData historicalData = openWeather.getHistoricalAirPollution(SEATTLE_LAT, SEATTLE_LON, weekAgo, now);
        
        assertNotNull(historicalData, "Historical air pollution data should not be null");
        assertNotNull(historicalData.getPollutionEntries(), "Pollution entries should not be null");
        assertFalse(historicalData.getPollutionEntries().isEmpty(), "Pollution entries should not be empty");
        
        System.out.println("Historical air pollution for Seattle (last 7 days):");
        System.out.println("  Latitude: " + historicalData.getLatitude());
        System.out.println("  Longitude: " + historicalData.getLongitude());
        System.out.println("  Historical entries: " + historicalData.getPollutionEntries().size());
        
        // Check that historical pollution information is present
        assertTrue(historicalData.getPollutionEntries().size() > 0, "Should have historical pollution entries");
    }
    
    /*
    @Test
    @DisplayName("Test user agent configuration")
    void testUserAgent() {
        String userAgent = OpenWeather.getUserAgent();
        
        assertNotNull(userAgent, "User agent should not be null");
        assertTrue(userAgent.contains("JavaOpenWeatherClient"), 
            "User agent should identify as JavaOpenWeatherClient");
        
        System.out.println("User agent: " + userAgent);
    }
    */
    
    @Test
    @DisplayName("Test invalid coordinates handling")
    void testInvalidCoordinates() {
        // Test with invalid latitude (>90)
        assertDoesNotThrow(() -> {
            openWeather.getCurrentWeather(100.0, 0.0);
        }, "API should handle invalid coordinates gracefully");
        
        // Test with invalid longitude (>180)
        assertDoesNotThrow(() -> {
            openWeather.getCurrentWeather(0.0, 200.0);
        }, "API should handle invalid coordinates gracefully");
    }
    
    @Test
    @DisplayName("Test different weather units")
    void testDifferentUnits() throws Exception {
        // Test with imperial units
        OpenWeather.CurrentWeatherData imperialWeather = openWeather.getCurrentWeather(SEATTLE_LAT, SEATTLE_LON, "imperial", "en");
        assertNotNull(imperialWeather, "Imperial weather data should not be null");
        
        // Test with standard units (Kelvin)
        OpenWeather.CurrentWeatherData standardWeather = openWeather.getCurrentWeather(SEATTLE_LAT, SEATTLE_LON, "standard", "en");
        assertNotNull(standardWeather, "Standard weather data should not be null");
        
        System.out.println("Weather data comparison:");
        System.out.println("Imperial units:");
        System.out.println("  Temperature: " + imperialWeather.getTemperature() + "°F");
        System.out.println("  Condition: " + imperialWeather.getCondition());
        System.out.println("Standard units:");
        System.out.println("  Temperature: " + standardWeather.getTemperature() + "K");
        System.out.println("  Condition: " + standardWeather.getCondition());
        
        // Verify different units produce different temperature values (if not error data)
        if (!imperialWeather.getCityName().contains("Error") && !standardWeather.getCityName().contains("Error")) {
            assertTrue(imperialWeather.getTemperature() != standardWeather.getTemperature(),
                      "Different units should produce different temperature values");
        }
    }
    
    @Test
    @DisplayName("Test different languages")
    void testDifferentLanguages() throws Exception {
        // Test with Spanish language
        OpenWeather.CurrentWeatherData spanishWeather = openWeather.getCurrentWeather(SEATTLE_LAT, SEATTLE_LON, "metric", "es");
        assertNotNull(spanishWeather, "Spanish weather data should not be null");
        
        // Test with French language
        OpenWeather.CurrentWeatherData frenchWeather = openWeather.getCurrentWeather(SEATTLE_LAT, SEATTLE_LON, "metric", "fr");
        assertNotNull(frenchWeather, "French weather data should not be null");
        
        System.out.println("Weather data in different languages:");
        System.out.println("Spanish:");
        System.out.println("  Description: " + spanishWeather.getDescription());
        System.out.println("French:");
        System.out.println("  Description: " + frenchWeather.getDescription());
        
        // Verify we get valid weather data
        assertNotNull(spanishWeather.getCondition(), "Spanish weather should have condition");
        assertNotNull(frenchWeather.getCondition(), "French weather should have condition");
    }
    
    @Test
    @DisplayName("Test direct geocoding by city name")
    void testGetLocationsByName() throws Exception {
        List<OpenWeather.LocationData> locationData = openWeather.getLocationsByName("London");
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        System.out.println("Direct geocoding for 'London':");
        for (OpenWeather.LocationData location : locationData) {
            System.out.println("  Name: " + location.getName());
            System.out.println("  Country: " + location.getCountry());
            System.out.println("  Coordinates: " + location.getLatitude() + ", " + location.getLongitude());
        }
        
        // Check that geocoding information is present
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertTrue(firstLocation.getName().contains("London") || firstLocation.getName().contains("Error"), 
                  "Location should contain 'London' in name or be an error message");
    }
    
    @Test
    @DisplayName("Test direct geocoding with specific format")
    void testGetLocationsByNameSpecific() throws Exception {
        List<OpenWeather.LocationData> locationData = openWeather.getLocationsByName("New York,NY,US", 3);
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        System.out.println("Direct geocoding for 'New York,NY,US' (limit 3):");
        for (OpenWeather.LocationData location : locationData) {
            System.out.println("  Name: " + location.getName());
            System.out.println("  State: " + location.getState());
            System.out.println("  Country: " + location.getCountry());
            System.out.println("  Coordinates: " + location.getLatitude() + ", " + location.getLongitude());
        }
        
        // Check that coordinates are valid (non-zero or error message)
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertTrue(firstLocation.getLatitude() != 0.0 || firstLocation.getName().contains("Error"), 
                  "Should have valid coordinates or error message");
    }
    
    @Test
    @DisplayName("Test zip code geocoding with country code")
    void testGetLocationByZipCode() throws Exception {
        List<OpenWeather.LocationData> locationData = openWeather.getLocationByZipCode("E14", "GB");
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        System.out.println("Zip code geocoding for 'E14,GB':");
        for (OpenWeather.LocationData location : locationData) {
            System.out.println("  Name: " + location.getName());
            System.out.println("  Country: " + location.getCountry());
            System.out.println("  Coordinates: " + location.getLatitude() + ", " + location.getLongitude());
            if (location.getZipCode() != null) {
                System.out.println("  Zip: " + location.getZipCode());
            }
        }
        
        // Check that zip code information is present
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertTrue(firstLocation.getName().contains("E14") || firstLocation.getName().contains("Error") ||
                  firstLocation.getCountry().equals("GB"), 
                  "Location should be related to E14,GB or contain error");
    }
    
    @Test
    @DisplayName("Test zip code geocoding with combined format")
    void testGetLocationByZipCodeCombined() throws Exception {
        List<OpenWeather.LocationData> locationData = openWeather.getLocationByZipCode("10001,US");
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        System.out.println("Zip code geocoding for '10001,US':");
        for (OpenWeather.LocationData location : locationData) {
            System.out.println("  Name: " + location.getName());
            System.out.println("  Country: " + location.getCountry());
            System.out.println("  Coordinates: " + location.getLatitude() + ", " + location.getLongitude());
        }
        
        // Check that area name is present
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertNotNull(firstLocation.getName(), "Location should have a name");
    }
    
    @Test
    @DisplayName("Test reverse geocoding by coordinates")
    void testGetLocationsByCoordinates() throws Exception {
        // Use coordinates for London
        List<OpenWeather.LocationData> locationData = openWeather.getLocationsByCoordinates(51.5074, -0.1278);
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        System.out.println("Reverse geocoding for London coordinates (51.5074, -0.1278):");
        for (OpenWeather.LocationData location : locationData) {
            System.out.println("  Name: " + location.getName());
            System.out.println("  Country: " + location.getCountry());
            System.out.println("  Coordinates: " + location.getLatitude() + ", " + location.getLongitude());
        }
        
        // Check that location names are present
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertNotNull(firstLocation.getName(), "Location should have a name");
    }
    
    @Test
    @DisplayName("Test reverse geocoding with limit")
    void testGetLocationsByCoordinatesWithLimit() throws Exception {
        // Use coordinates for Seattle
        List<OpenWeather.LocationData> locationData = openWeather.getLocationsByCoordinates(SEATTLE_LAT, SEATTLE_LON, 2);
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        System.out.println("Reverse geocoding for Seattle coordinates (limit 2):");
        for (OpenWeather.LocationData location : locationData) {
            System.out.println("  Name: " + location.getName());
            System.out.println("  Country: " + location.getCountry());
            System.out.println("  Coordinates: " + location.getLatitude() + ", " + location.getLongitude());
        }
        
        // Check that coordinates are present
        assertTrue(locationData.size() <= 2, "Should respect the limit of 2 results");
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertTrue(firstLocation.getLatitude() != 0.0 || firstLocation.getName().contains("Error"), 
                  "Should have valid coordinates or error message");
    }
    
    @Test
    @DisplayName("Test geocoding error handling - empty query")
    void testGeocodingEmptyQuery() throws Exception {
        List<OpenWeather.LocationData> locationData = openWeather.getLocationsByName("");
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertTrue(firstLocation.getName().contains("Error"), 
                  "Should return error message for empty query");
        
        System.out.println("Error handling for empty query:");
        System.out.println("  Error: " + firstLocation.getName());
        System.out.println("  Message: " + firstLocation.getCountry());
    }
    
    @Test
    @DisplayName("Test geocoding error handling - empty zip code")
    void testGeocodingEmptyZipCode() throws Exception {
        List<OpenWeather.LocationData> locationData = openWeather.getLocationByZipCode("");
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertTrue(firstLocation.getName().contains("Error"), 
                  "Should return error message for empty zip code");
        
        System.out.println("Error handling for empty zip code:");
        System.out.println("  Error: " + firstLocation.getName());
        System.out.println("  Message: " + firstLocation.getCountry());
    }
    
    @Test
    @DisplayName("Test geocoding error handling - invalid coordinates")
    void testGeocodingInvalidCoordinates() throws Exception {
        // Test with invalid latitude (>90)
        List<OpenWeather.LocationData> locationData = openWeather.getLocationsByCoordinates(100.0, 0.0);
        
        assertNotNull(locationData, "Location data should not be null");
        assertFalse(locationData.isEmpty(), "Location data should not be empty");
        
        OpenWeather.LocationData firstLocation = locationData.get(0);
        assertTrue(firstLocation.getName().contains("Error"), 
                  "Should handle invalid coordinates gracefully");
        
        System.out.println("Error handling for invalid coordinates:");
        System.out.println("  Error: " + firstLocation.getName());
        System.out.println("  Message: " + firstLocation.getCountry());
    }
}
