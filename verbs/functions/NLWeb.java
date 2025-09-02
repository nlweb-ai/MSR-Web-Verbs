import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.JsonSyntaxException;

public class NLWeb {
    
    /**
     * Sends a natural language query to the NLWeb API and retrieves recommendations.
     *
     * @param queryString The natural language query to send to the API.
     *                   Example: "I am traveling to Anchorage, Alaska. Can you recommend 5 museums?"
     * @return A JSON string containing the recommended items in the format:
     *         {"item_0":"Museum Name 1","item_1":"Museum Name 2",...}
     *         Returns null if all retry attempts fail or no valid ensemble_result is found.
     */
    public String AskNLWeb(String queryString) throws IOException, InterruptedException {
        // Use URLEncoder and replace + with %20 for proper URL encoding
        String encodedQuery = URLEncoder.encode(queryString, "UTF-8").replace("+", "%20");
        System.out.println("Encoded Query: " + encodedQuery);

        int count = 0;
        while (count < 3) {
            // Send the HTTP request
            JsonObject response = sendAskRequest(encodedQuery);
            if (response == null || !response.get("status").getAsString().equals("200")) {
                count ++;
                continue;
            }
            String respText = response.get("response").getAsString();
            String ensembleResultText = null;
            for (String line : respText.split("\n")) {
                if (line.contains("ensemble_result")) {
                    ensembleResultText = line;
                }
            }
            if (ensembleResultText == null) {
                count ++;
                continue;
            }
            // Remove "data: " prefix if it exists
            if (ensembleResultText.startsWith("data: ")) {
                ensembleResultText = ensembleResultText.substring("data: ".length());
            }
            // If we found a valid ensemble_result, we can return it
            JsonObject ensembleResultJSON = JsonParser.parseString(ensembleResultText).getAsJsonObject();
            JsonArray ensembleResultItems = ensembleResultJSON.getAsJsonObject("result").getAsJsonObject("recommendations").getAsJsonArray("items");
            JsonObject outputJson = new JsonObject();
            for (int i=0;i<ensembleResultItems.size();i++) {
                String itemName = ensembleResultItems.get(i).getAsJsonObject().get("name").getAsString();
                outputJson.addProperty("item_" + i, itemName);
            }
            return outputJson.toString();
        }
        return null; // Return null if all attempts fail
    }
    
    private JsonObject sendAskRequest(String encodedQuery) throws IOException, InterruptedException {
        // Build the URL with the encoded query
        String url = "http://localhost:8000/ask?query=" + encodedQuery + "&streaming=true";
        
        // Create HTTP client
        HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(30))
            .build();
        
        // Create HTTP request
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .header("Accept", "text/event-stream")
            .GET()
            .timeout(Duration.ofSeconds(60))
            .build();
        
        try {
            // Send the request and get response
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            System.out.println("Response Status: " + response.statusCode());
            System.out.println("Response Body: " + response.body());
            
            // Parse the response body as JSON if it's valid JSON
            if (response.statusCode() == 200 && response.body() != null && !response.body().trim().isEmpty()) {
                try {
                    // Try to parse as JSON
                    return JsonParser.parseString(response.body()).getAsJsonObject();
                } catch (JsonSyntaxException | IllegalStateException e) {
                    // If parsing fails, create a JSON object with the raw response
                    JsonObject result = new JsonObject();
                    result.addProperty("response", response.body());
                    result.addProperty("status", response.statusCode());
                    return result;
                }
            } else {
                // Create error response
                JsonObject errorResult = new JsonObject();
                errorResult.addProperty("error", "Request failed");
                errorResult.addProperty("status", response.statusCode());
                errorResult.addProperty("body", response.body());
                return errorResult;
            }
            
        } catch (IOException | InterruptedException e) {
            // Handle exceptions
            JsonObject errorResult = new JsonObject();
            errorResult.addProperty("error", e.getMessage());
            errorResult.addProperty("exception", e.getClass().getSimpleName());
            throw e; // Re-throw the exception as specified in method signature
        }
    }
}
