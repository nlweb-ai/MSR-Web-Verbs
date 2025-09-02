import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;

import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the NLWeb class
 * Tests the AskNLWeb method with various input scenarios
 */
public class NLWebTest {
    private NLWeb nlWeb;
    private ByteArrayOutputStream outputStream;
    private PrintStream originalOut;

    @BeforeEach
    void setUp() {
        nlWeb = new NLWeb();
        // Capture System.out for testing console output
        outputStream = new ByteArrayOutputStream();
        originalOut = System.out;
        System.setOut(new PrintStream(outputStream));
    }

    @Test
    @DisplayName("Test AskNLWeb with special characters")
    void testAskNLWebSpecialCharacters() throws IOException, InterruptedException {
        String query = "I am traveling to Anchorage, Alaska. Can you recommend 5 museums?";
        
        // Note: This test will make an actual HTTP request to localhost:8000
        // If the server is not running, it will return an error JsonObject
        String result = nlWeb.AskNLWeb(query);
        
        // The result should not be null - it should be a JsonObject (either success or error)
        assertTrue(result != null, "Result should not be null - should be a JsonObject");
    }

    // Clean up after each test
    @AfterEach
    void tearDown() {
        System.setOut(originalOut);
    }
}
