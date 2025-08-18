import java.util.List;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the NASA API wrapper
 */
public class NasaTest {
    private Nasa nasa;

    @BeforeEach
    void setUp() {
        nasa = new Nasa();
    }

    @Test
    @DisplayName("Test getting Astronomy Picture of the Day")
    void testGetApod() throws Exception {
        Nasa.ApodResult apod = nasa.getApod("2024-01-01", true);
        assertNotNull(apod, "APOD result should not be null");
        assertNotNull(apod.title, "APOD title should not be null");
        assertNotNull(apod.url, "APOD url should not be null");
        assertNotNull(apod.explanation, "APOD explanation should not be null");
        System.out.println("  Explanation: " + apod.explanation);
        System.out.println("  Date: " + apod.date);
    }

    @Test
    @DisplayName("Test getting APOD without specific date")
    void testGetApodToday() throws Exception {
        Nasa.ApodResult apod = nasa.getApod(null, false);
        assertNotNull(apod, "APOD result should not be null");
        System.out.println("Today's APOD Data:");
        System.out.println("  Title: " + apod.title);
        System.out.println("  URL: " + apod.url);
        System.out.println("  Explanation: " + apod.explanation);
        System.out.println("  Date: " + apod.date);
    }

    @Test
    @DisplayName("Test getting Near Earth Objects feed")
    void testGetNeoFeed() throws Exception {
        List<Nasa.NeoResult> neoData = nasa.getNeoFeed("2024-01-01", "2024-01-02");
        assertNotNull(neoData, "NEO feed data should not be null");
        System.out.println("NEO Feed Data (2024-01-01 to 2024-01-02):");
        if (neoData.isEmpty()) {
            System.out.println("  No NEOs found for this date range");
        } else {
            for (int i = 0; i < Math.min(5, neoData.size()); i++) {
                Nasa.NeoResult neo = neoData.get(i);
                System.out.println("  " + (i + 1) + ". Name: " + neo.name + ", ID: " + neo.id);
            }
        }
    }

    @Test
    @DisplayName("Test NEO feed with single date")
    void testGetNeoFeedSingleDate() throws Exception {
        List<Nasa.NeoResult> neoData = nasa.getNeoFeed("2024-01-01", null);
        assertNotNull(neoData, "NEO feed data should not be null");
        System.out.println("NEO Feed Data (2024-01-01 only):");
        if (neoData.isEmpty()) {
            System.out.println("  No NEOs found for this date");
        } else {
            for (int i = 0; i < Math.min(3, neoData.size()); i++) {
                Nasa.NeoResult neo = neoData.get(i);
                System.out.println("  " + (i + 1) + ". Name: " + neo.name + ", ID: " + neo.id);
            }
        }
    }

    @Test
    @DisplayName("Test NEO lookup by specific asteroid ID")
    void testGetNeoLookup() throws Exception {
        Nasa.NeoResult neo = nasa.getNeoLookup(3542519);
        assertNotNull(neo, "NEO lookup result should not be null");
        assertNotNull(neo.name, "NEO name should not be null");
        assertNotNull(neo.id, "NEO id should not be null");
        System.out.println("NEO Lookup Data for asteroid 3542519:");
        System.out.println("  Name: " + neo.name);
        System.out.println("  ID: " + neo.id);
    }

    @Test
    @DisplayName("Test NEO browse overall dataset")
    void testGetNeoBrowse() throws Exception {
        List<Nasa.NeoResult> neoData = nasa.getNeoBrowse();
        assertNotNull(neoData, "NEO browse data should not be null");
        assertFalse(neoData.isEmpty(), "Browse should return NEO data");
        System.out.println("NEO Browse Data (first 5 entries):");
        for (int i = 0; i < Math.min(5, neoData.size()); i++) {
            Nasa.NeoResult neo = neoData.get(i);
            System.out.println("  " + (i + 1) + ". Name: " + neo.name + ", ID: " + neo.id);
        }
    }

    @Test
    @DisplayName("Test user agent string")
    void testGetUserAgent() {
        String userAgent = Nasa.getUserAgent();
        assertNotNull(userAgent, "User agent should not be null");
        assertTrue(userAgent.contains("javify"), "User agent should contain app name");
        assertTrue(userAgent.contains("sirius0see+api@gmail.com"), "User agent should contain email");
        System.out.println("NASA User Agent: " + userAgent);
    }

    @Test
    @DisplayName("Test invalid date format handling")
    void testInvalidDateFormat() {
        // This test checks that the API properly throws exceptions for invalid dates
        // The NASA API returns HTTP 400 for invalid date formats, which is correct behavior
        assertThrows(Exception.class, () -> {
            nasa.getApod("invalid-date", false);
        }, "Should throw exception for invalid date formats");
    }
}
